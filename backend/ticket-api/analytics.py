import boto3
import os
import json
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def get_analytics():

    response = table.scan()

    tickets = response["Items"]

    analytics = {
        "totalTickets": 0,
        "newTickets": 0,
        "pendingReview": 0,
        "approved": 0,
        "rejected": 0,

        "authentication": 0,
        "billing": 0,
        "technicalIssue": 0,
        "accountManagement": 0,
        "generalInquiry": 0,
        "outOfScope": 0,

        "avgConfidence": 0
    }

    confidence_sum = 0
    confidence_count = 0

    for ticket in tickets:

        analytics["totalTickets"] += 1

        status = ticket.get("status")

        if status == "NEW":
            analytics["newTickets"] += 1

        elif status == "PENDING_REVIEW":
            analytics["pendingReview"] += 1

        elif status == "APPROVED":
            analytics["approved"] += 1

        elif status == "REJECTED":
            analytics["rejected"] += 1

        category = ticket.get("category")

        if category == "Authentication":
            analytics["authentication"] += 1

        elif category == "Billing":
            analytics["billing"] += 1

        elif category == "Technical Issue":
            analytics["technicalIssue"] += 1

        elif category == "Account Management":
            analytics["accountManagement"] += 1

        elif category == "General Inquiry":
            analytics["generalInquiry"] += 1

        elif category == "Out Of Scope":
            analytics["outOfScope"] += 1

        confidence = ticket.get("confidence")

        if confidence is not None:

            confidence_sum += float(confidence)
            confidence_count += 1

    if confidence_count > 0:

        analytics["avgConfidence"] = round(
            confidence_sum / confidence_count,
            2
        )

    return {
        "statusCode": 200,
        "body": json.dumps(analytics)
    }