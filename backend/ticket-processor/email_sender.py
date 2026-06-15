import boto3

ses = boto3.client(
    "ses",
    region_name="ap-south-1"
)

FROM_EMAIL = "ran2002924@gmail.com"


def send_email(
        to_email,
        ticket_id,
        reply_text
):

    print(f"Sending email to {to_email}")
    response = ses.send_email(
        Source=FROM_EMAIL,
        Destination={
            "ToAddresses": [
                to_email
            ]
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
    print("EMAIL SENT")
    print(response)