import boto3
import json
from retriever import retrieve_documents

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

MODEL_ID = "google.gemma-3-27b-it"


def generate_reply(ticket):

    if ticket["category"] == "Out Of Scope":
        return {
        "reply": (
            "Thank you for contacting support. "
            "This request appears to be outside the scope of "
            "our support platform. Please contact the appropriate "
            "service provider for assistance."
        ),
        "sources": ["out-of-scope.txt"]
        }

    knowledge_base, sources = retrieve_documents(
    ticket["category"]
    )

    prompt = f"""
You are a professional customer support agent.

Use ONLY the information present in the knowledge base.

Knowledge Base:
{knowledge_base}

Ticket Category:
{ticket["category"]}

Ticket Priority:
{ticket["priority"]}

Ticket Subject:
{ticket["subject"]}

Ticket Description:
{ticket["description"]}

Rules:
- Use the knowledge base when answering.
- Do not invent information.
- Do not invent links.
- Do not invent phone numbers.
- Do not invent email addresses.
- If the knowledge base does not contain the answer, state that the support team will investigate.
- Be professional.
- Be concise.
- Return only the response text.
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

    return {
    "reply": reply.strip(),
    "sources": sources
    }