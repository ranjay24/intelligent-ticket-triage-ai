import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)

def get_ticket(ticket_id):

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

    return {
        "statusCode": 200,
        "body": json.dumps(item)
    }