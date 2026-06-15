import json
import boto3
import os
from decimal import Decimal

from classifier import classify_ticket
from reply_generator import generate_reply
from email_sender import send_email
from domain_validator import detect_domain

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    for record in event["Records"]:

        ticket = json.loads(record["body"])

        try:

            domain_result = detect_domain(
                ticket["subject"],
                ticket["description"]
            )

            print("DOMAIN RESULT")
            print(domain_result)

            if domain_result == "OUT_OF_SCOPE":

                ticket["category"] = "Out Of Scope"
                ticket["priority"] = "LOW"
                ticket["sentiment"] = "NEUTRAL"
                ticket["language"] = "English"

                ticket["draftReply"] = (
                    "Thank you for contacting support. "
                    "This request appears to be outside the scope of "
                    "our support platform. Please contact the appropriate "
                    "service provider for assistance."
                )

                ticket["sources"] = [
                    "out-of-scope.txt"
                ]

            else:

                classification = classify_ticket(
                    ticket["subject"],
                    ticket["description"]
                )

                ticket["confidence"] = Decimal(
                    str(classification.get(
                            "confidence",
                            0.5
                        )
                    )
                )

                if ticket["confidence"] <= 0.85:

                    ticket["requiresReview"] = True
                    ticket["status"] = "PENDING_REVIEW"

                else:

                    ticket["requiresReview"] = False

                ticket["category"] = classification["category"]
                ticket["priority"] = classification["priority"]
                ticket["sentiment"] = classification["sentiment"]
                ticket["language"] = classification["language"]

                try:

                    rag_result = generate_reply(ticket)

                    ticket["draftReply"] = rag_result["reply"]
                    ticket["sources"] = rag_result["sources"]

                except Exception as e:

                    print("RAG FAILED")
                    print(str(e))

                    ticket["draftReply"] = (
                        "Support team will investigate."
                    )

                    ticket["sources"] = []

            if (ticket.get("customerEmail") and not ticket["requiresReview"]):

                try:

                    send_email(
                        ticket["customerEmail"],
                        ticket["ticketId"],
                        ticket["draftReply"]
                    )

                except Exception as e:

                    print("EMAIL FAILED")
                    print(str(e))

        except Exception as e:

            print("PROCESSING FAILED")
            print(str(e))

            ticket["category"] = "UNKNOWN"
            ticket["priority"] = "LOW"
            ticket["sentiment"] = "NEUTRAL"
            ticket["language"] = "EN"
            ticket["draftReply"] = "Support team will investigate."
            ticket["sources"] = []
            ticket["confidence"] = Decimal("0.0")
            ticket["requiresReview"] = True



        print(type(ticket["confidence"]))
        print(ticket["confidence"])
        table.put_item(
            Item=ticket
        )

    return {
        "statusCode": 200
    }