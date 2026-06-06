import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):

    for record in event["Records"]:

        ticket = json.loads(record["body"])

        table.put_item(
            Item=ticket
        )

    return {
        "statusCode": 200
    }