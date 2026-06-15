import boto3
import os
import json

from boto3.dynamodb.conditions import Key
from json_encoder import DecimalEncoder

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["TABLE_NAME"]
)


def get_pending_reviews():

    response = table.query(
        IndexName="status-index",
        KeyConditionExpression=
            Key("status").eq(
                "PENDING_REVIEW"
            )
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            response["Items"],
            cls=DecimalEncoder
        )
    }