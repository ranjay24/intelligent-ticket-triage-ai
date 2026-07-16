from datetime import datetime
import json
import boto3
import os
import traceback
from decimal import Decimal

from classifier import classify_ticket
from pii_redactor import redact
from reply_generator import generate_reply
from email_sender import send_email
from tools.order_status_tool import get_order_status
from observability import (
    log_info,
    log_error,
    publish_metric
)

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)

# Attributes the processor must NOT write, so it can never clobber data
# owned by another writer. `attachments` is maintained by the
# attachment-processor; the processor updates everything else.
NOT_OWNED = ("ticketId", "attachments")


def lambda_handler(event, context):

    log_info(
        "TICKET_PROCESSOR_STARTED",
        recordCount=len(event.get("Records", []))
    )

    # Partial-batch response: report ONLY the messages that failed, so
    # SQS redelivers just those instead of the whole batch (which would
    # reprocess — and re-email — the ones that already succeeded).
    batch_item_failures = []

    for record in event["Records"]:

        message_id = record.get("messageId")

        try:
            ticket = json.loads(record["body"])

            log_info(
                "AI_PROCESSING_STARTED",
                ticketId=ticket["ticketId"],
                subject=ticket["subject"]
            )

            process_ticket(ticket)     # never raises (degrades on AI error)
            save_ticket(ticket)        # hard failure here -> retry this msg
            publish_metric("TicketsProcessed")

            send_customer_email(ticket)  # catches its own errors

            log_info(
                "AI_PROCESSING_COMPLETED",
                ticketId=ticket["ticketId"],
                category=ticket.get("category"),
                priority=ticket.get("priority"),
                confidence=ticket.get("confidence"),
                status=ticket.get("status")
            )

        except Exception as e:

            # Something unrecoverable for THIS message (bad JSON, a
            # DynamoDB write error, etc.). Mark it failed so SQS retries
            # only this message; after maxReceiveCount it lands in the DLQ.
            log_error(
                "RECORD_PROCESSING_FAILED",
                error=e,
                messageId=message_id,
                traceback=traceback.format_exc()
            )
            publish_metric("ProcessingError")

            if message_id:
                batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}


def process_ticket(ticket):
    """Classify, draft, run tools, decide status. Mutates `ticket`.

    AI/tool errors are caught here and degraded to a review ticket, so
    they do NOT fail the SQS message (only genuine infra failures do).
    """

    try:

        # ---- redact PII before anything is sent to the model ----
        # The original ticket text is kept unchanged (stored + shown to
        # agents); only the model ever sees the masked version.
        safe_subject, r1 = redact(ticket["subject"])
        safe_description, r2 = redact(ticket["description"])
        if (r1 + r2) > 0:
            publish_metric("PiiRedactions", value=(r1 + r2))
            log_info("PII_REDACTED", ticketId=ticket["ticketId"],
                     count=(r1 + r2))

        # ---- single triage call (on redacted text) ----
        classification = classify_ticket(
            safe_subject,
            safe_description
        )

        log_info(
            "CLASSIFICATION_COMPLETE",
            ticketId=ticket["ticketId"],
            category=classification.get("category"),
            priority=classification.get("priority"),
            confidence=classification.get("confidence"),
            actionType=classification.get("actionType")
        )

        category = classification.get("category", "General Inquiry")

        if category == "Out Of Scope":

            ticket["category"] = "Out Of Scope"
            ticket["priority"] = "LOW"
            ticket["sentiment"] = "NEUTRAL"
            ticket["language"] = "English"
            ticket["actionType"] = "NONE"
            ticket["actionStatus"] = None
            ticket["entityType"] = "NONE"
            ticket["entityId"] = None
            ticket["confidence"] = Decimal("1.0")
            ticket["requiresReview"] = False
            ticket["reviewReasons"] = []
            ticket["draftReply"] = (
                "Thank you for contacting support. "
                "This request appears to be outside the scope of "
                "our support platform."
            )
            ticket["sources"] = ["out-of-scope.txt"]

        else:

            ticket["category"] = category
            ticket["priority"] = classification.get("priority", "LOW")
            ticket["sentiment"] = classification.get("sentiment", "NEUTRAL")
            ticket["language"] = classification.get("language", "English")
            ticket["confidence"] = Decimal(
                str(classification.get("confidence", 0.5))
            )
            ticket["actionType"] = classification.get("actionType", "NONE")
            ticket["entityType"] = classification.get("entityType", "NONE")
            ticket["entityId"] = classification.get("entityId") or None

            # ---- order status tool ----
            if ticket["actionType"] == "GET_ORDER_STATUS":

                result = get_order_status(ticket["entityId"])

                log_info(
                    "ORDER_STATUS_TOOL_EXECUTED",
                    ticketId=ticket["ticketId"],
                    orderId=ticket["entityId"],
                    success=result.get("success")
                )

                ticket["toolExecuted"] = True
                ticket["toolResult"] = result
                ticket["actionStatus"] = "COMPLETED"

                if result.get("success"):
                    ticket["draftReply"] = (
                        f"Your order {result['orderId']} "
                        f"is currently {result['status']}."
                    )
                else:
                    ticket["draftReply"] = result.get(
                        "message", "Order not found."
                    )

            elif ticket["actionType"] in ["RESET_PASSWORD", "ISSUE_REFUND"]:
                ticket["actionStatus"] = "PENDING"
            else:
                ticket["actionStatus"] = None

            # ---- review gate ----
            requires_review = False
            review_reasons = []

            if ticket["actionType"] in ("RESET_PASSWORD", "ISSUE_REFUND"):
                requires_review = True
                review_reasons.append("DESTRUCTIVE_ACTION")

            if ticket["priority"] == "CRITICAL":
                requires_review = True
                review_reasons.append("CRITICAL_PRIORITY")

            if ticket["confidence"] <= Decimal("0.85"):
                requires_review = True
                review_reasons.append("LOW_CONFIDENCE")

            if (
                ticket["actionType"] == "GET_ORDER_STATUS"
                and ticket.get("actionStatus") == "COMPLETED"
            ):
                if ticket.get("toolResult", {}).get("success"):
                    requires_review = False
                    review_reasons = []
                else:
                    requires_review = True
                    if "ORDER_NOT_FOUND" not in review_reasons:
                        review_reasons.append("ORDER_NOT_FOUND")

            ticket["requiresReview"] = requires_review
            ticket["reviewReasons"] = review_reasons

            if requires_review:
                publish_metric("PendingReview")
                log_info("REVIEW_REQUIRED", ticketId=ticket["ticketId"],
                         confidence=ticket["confidence"], reasons=review_reasons)
            else:
                log_info("AUTO_RESOLVED", ticketId=ticket["ticketId"],
                         confidence=ticket["confidence"])

            # ---- RAG (skip for order status, tool already answered) ----
            if ticket["actionType"] != "GET_ORDER_STATUS":
                try:
                    # Draft on the redacted text too (model never sees PII)
                    rag_ticket = {
                        **ticket,
                        "subject": safe_subject,
                        "description": safe_description,
                    }
                    rag_result = generate_reply(rag_ticket)
                    ticket["draftReply"] = rag_result.get(
                        "reply", "Support team will investigate."
                    )
                    ticket["sources"] = rag_result.get("sources", [])
                except Exception as e:
                    log_info("RAG_FAILED", ticketId=ticket["ticketId"],
                             error=str(e))
                    ticket["draftReply"] = "Support team will investigate."
                    ticket["sources"] = []

    except Exception as e:

        # Degrade to a review ticket; do NOT fail the SQS message.
        log_error(
            "CLASSIFICATION_FAILED",
            error=e,
            ticketId=ticket.get("ticketId"),
            traceback=traceback.format_exc()
        )
        ticket["category"] = "UNKNOWN"
        ticket["priority"] = "LOW"
        ticket["sentiment"] = "NEUTRAL"
        ticket["language"] = "English"
        ticket["actionType"] = "NONE"
        ticket["actionStatus"] = None
        ticket["entityType"] = "NONE"
        ticket["entityId"] = None
        ticket["draftReply"] = "Support team will investigate."
        ticket["sources"] = []
        ticket["confidence"] = Decimal("0.0")
        ticket["requiresReview"] = True
        ticket["reviewReasons"] = ["PROCESSING_ERROR"]

    # ---- status / lifecycle ----
    now = datetime.utcnow().isoformat()

    if ticket.get("category") == "Out Of Scope":
        ticket["status"] = "CLOSED"
        ticket["requiresReview"] = False
        ticket["closedAt"] = now
    elif ticket.get("requiresReview", True):
        ticket["status"] = "PENDING_REVIEW"
    else:
        ticket["status"] = "RESOLVED"
        ticket["resolvedAt"] = now

    ticket["updatedAt"] = now

    # ---- history (Timeline panel) ----
    history = ticket.get("history", [])
    history.append({"event": "AI_CLASSIFIED", "time": now})
    history.append({"event": ticket["status"], "time": now})
    ticket["history"] = history


def save_ticket(ticket):
    """Write the processor's fields via update_item, NEVER touching
    `attachments` (owned by the attachment-processor). This replaces the
    old put_item, which overwrote the whole item and could wipe an
    attachment added between ticket creation and processing.
    """
    fields = {k: v for k, v in ticket.items() if k not in NOT_OWNED}

    names = {}
    values = {}
    assignments = []
    for i, (k, v) in enumerate(fields.items()):
        names[f"#f{i}"] = k
        values[f":v{i}"] = v
        assignments.append(f"#f{i} = :v{i}")

    table.update_item(
        Key={"ticketId": ticket["ticketId"]},
        UpdateExpression="SET " + ", ".join(assignments),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )


def send_customer_email(ticket):
    """Email the customer for auto-resolved / closed tickets. Runs AFTER
    the save, so a save failure never results in an email being sent for
    a ticket that wasn't persisted. Email failures are logged, not raised
    (we don't want a mail hiccup to trigger a full reprocess)."""

    if ticket.get("status") not in ("RESOLVED", "CLOSED"):
        return
    if not ticket.get("customerEmail"):
        return

    now = datetime.utcnow().isoformat()

    try:
        send_email(
            ticket["customerEmail"],
            ticket["ticketId"],
            ticket["draftReply"]
        )
        publish_metric("EmailSent")

        # Record emailSent + timeline event without clobbering attachments
        try:
            table.update_item(
                Key={"ticketId": ticket["ticketId"]},
                UpdateExpression=(
                    "SET emailSent = :t, emailSentAt = :now, "
                    "#h = list_append(if_not_exists(#h, :empty), :ev)"
                ),
                ExpressionAttributeNames={"#h": "history"},
                ExpressionAttributeValues={
                    ":t": True,
                    ":now": now,
                    ":empty": [],
                    ":ev": [{"event": "EMAIL_SENT", "time": now}],
                },
            )
        except Exception as e:
            log_error("EMAIL_FLAG_UPDATE_FAILED", error=e,
                      ticketId=ticket["ticketId"])

    except Exception as e:
        publish_metric("EmailFailed")
        log_error("EMAIL_FAILED", error=e, ticketId=ticket["ticketId"])