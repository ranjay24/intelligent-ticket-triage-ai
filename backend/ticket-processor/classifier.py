import boto3
import json

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

MODEL_ID = "google.gemma-3-27b-it"


def classify_ticket(subject, description):
    """Single-call triage: scope + category + priority + sentiment +
    language + confidence + action detection (incl. order id extraction).

    This replaces the previous three separate Bedrock calls
    (domain_validator -> classifier -> action_detector) with one.
    """

    prompt = f"""
You are a customer support ticket triage system.

Analyze the ticket and return ONLY valid JSON with exactly this shape:

{{
  "category": "",
  "priority": "",
  "sentiment": "",
  "language": "",
  "confidence": 0.0,
  "actionType": "",
  "entityType": "",
  "entityId": ""
}}

Ticket Subject:
{subject}

Ticket Description:
{description}

Categories:
- Authentication
- Billing
- Technical Issue
- Account Management
- General Inquiry
- Out Of Scope

Scope:
This platform handles software / SaaS customer support, for example:
login and password problems, billing and invoices, subscriptions,
account management, orders and order tracking, application errors,
website issues, and technical support.
Order status and shipping questions ARE in scope (General Inquiry).
Only if the ticket is clearly unrelated to software or this kind of
customer support - for example plumbing, car repair, medical advice,
legal advice, home maintenance, electrical work, or a physical product
unrelated to the platform - set category to "Out Of Scope".

Priorities:
- LOW
- MEDIUM
- HIGH
- CRITICAL
Use CRITICAL for outages or issues affecting many users or blocking all work.

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

Actions:
- NONE
- RESET_PASSWORD
- ISSUE_REFUND
- GET_ORDER_STATUS

Entity Types:
- NONE
- CUSTOMER
- ORDER

Action rules:
- Forgot password, cannot log in after a reset, or explicitly asks to
  reset the password -> actionType=RESET_PASSWORD, entityType=CUSTOMER
- Requests a refund, duplicate-charge refund, subscription refund, or
  payment reversal -> actionType=ISSUE_REFUND, entityType=ORDER
- Asks for order status / tracking / "where is my order" ->
  actionType=GET_ORDER_STATUS, entityType=ORDER
- Otherwise -> actionType=NONE, entityType=NONE
- If an order number is mentioned (e.g. ORD1001), put it in entityId.
  Otherwise set entityId to "".

Example - "Where is my order ORD1001?":
{{"category":"General Inquiry","priority":"MEDIUM","sentiment":"NEUTRAL","language":"English","confidence":0.95,"actionType":"GET_ORDER_STATUS","entityType":"ORDER","entityId":"ORD1001"}}

Confidence:
- Between 0.0 and 1.0, higher means more certain.
- If the ticket lacks enough information to classify confidently,
  use a value below 0.60.

Rules:
- Return ONLY the JSON. No explanations, no markdown, no code fences.
- category, priority, sentiment, language, actionType and entityType
  must each be one of the listed values.
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
            "max_tokens": 250,
            "temperature": 0.1
        })
    )

    response_body = json.loads(response["body"].read())

    text = response_body["choices"][0]["message"]["content"]

    print("CLASSIFICATION RESPONSE")
    print(text)

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    print("CLEANED RESPONSE")
    print(text)

    try:
        result = json.loads(text)

        # Normalize the fields the pipeline relies on
        return {
            "category": result.get("category", "General Inquiry"),
            "priority": result.get("priority", "LOW"),
            "sentiment": result.get("sentiment", "NEUTRAL"),
            "language": result.get("language", "English"),
            "confidence": result.get("confidence", 0.0),
            "actionType": result.get("actionType", "NONE"),
            "entityType": result.get("entityType", "NONE"),
            "entityId": result.get("entityId", ""),
        }

    except Exception as e:

        print("JSON PARSE ERROR")
        print(text)
        print(str(e))

        # Safe fallback: low confidence routes to human review
        return {
            "category": "General Inquiry",
            "priority": "LOW",
            "sentiment": "NEUTRAL",
            "language": "English",
            "confidence": 0.0,
            "actionType": "NONE",
            "entityType": "NONE",
            "entityId": "",
        }
