import boto3
import os

from response import build_response

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def _scan_all():
    """Scan the whole table, following pagination.

    A single scan() returns at most 1 MB of data; without following
    LastEvaluatedKey, analytics silently ignore everything past the
    first page once the table grows.
    """
    items = []

    response = table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    return items


def get_analytics():

    tickets = _scan_all()

    analytics = {

        "summary": {

            "totalTickets": 0,

            "newTickets": 0,

            "pendingReview": 0,

            "resolved": 0,

            "rejected": 0,

            "closed": 0,

            # Deprecated alias, kept == resolved so the existing
            # frontend "Approved" card keeps working until it's
            # relabelled to "Resolved".
            "approved": 0,

            "avgConfidence": 0

        },

        "categoryDistribution": {},

        "priorityDistribution": {},

        "recentTickets": []

    }

    confidence_sum = 0
    confidence_count = 0

    tickets = sorted(
        tickets,
        key=lambda x: x.get("createdAt", ""),
        reverse=True
    )

    analytics["recentTickets"] = tickets[:5]

    for ticket in tickets:

        analytics["summary"]["totalTickets"] += 1

        status = ticket.get("status")

        if status == "NEW":
            analytics["summary"]["newTickets"] += 1

        elif status == "PENDING_REVIEW":
            analytics["summary"]["pendingReview"] += 1

        # Fold legacy "APPROVED" rows into resolved so pre-migration
        # tickets still show up correctly.
        elif status in ("RESOLVED", "APPROVED"):
            analytics["summary"]["resolved"] += 1

        elif status == "REJECTED":
            analytics["summary"]["rejected"] += 1

        elif status == "CLOSED":
            analytics["summary"]["closed"] += 1

        category = ticket.get("category") or "Unknown"

        analytics["categoryDistribution"][category] = (
            analytics["categoryDistribution"].get(category, 0) + 1
        )

        priority = ticket.get("priority") or "Unknown"

        analytics["priorityDistribution"][priority] = (
            analytics["priorityDistribution"].get(priority, 0) + 1
        )

        confidence = ticket.get("confidence")

        if confidence is not None:
            confidence_sum += float(confidence)
            confidence_count += 1

    # Keep the deprecated alias in sync
    analytics["summary"]["approved"] = analytics["summary"]["resolved"]

    if confidence_count > 0:
        analytics["summary"]["avgConfidence"] = round(
            confidence_sum / confidence_count,
            2
        )

    return build_response(
        200,
        analytics
    )