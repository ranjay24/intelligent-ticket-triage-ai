import boto3
import os
import json
from datetime import datetime

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def approve_ticket(ticket_id):

    response = table.get_item(
        Key={
            "ticketId": ticket_id
        }
    )

    item = response.get("Item")

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Ticket not found"
            })
        }

    if item.get("status") != "PENDING_REVIEW":
        return {
        "statusCode": 400,
        "body": json.dumps({
            "message": "Ticket is not pending review"
        })
        }

    item["status"] = "APPROVED"
    item["requiresReview"] = False
    item["updatedAt"] = datetime.utcnow().isoformat()

    table.put_item(
        Item=item
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Ticket approved"
        })
    }