import boto3
import os

from boto3.dynamodb.conditions import Key

from response import build_response

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

    return build_response(
        200,
        response["Items"]
    )