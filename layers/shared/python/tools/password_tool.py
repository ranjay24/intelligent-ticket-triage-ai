import boto3
import os

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["CUSTOMERS_TABLE"]
)


def reset_password(customer_id):

    if not customer_id:
        return {
            "success": False,
            "message": "No customer id provided"
        }

    response = table.get_item(
        Key={
            "customerId": customer_id
        }
    )

    customer = response.get("Item")

    if not customer:
        return {
            "success": False,
            "message": "Customer not found"
        }

    table.update_item(
        Key={
            "customerId": customer_id
        },
        UpdateExpression="SET passwordResetRequired = :value",
        ExpressionAttributeValues={
            ":value": True
        }
    )

    return {
        "success": True,
        "message": "Password reset initiated"
    }
