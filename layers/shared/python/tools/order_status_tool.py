import boto3
import os

dynamodb = boto3.resource("dynamodb")

orders_table = dynamodb.Table(
    os.environ.get("ORDERS_TABLE", "orders")
)


def get_order_status(order_id):

    if not order_id:
        return {
            "success": False,
            "message": "No order id provided"
        }

    response = orders_table.get_item(
        Key={
            "orderId": order_id
        }
    )

    order = response.get("Item")

    if not order:
        return {
            "success": False,
            "message": "Order not found"
        }

    return {
        "success": True,
        "orderId": order_id,
        "status": order.get("status", "UNKNOWN")
    }
