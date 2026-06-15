import boto3
import json

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

MODEL_ID = "google.gemma-3-27b-it"


def detect_domain(subject, description):

    prompt = f"""
Determine whether this ticket belongs to a software customer support platform.

Ticket Subject:
{subject}

Ticket Description:
{description}

Supported examples:
- Login issues
- Password reset
- Account update
- Billing problems
- Subscription issues
- Invoice issues
- Website issues
- Application errors
- Technical support requests

Out of scope examples:
- Plumbing issues
- Water leakage
- Car repair
- Medical advice
- Electrical work
- Home maintenance
- Legal advice

Return ONLY one value:

SUPPORTED

or

OUT_OF_SCOPE
"""

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 10,
            "temperature": 0
        })
    )

    response_body = json.loads(
        response["body"].read()
    )

    result = response_body["choices"][0]["message"]["content"]

    return result.strip()