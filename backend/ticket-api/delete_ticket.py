import boto3
import os

from response import build_response

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def delete_ticket(ticket_id):

    table.delete_item(
        Key={
            "ticketId": ticket_id
        }
    )

    return build_response(
        200,
        {
            "message": "Ticket deleted successfully"
        }
    )