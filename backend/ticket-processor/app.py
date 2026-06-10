import json
import boto3
import os

from classifier import classify_ticket
from reply_generator import generate_reply

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    for record in event["Records"]:

        ticket = json.loads(record["body"])

        try:

            classification = classify_ticket(
                ticket["subject"],
                ticket["description"]
            )

            ticket["category"] = classification["category"]
            ticket["priority"] = classification["priority"]
            ticket["sentiment"] = classification["sentiment"]
            ticket["language"] = classification["language"]
            ticket["draftReply"] = generate_reply(ticket)

        except Exception as e:

            print("CLASSIFICATION FAILED")
            print(str(e))

            ticket["category"] = "UNKNOWN"
            ticket["priority"] = "LOW"
            ticket["sentiment"] = "NEUTRAL"
            ticket["language"] = "EN"

        table.put_item(
            Item=ticket
        )

    return {
        "statusCode": 200
    }