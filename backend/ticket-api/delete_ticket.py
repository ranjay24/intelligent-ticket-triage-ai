import boto3
import os
import json

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

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Ticket deleted successfully"
        })
    }