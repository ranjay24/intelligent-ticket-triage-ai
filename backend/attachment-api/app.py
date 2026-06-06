import json
import boto3
import os
import uuid

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]


def lambda_handler(event, context):

    try:

        body = json.loads(event.get("body") or "{}")

        file_name = body.get("fileName")

        if not file_name:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "fileName is required"
                })
            }

        ticket_id = event["pathParameters"]["ticketId"]

        file_key = (
            f"tickets/"
            f"{ticket_id}/"
            f"{uuid.uuid4()}-{file_name}"
        )

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key
            },
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "ticketId": ticket_id,
                "fileKey": file_key,
                "uploadUrl": upload_url
            })
        }

    except Exception as e:

        print(str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e)
            })
        }