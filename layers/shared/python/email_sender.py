import os
import boto3

from observability import log_info, log_error

AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

# Sender address is configurable so it can be swapped for a verified
# domain identity (e.g. support@yourdomain.com) without a code change.
FROM_EMAIL = os.environ.get("FROM_EMAIL", "ran2002924@gmail.com")

ses = boto3.client("ses", region_name=AWS_REGION)


def send_email(to_email, ticket_id, reply_text):

    log_info(
        "EMAIL_SENDING",
        ticketId=ticket_id,
        to=to_email,
        source=FROM_EMAIL,
    )

    response = ses.send_email(
        Source=FROM_EMAIL,
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {
                "Data": f"Ticket Update - {ticket_id}"
            },
            "Body": {
                "Text": {
                    "Data": reply_text
                }
            }
        }
    )

    log_info(
        "EMAIL_ACCEPTED",
        ticketId=ticket_id,
        to=to_email,
        messageId=response.get("MessageId"),
    )

    return response
