import json
import urllib.parse
import boto3
import os
from datetime import datetime
from observability import log_info

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]

# BUCKET_NAME = os.environ["BUCKET_NAME"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    print(json.dumps(event))

    for record in event["Records"]:

        bucket_name = record["s3"]["bucket"]["name"]

        key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        print(f"Uploaded file: {key}")

        parts = key.split("/")

        if len(parts) < 3:
            continue

        ticket_id = parts[1]

        file_name = parts[-1]

        extension = file_name.split(".")[-1].lower()

        if extension in ["png", "jpg", "jpeg"]:
            content_type = "image"

        elif extension == "pdf":
            content_type = "pdf"

        else:
            content_type = "file"

        object_url = (
            f"https://{bucket_name}.s3.amazonaws.com/{key}"
        )

        attachment = {

            "fileName": file_name,

            "fileKey": key,

            "fileUrl": object_url,

            "contentType": content_type,

            "uploadedAt": datetime.utcnow().isoformat()

        }

        table.update_item(

            Key={
                "ticketId": ticket_id
            },

            UpdateExpression="""
                SET attachments =
                list_append(
                    if_not_exists(attachments,:empty),
                    :attachment
                )
            """,

            ExpressionAttributeValues={

                ":empty": [],

                ":attachment": [
                    attachment
                ]

            }

        )

        # Log attachment processing
        log_info(
            "ATTACHMENT_PROCESSED",
            ticketId=ticket_id,
            fileKey=key
        )

    return {

        "statusCode": 200

    }