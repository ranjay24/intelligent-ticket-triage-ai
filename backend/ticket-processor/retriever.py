import boto3

s3 = boto3.client("s3")

BUCKET_NAME = "ticket-kb-479752407378"


CATEGORY_FILES = {
    "Authentication": "password-reset.txt",
    "Billing": "billing-refund.txt",
    "Technical Issue": "outage-guide.txt",
    "Account Management": "account-update.txt",
    "General Inquiry": "general-inquiry.txt",
    "Out Of Scope": "out-of-scope.txt"
}


def retrieve_documents(category):

    file_name = CATEGORY_FILES.get(
        category,
        "general-inquiry.txt"
    )

    try:

        file = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=file_name
        )

        content = (
            file["Body"]
            .read()
            .decode("utf-8")
        )

        return content, [file_name]

    except Exception as e:

        print("KB RETRIEVAL FAILED")
        print(str(e))

        return (
            "Knowledge base article not found.",
            []
        )