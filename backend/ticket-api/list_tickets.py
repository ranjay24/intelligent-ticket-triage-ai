import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)

def list_tickets():

    response = table.scan()

    return {
        "statusCode": 200,
        "body": json.dumps(response["Items"])
    }