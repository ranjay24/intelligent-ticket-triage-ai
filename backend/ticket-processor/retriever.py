import os
import boto3

s3 = boto3.client("s3")

# Configurable so the KB bucket isn't baked into source per account.
BUCKET_NAME = os.environ.get("KB_BUCKET", "ticket-kb-479752407378")

CATEGORY_PREFIXES = {
    "Authentication": "Authentication/",
    "Billing": "Billing/",
    "Technical Issue": "Technical/",
    "Account Management": "AccountManagement/",
    "General Inquiry": "GeneralInquiry/",
    "Out Of Scope": "OutOfScope/",
}


def retrieve_documents(category):

    prefix = CATEGORY_PREFIXES.get(category, "GeneralInquiry/")

    try:

        knowledge_base = ""
        sources = []

        paginator = s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):

            for file in page.get("Contents", []):

                key = file["Key"]

                if key.endswith("/"):
                    continue

                document = s3.get_object(Bucket=BUCKET_NAME, Key=key)

                content = document["Body"].read().decode("utf-8")

                knowledge_base += f"\n\n===== {key} =====\n"
                knowledge_base += content

                sources.append(key)

        if not sources:
            return "Knowledge base article not found.", []

        return knowledge_base, sources

    except Exception as e:

        print("KB RETRIEVAL FAILED")
        print(str(e))

        return "Knowledge base article not found.", []