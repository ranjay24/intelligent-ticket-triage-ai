import boto3
import os
from datetime import datetime

from response import build_response
from email_sender import send_email
from observability import (
    log_info,
    publish_metric
)

from tools.password_tool import reset_password
from tools.refund_tool import issue_refund
from tools.order_status_tool import get_order_status

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def approve_ticket(
    ticket_id,
    approved_by="Admin",
    review_comment=None,
    edited_reply=None
):

    response = table.get_item(
        Key={
            "ticketId": ticket_id
        }
    )

    item = response.get("Item")

    # ------------------------
    # Validate BEFORE mutating the item.
    # (The old code edited item["draftReply"] before this check,
    #  which crashed with a 500 when the ticket did not exist.)
    # ------------------------

    if not item:
        return build_response(
            404,
            {
                "message": "Ticket not found"
            }
        )

    if item.get("status") != "PENDING_REVIEW":
        return build_response(
            400,
            {
                "message": "Ticket is not pending review"
            }
        )

    # Admin may edit the AI draft before approval
    if edited_reply:
        item["draftReply"] = edited_reply

    now = datetime.utcnow().isoformat()
    history = item.get("history", [])
    result = None

    try:

        # ------------------------
        # Execute the tool — only now, after human approval
        # ------------------------

        if item.get("actionType") == "RESET_PASSWORD":
            result = reset_password(item["customerId"])

        elif item.get("actionType") == "ISSUE_REFUND":
            result = issue_refund(item["entityId"])

        elif item.get("actionType") == "GET_ORDER_STATUS":
            result = get_order_status(item["entityId"])

        # ------------------------
        # Tool result
        # ------------------------

        if result:

            item["toolExecuted"] = True
            item["toolResult"] = result
            item["actionStatus"] = (
                "COMPLETED" if result.get("success") else "FAILED"
            )

            if item.get("actionType") == "RESET_PASSWORD":
                publish_metric("PasswordReset")
            elif item.get("actionType") == "ISSUE_REFUND":
                publish_metric("RefundIssued")
            elif item.get("actionType") == "GET_ORDER_STATUS":
                publish_metric("OrderStatusChecked")

    except Exception as e:

        print("TOOL EXECUTION FAILED")
        print(str(e))

        item["toolExecuted"] = False
        item["actionStatus"] = "FAILED"
        item["toolResult"] = {
            "success": False,
            "message": str(e)
        }

    # ------------------------
    # Approval metadata + lifecycle
    # ------------------------

    item["status"] = "RESOLVED"
    item["requiresReview"] = False
    item["approvedAt"] = now
    item["approvedBy"] = approved_by
    item["resolvedAt"] = now
    item["updatedAt"] = now
    item["lastReviewedBy"] = approved_by
    item["lastReviewedAt"] = now

    # Don't wipe an existing saved note if approve is called without one
    if review_comment is not None:
        item["reviewComment"] = review_comment

    # ------------------------
    # Timeline / History
    #   APPROVED -> (TOOL_EXECUTED) -> (EMAIL_SENT) -> RESOLVED
    # ------------------------

    history.append({
        "event": "APPROVED",
        "time": now,
        "performedBy": approved_by,
        "comment": review_comment,
        "draftEdited": edited_reply is not None
    })

    if result:
        history.append({
            "event": "TOOL_EXECUTED",
            "time": now,
            "tool": item.get("actionType"),
            "status": item.get("actionStatus"),
            "success": result.get("success", False)
        })

    # ------------------------
    # Email customer
    # ------------------------

    if item.get("customerEmail"):

        try:
            send_email(
                item["customerEmail"],
                item["ticketId"],
                item["draftReply"]
            )

            item["emailSent"] = True
            item["emailSentAt"] = now
            publish_metric("EmailSent")
            history.append({"event": "EMAIL_SENT", "time": now})

            log_info(
                "EMAIL_SENT",
                ticketId=ticket_id,
                customer=item.get("customerEmail")
            )

        except Exception as e:
            publish_metric("EmailFailed")
            log_info(
                "EMAIL_FAILED",
                ticketId=ticket_id,
                customer=item.get("customerEmail"),
                error=str(e)
            )

            item["emailSent"] = False
            item["emailError"] = str(e)

    # Final lifecycle event
    history.append({"event": "RESOLVED", "time": now})
    item["history"] = history

    # ------------------------
    # Save
    # ------------------------

    table.put_item(Item=item)

    publish_metric("TicketResolved")

    log_info(
        "TICKET_RESOLVED",
        ticketId=ticket_id,
        approvedBy=approved_by,
        actionType=item.get("actionType"),
        toolExecuted=item.get("toolExecuted"),
        emailSent=item.get("emailSent")
    )

    return build_response(
        200,
        {
            "message": "Ticket resolved successfully",
            "ticketId": ticket_id,
            "approvedBy": approved_by,
            "approvedAt": now,
            "toolExecuted": item.get("toolExecuted", False),
            "actionStatus": item.get("actionStatus"),
            "emailSent": item.get("emailSent", False)
        }
    )