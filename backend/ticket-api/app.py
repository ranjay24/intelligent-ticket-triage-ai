import json
import uuid
from datetime import datetime
import boto3
import os

from get_ticket import get_ticket
from list_tickets import list_tickets
from update_ticket import update_ticket
from delete_ticket import delete_ticket
from pending_reviews import get_pending_reviews
from approve_ticket import approve_ticket
from reject_ticket import reject_ticket
from analytics import get_analytics

sqs = boto3.client("sqs")

QUEUE_URL = os.environ["QUEUE_URL"]


def lambda_handler(event, context):

    print("EVENT RECEIVED")
    print(json.dumps(event))

    http_method = event["httpMethod"]

    # =========================
    # GET
    # =========================
    if http_method == "GET":

        path = event["path"]

        if path.endswith("/analytics"):
            print("ANALYTICS API HIT")
            return get_analytics()

        if path.endswith("/reviews/pending"):
            print("PENDING REVIEW API HIT")
            return get_pending_reviews()

        path_parameters = event.get("pathParameters")

        if (
            path_parameters and
            path_parameters.get("ticketId")
        ):
            return get_ticket(
                path_parameters["ticketId"]
            )

        return list_tickets()

    # =========================
    # PUT
    # =========================
    if http_method == "PUT":

        ticket_id = event["pathParameters"]["ticketId"]

        body = json.loads(event["body"])

        return update_ticket(
            ticket_id,
            body
        )

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

        path = event["path"]

        if path.endswith("/approve"):

            ticket_id = event["pathParameters"]["ticketId"]

            return approve_ticket(ticket_id)

        if path.endswith("/reject"):

            ticket_id = event["pathParameters"]["ticketId"]

            return reject_ticket(ticket_id)

        # =========================
        # CREATE TICKET
        # =========================

        body = json.loads(event["body"])

        ticket = {
            "ticketId": str(uuid.uuid4()),
            "customerId": body["customerId"],
            "customerEmail": body.get("customerEmail"),
            "subject": body["subject"],
            "description": body["description"],
            "status": "NEW",
            "confidence": None,
            "requiresReview": False,
            "category": None,
            "priority": None,
            "sentiment": None,
            "draftReply": None,
            "attachments": [],
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(ticket)
        )

        return {
            "statusCode": 201,
            "body": json.dumps(ticket)
        }

    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": "Unsupported request"
        })
    }