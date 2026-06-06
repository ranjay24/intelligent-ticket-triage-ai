import json
import uuid
from datetime import datetime
import boto3
import os
from get_ticket import get_ticket
from list_tickets import list_tickets
from update_ticket import update_ticket
from delete_ticket import delete_ticket

sqs = boto3.client("sqs")

QUEUE_URL = os.environ["QUEUE_URL"]

def lambda_handler(event, context):
    print("EVENT RECEIVED")
    print(json.dumps(event))
    http_method = event["httpMethod"]

    if http_method == "GET":

       path_parameters = event.get("pathParameters")

       if path_parameters and path_parameters.get("ticketId"):
        return get_ticket(
            path_parameters["ticketId"]
        )

       return list_tickets()
    
    if http_method == "PUT":

       ticket_id = event["pathParameters"]["ticketId"]

       body = json.loads(event["body"])

       return update_ticket(
        ticket_id,
        body
    )

    if http_method == "DELETE":

       ticket_id = event["pathParameters"]["ticketId"]

       return delete_ticket(ticket_id)

    body = json.loads(event["body"])

    ticket = {
        "ticketId": str(uuid.uuid4()),
        "customerId": body["customerId"],
        "subject": body["subject"],
        "description": body["description"],

        "status": "NEW",

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