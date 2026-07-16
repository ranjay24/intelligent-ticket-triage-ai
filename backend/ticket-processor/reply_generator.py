import boto3
import json
from retriever import retrieve_documents

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

MODEL_ID = "google.gemma-3-27b-it"


def _match_sources(claimed, available):
    """Map the model's claimed source names back to real retrieved keys.

    Prevents hallucinated citations (only keys we actually retrieved can be
    cited) and tolerates the model returning a basename instead of the full
    S3 key.
    """
    cited = []
    for a in available:
        base = a.split("/")[-1]
        for c in claimed:
            c = str(c).strip()
            if c and (c == a or c == base or c in a):
                cited.append(a)
                break
    return cited


def generate_reply(ticket):

    if ticket["category"] == "Out Of Scope":
        return {
            "reply": (
                "Thank you for contacting support. "
                "This request appears to be outside the scope of "
                "our support platform. Please contact the appropriate "
                "service provider for assistance."
            ),
            "sources": ["out-of-scope.txt"],
        }

    knowledge_base, available_sources = retrieve_documents(ticket["category"])

    prompt = f"""
You are a professional customer support agent.

Use ONLY the information in the knowledge base below. Each article begins
with a header line like "===== <source> =====".

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

Write a reply to the customer, then list the exact source name(s) you
actually used to write it.

Return ONLY valid JSON in this shape (no markdown, no code fences):
{{"reply": "<the reply text>", "sources": ["<source used>", ...]}}

Rules:
- Use only facts present in the knowledge base. Do not invent information,
  links, phone numbers, or email addresses.
- "sources" must contain only names that appear as "=====" headers above,
  and only the ones you actually used. If you used none, return [].
- If the knowledge base does not contain the answer, state that the support
  team will investigate and return "sources": [].
- Be professional and concise.
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
            "max_tokens": 400,
            "temperature": 0.3
        })
    )

    response_body = json.loads(response["body"].read())
    text = response_body["choices"][0]["message"]["content"]

    text = text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(text)

        reply = (parsed.get("reply") or "").strip()
        claimed = parsed.get("sources") or []

        if not reply:
            raise ValueError("empty reply")

        # Only cite sources we actually retrieved
        cited = _match_sources(claimed, available_sources)

        return {"reply": reply, "sources": cited}

    except Exception as e:

        # Graceful fallback: the model didn't return clean JSON. Use the raw
        # text as the reply and fall back to listing the retrieved docs, so
        # we degrade to the old "whole category" behavior rather than losing
        # grounding entirely.
        print("REPLY PARSE FALLBACK")
        print(str(e))

        return {
            "reply": text or "Support team will investigate.",
            "sources": available_sources,
        }