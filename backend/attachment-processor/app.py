import json
import urllib.parse
import boto3
import os

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    print(json.dumps(event))

    for record in event["Records"]:

        key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        print(f"Uploaded file: {key}")

        parts = key.split("/")

        if len(parts) < 3:
            continue

        ticket_id = parts[1]

        file_name = parts[-1]

        table.update_item(
            Key={
                "ticketId": ticket_id
            },
            UpdateExpression="""
                SET attachments =
                list_append(
                    if_not_exists(attachments, :empty),
                    :attachment
                )
            """,
            ExpressionAttributeValues={
                ":empty": [],
                ":attachment": [
                    {
                        "fileName": file_name,
                        "fileKey": key
                    }
                ]
            }
        )

    return {
        "statusCode": 200
    }