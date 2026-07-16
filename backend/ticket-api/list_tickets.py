import boto3
import os

from boto3.dynamodb.conditions import Key

from response import build_response

dynamodb = boto3.resource("dynamodb")

tickets_table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

customers_table = dynamodb.Table(
    os.environ["CUSTOMERS_TABLE"]
)


def _scan_all(table, **kwargs):
    """Scan a table fully, following pagination.

    A single scan() returns at most 1 MB; without following
    LastEvaluatedKey, rows past the first page are silently dropped.
    """
    items = []

    response = table.scan(**kwargs)
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"],
            **kwargs
        )
        items.extend(response.get("Items", []))

    return items


def list_tickets():

    tickets = _scan_all(tickets_table)

    return build_response(
        200,
        tickets
    )


def list_my_tickets(customer_email):

    customer_response = customers_table.query(
        IndexName="email-index",
        KeyConditionExpression=Key("email").eq(customer_email)
    )

    customers = customer_response.get("Items", [])

    if len(customers) == 0:
        return build_response(
            200,
            []
        )

    customer_id = customers[0]["customerId"]

    # NOTE: This scans the whole table and filters in Python, which
    # reads every ticket on each call. It is correct but not scalable.
    # The proper fix is a GSI on customerId (see template.yaml note),
    # then replace this with a query. Kept as a scan to avoid an infra
    # change; pagination below at least makes it correct at any size.
    all_tickets = _scan_all(tickets_table)

    tickets = [
        ticket
        for ticket in all_tickets
        if ticket.get("customerId") == customer_id
    ]

    return build_response(
        200,
        tickets
    )