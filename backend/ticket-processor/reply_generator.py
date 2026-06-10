import boto3
import json

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

MODEL_ID = "google.gemma-3-27b-it"


def generate_reply(ticket):

    prompt = f"""
You are a professional customer support agent.

Generate a helpful and polite customer support response.

Ticket Category:
{ticket["category"]}

Ticket Priority:
{ticket["priority"]}

Ticket Subject:
{ticket["subject"]}

Ticket Description:
{ticket["description"]}

Rules:
- Be professional.
- Be concise.
- Do not invent actions already taken.
- Do not invent links, URLs, phone numbers, emails, or support resources.
- If information is unavailable, say that the support team will investigate.
- Acknowledge the customer's issue.
- Suggest reasonable next steps.
- Return only the reply text.
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
            "max_tokens": 300,
            "temperature": 0.3
        })
    )

    response_body = json.loads(
        response["body"].read()
    )

    reply = response_body["choices"][0]["message"]["content"]

    return reply.strip()