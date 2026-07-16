import boto3
import os
from datetime import datetime

from botocore.exceptions import ClientError

from response import build_response

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

EDITABLE_FIELDS = [
    "status",
    "draftReply",
    "reviewComment",
]


def update_ticket(ticket_id, body):

    update_expression = []
    expression_values = {}
    expression_names = {}

    for field in EDITABLE_FIELDS:

        if field in body:

            placeholder = "#" + field
            value = ":" + field

            update_expression.append(f"{placeholder} = {value}")
            expression_names[placeholder] = field
            expression_values[value] = body[field]

    # Nothing valid to update -> clean 400 instead of a DynamoDB
    # ValidationException (empty ExpressionAttributeNames).
    if not expression_names:
        return build_response(
            400,
            {"message": "No editable fields provided"}
        )

    # Always bump the timestamp
    update_expression.append("updatedAt = :updatedAt")
    expression_values[":updatedAt"] = datetime.utcnow().isoformat()

    try:

        response = table.update_item(
            Key={"ticketId": ticket_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            # Fail instead of creating a phantom ticket via upsert
            ConditionExpression="attribute_exists(ticketId)",
            ReturnValues="ALL_NEW",
        )

    except ClientError as e:

        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return build_response(
                404,
                {"message": "Ticket not found"}
            )
        raise

    return build_response(
        200,
        response["Attributes"]
    )