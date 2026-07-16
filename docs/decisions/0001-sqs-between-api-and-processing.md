# 0001 — Queue between the API and AI processing

**Status:** Accepted

## Context
Creating a ticket triggers AI work (classification + RAG drafting) that takes a
few seconds and calls Bedrock. Doing that inside the API request would make the
customer wait several seconds for a "create ticket" call and couple the API's
availability to Bedrock's.

## Decision
The API validates and enqueues the ticket to **SQS**, then returns `201`
immediately. A separate **ticket-processor** Lambda consumes the queue and does
the AI work asynchronously, updating the ticket in DynamoDB when done.

## Alternatives considered
- **Synchronous processing in the API** — simplest, but 3–5s response times and
  the API fails whenever Bedrock is slow/throttled.
- **Step Functions** — great for complex multi-step orchestration, but overkill
  for a linear classify→draft→store flow, and more moving parts.
- **Direct async Lambda invoke** — works, but loses SQS's built-in retries,
  buffering, and (future) dead-letter handling.

## Consequences
- Fast, resilient API; processing scales independently and absorbs bursts.
- **Eventual consistency:** a ticket first appears as `NEW`, then updates a few
  seconds later — the UI refreshes to reflect the final state.
- SQS gives at-least-once delivery, so processing must tolerate retries.
- **Known gap:** no dead-letter queue / partial-batch response yet, so one bad
  message currently reprocesses its whole batch. Tracked as hardening.
