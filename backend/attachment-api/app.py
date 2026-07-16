import json
import boto3
import os
import uuid
from observability import log_info
from response import build_response

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]

ALLOWED_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "application/pdf"
]


def lambda_handler(event, context):

    try:

        method = event["httpMethod"]

        ticket_id = event["pathParameters"]["ticketId"]

        # Every object for this ticket lives under this prefix.
        ticket_prefix = f"tickets/{ticket_id}/"

        # =====================================
        # GENERATE DOWNLOAD URL
        # =====================================

        if method == "GET":

            params = event.get("queryStringParameters") or {}

            file_key = params.get("key")

            if not file_key:
                return build_response(
                    400,
                    {"message": "key is required"}
                )

            # Only allow presigning objects that belong to THIS ticket.
            # Without this, any object in the bucket could be requested.
            if not file_key.startswith(ticket_prefix):
                return build_response(
                    403,
                    {"message": "key does not belong to this ticket"}
                )

            download_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": BUCKET_NAME,
                    "Key": file_key
                },
                ExpiresIn=3600
            )

            return build_response(
                200,
                {"downloadUrl": download_url}
            )

        # =====================================
        # GENERATE UPLOAD URL
        # =====================================

        body = json.loads(event.get("body") or "{}")

        file_name = body.get("fileName")
        content_type = body.get("contentType")

        if not file_name:
            return build_response(
                400,
                {"message": "fileName is required"}
            )

        if not content_type:
            return build_response(
                400,
                {"message": "contentType is required"}
            )

        if content_type not in ALLOWED_TYPES:
            return build_response(
                400,
                {"message": "Unsupported file type"}
            )

        file_key = f"{ticket_prefix}{uuid.uuid4()}-{file_name}"

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": content_type
            },
            ExpiresIn=3600
        )

        log_info(
            "UPLOAD_URL_GENERATED",
            ticketId=ticket_id,
            fileName=file_name,
            contentType=content_type
        )

        return build_response(
            200,
            {
                "ticketId": ticket_id,
                "fileKey": file_key,
                "contentType": content_type,
                "uploadUrl": upload_url
            }
        )

    except Exception as e:

        # Log the detail, return a generic message (don't leak internals).
        log_info(
            "ATTACHMENT_API_ERROR",
            error=str(e)
        )

        return build_response(
            500,
            {"message": "Internal server error"}
        )