import boto3
import os

from response import build_response

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

        return build_response(
            404,
            {
                "message": "Ticket not found"
            }
        )

    return build_response(
        200,
        item
    )