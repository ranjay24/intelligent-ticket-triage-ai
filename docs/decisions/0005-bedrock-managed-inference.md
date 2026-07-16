# 0005 — Bedrock (managed) for the AI layer

**Status:** Accepted

## Context
The system needs an LLM for classification and reply drafting. Options ranged
from self-hosting an open model to calling a third-party API, to using a managed
model on AWS.

## Decision
Use **Amazon Bedrock** with an open-weights model (`google.gemma-3-27b-it`).
No inference infrastructure to run, requests stay within AWS/IAM, and it fits the
serverless model of the rest of the stack.

## Alternatives considered
- **Self-host an open model (SageMaker / EC2 + GPU)** — full control, but real
  ops burden and idle GPU cost for a bursty support workload.
- **A higher-capability managed model (e.g. Claude on Bedrock)** — better quality
  on hard tickets, at higher per-token cost. Straightforward to switch to, since
  only the model id and request body change.
- **A non-AWS API (e.g. OpenAI)** — capable, but customer ticket text would leave
  the AWS trust boundary, complicating the data-handling story.

## Consequences
- Zero inference infra; IAM-scoped access; data stays in-account.
- Model choice is a one-line change (`MODEL_ID`), so quality/cost can be re-tuned
  — the eval harness exists precisely to compare models objectively.
- Gemma is cost-effective and scored 97.8% on our eval; a harder production mix
  might justify moving up to a stronger model, measured via the same harness.
