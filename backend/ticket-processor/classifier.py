import boto3
import json

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

MODEL_ID = "google.gemma-3-27b-it"


def classify_ticket(subject, description):

    prompt = f"""
You are a customer support ticket classifier.

Analyze the ticket and return ONLY valid JSON.

Ticket Subject:
{subject}

Ticket Description:
{description}

Return exactly:

{{
  "category": "",
  "priority": "",
  "sentiment": "",
  "language": "",
  "confidence": 0.0
}}

Categories:
- Authentication
- Billing
- Technical Issue
- Account Management
- General Inquiry
- Out Of Scope

Priorities:
- LOW
- MEDIUM
- HIGH
- CRITICAL

Sentiments:
- POSITIVE
- NEUTRAL
- NEGATIVE

Languages:
- English
- Spanish
- French
- German
- Hindi
- Other

Rules:
- Return ONLY JSON.
- Do not include explanations.
- Do not include markdown.
- Do not wrap the JSON in ```json blocks.
- Language must be one of the listed language values.
- If the request is unrelated to software, customer accounts,
  billing, authentication, subscriptions, applications,
  websites, or platform support, classify as "Out Of Scope".
- Confidence:
- Between 0.0 and 1.0
- Higher means more certain
- If the ticket lacks enough information to determine
  the category confidently, return confidence below 0.60.
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
            "max_tokens": 200,
            "temperature": 0.1
        })
    )

    response_body = json.loads(
        response["body"].read()
    )

    text = response_body["choices"][0]["message"]["content"]

    print("CLASSIFICATION RESPONSE")
    print(text)

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    print("CLEANED RESPONSE")
    print(text)

    try:
        return json.loads(text)

    except Exception as e:

        print("JSON PARSE ERROR")
        print(text)
        print(str(e))

        return {
            "category": "General Inquiry",
            "priority": "LOW",
            "sentiment": "NEUTRAL",
            "language": "English",
            "confidence": 0.0
        }