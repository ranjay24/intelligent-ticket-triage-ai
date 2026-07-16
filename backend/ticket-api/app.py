import json
import uuid
import traceback
from datetime import datetime
import boto3
import os

from response import build_response

from get_ticket import get_ticket
from list_tickets import list_tickets, list_my_tickets
from update_ticket import update_ticket
from delete_ticket import delete_ticket
from pending_reviews import get_pending_reviews
from approve_ticket import approve_ticket
from reject_ticket import reject_ticket
from analytics import get_analytics
from customer_service import get_or_create_customer
from observability import log_info, log_error, publish_metric

sqs = boto3.client("sqs")

QUEUE_URL = os.environ["QUEUE_URL"]


def _parse_body(event):
    """Safely parse a JSON body. Returns {} when there is no body."""
    raw = event.get("body")
    if not raw:
        return {}
    return json.loads(raw)


def lambda_handler(event, context):

    # Leave this ABOVE the try/except: uncommenting it raises an
    # UNCAUGHT exception, which is what the CloudWatch Errors alarm
    # watches for. (Handled errors below use the ApiError metric.)
    # raise Exception("Testing CloudWatch Alarm")

    log_info(
        "API_REQUEST_RECEIVED",
        httpMethod=event.get("httpMethod"),
        path=event.get("path"),
    )

    try:

        http_method = event.get("httpMethod")
        path = event.get("path", "")

        # =========================
        # GET
        # =========================

        if http_method == "GET":

            if path.endswith("/analytics"):
                return get_analytics()

            if path.endswith("/reviews/pending"):
                return get_pending_reviews()

            if path.endswith("/my-tickets"):

                headers = event.get("headers", {})
                customer_email = headers.get("x-customer-email")

                if not customer_email:
                    return build_response(
                        400,
                        {"message": "x-customer-email header missing"},
                    )

                return list_my_tickets(customer_email)

            path_parameters = event.get("pathParameters")

            if path_parameters and path_parameters.get("ticketId"):
                return get_ticket(path_parameters["ticketId"])

            return list_tickets()

        # =========================
        # PUT
        # =========================

        if http_method == "PUT":

            ticket_id = event["pathParameters"]["ticketId"]
            body = _parse_body(event)

            return update_ticket(ticket_id, body)

        # =========================
        # DELETE
        # =========================

        if http_method == "DELETE":

            ticket_id = event["pathParameters"]["ticketId"]

            return delete_ticket(ticket_id)

        # =========================
        # POST
        # =========================

        if http_method == "POST":

            if path.endswith("/approve"):

                ticket_id = event["pathParameters"]["ticketId"]
                body = _parse_body(event)

                return approve_ticket(
                    ticket_id,
                    approved_by=body.get("approvedBy", "Admin"),
                    review_comment=body.get("reviewComment"),
                    edited_reply=body.get("draftReply"),
                )

            if path.endswith("/reject"):

                ticket_id = event["pathParameters"]["ticketId"]
                body = _parse_body(event)

                return reject_ticket(ticket_id)

            # ---- Create ticket ----

            body = _parse_body(event)

            headers = event.get("headers", {})
            customer_email = headers.get("x-customer-email")

            if not customer_email:
                return build_response(
                    400,
                    {"message": "x-customer-email header missing"},
                )

            # Validate required fields -> clean 400 instead of a 500
            subject = body.get("subject")
            description = body.get("description")

            if not subject or not description:
                return build_response(
                    400,
                    {"message": "subject and description are required"},
                )

            customer = get_or_create_customer(customer_email)

            now = datetime.utcnow().isoformat()

            ticket = {
                "ticketId": str(uuid.uuid4()),
                "customerId": customer["customerId"],
                "customerEmail": customer["email"],
                "subject": subject,
                "description": description,
                "status": "NEW",
                "confidence": None,
                "requiresReview": False,
                "category": None,
                "priority": None,
                "sentiment": None,
                "actionType": None,
                "actionStatus": None,
                "entityType": None,
                "entityId": None,
                "toolExecuted": False,
                "toolResult": None,
                "draftReply": None,
                "attachments": [],
                "createdAt": now,
                "updatedAt": now,
            }

            sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(ticket),
            )

            publish_metric("TicketsCreated")

            log_info(
                "TICKET_CREATED",
                ticketId=ticket["ticketId"],
                customerId=ticket["customerId"],
                customerEmail=ticket["customerEmail"],
                status=ticket["status"],
            )

            return build_response(201, ticket)

        return build_response(
            400,
            {"message": "Unsupported request"},
        )

    except Exception as e:

        # Return a CORS-safe 500 (goes through build_response, so it
        # carries the CORS headers). Without this, an unhandled error
        # produces a raw 500 with no CORS headers, which the browser
        # misreports as a "CORS error" and hides the real cause.
        log_error(
            "API_UNHANDLED_ERROR",
            error=e,
            httpMethod=event.get("httpMethod"),
            path=event.get("path"),
            traceback=traceback.format_exc(),
        )

        publish_metric("ApiError")

        return build_response(
            500,
            {"message": "Internal server error"},
        )