import boto3
import os
import json
from datetime import datetime

from json_encoder import DecimalEncoder

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def update_ticket(ticket_id, body):

    response = table.update_item(
        Key={
            "ticketId": ticket_id
        },
        UpdateExpression="""
            SET #s = :status,
                updatedAt = :updatedAt
        """,
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":status": body["status"],
            ":updatedAt": datetime.utcnow().isoformat()
        },
        ReturnValues="ALL_NEW"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            response["Attributes"],
            cls=DecimalEncoder
        )
    }