import boto3
import os
from datetime import datetime

from response import build_response
from observability import (
    log_info,
    publish_metric
)

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def reject_ticket(ticket_id):

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

    if item.get("status") != "PENDING_REVIEW":
        return build_response(
            400,
            {
                "message": "Ticket is not pending review"
            }
        )

    now = datetime.utcnow().isoformat()

    # Status and history event now agree, and REJECTED exists in the
    # frontend STATUS_STYLES map (IN_PROGRESS did not, so it rendered
    # unstyled). Setting requiresReview=False drops it from the queue.
    item["status"] = "REJECTED"
    item["requiresReview"] = False
    item["updatedAt"] = now

    history = item.get("history", [])
    history.append({
        "event": "REJECTED",
        "time": now
    })
    item["history"] = history

    table.put_item(
        Item=item
    )

    publish_metric("TicketRejected")

    log_info(
        "TICKET_REJECTED",
        ticketId=ticket_id
    )

    return build_response(
        200,
        {
            "message": "Ticket rejected"
        }
    )