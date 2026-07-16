import os
import uuid
import boto3

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["CUSTOMERS_TABLE"]
)


def get_or_create_customer(email):

    response = table.query(
        IndexName="email-index",
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])

    if items:
        return items[0]

    customer = {
        "customerId": f"C{str(uuid.uuid4())[:8]}",
        "email": email,
        "accountStatus": "ACTIVE",
        "passwordResetRequired": False
    }

    table.put_item(
        Item=customer
    )

    return customer