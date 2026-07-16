# Cost Model

A rough monthly cost estimate for the ticket-triage system at three volumes.
The goal is to understand the shape of the cost — **which service dominates** —
not to predict a bill to the cent.

## Assumptions

- Region: `ap-south-1`, on-demand pricing, AWS Free Tier **not** counted
  (so these are conservative — real cost is lower while under free tier).
- Per ticket, the pipeline makes ~2 Bedrock calls (one classification, one RAG
  draft) totalling **~2,000 input + ~350 output tokens** (from the eval:
  ~450 in / ~120 out for classification, plus a larger RAG call with KB context).
- Processor Lambda: 256 MB, ~2s per invocation. API Lambda: negligible compute.
- One outbound email per resolved/closed ticket.
- **Bedrock price is the key unknown.** The numbers below use an *illustrative*
  blended rate of **$0.0006 per 1K input** and **$0.0006 per 1K output** tokens.
  Replace with the real per-token price for your model from the Bedrock pricing
  page — this is the one figure that materially moves the total.

## Per-service cost (illustrative rates)

| Service | Rate used | Per ticket |
|---|---|---|
| **Bedrock** (LLM) | $0.0006 / 1K tokens (in & out) | ~$0.0014 |
| SES (email) | $0.10 / 1,000 emails | ~$0.0001 |
| Lambda | $0.20 / 1M req + $16.67 / 1M GB-s | ~$0.00002 |
| DynamoDB (on-demand) | $1.25 / 1M writes, $0.25 / 1M reads | ~$0.00001 |
| SQS | $0.40 / 1M requests | ~$0.000001 |
| S3 (KB + attachments) | $0.023 / GB-mo + requests | negligible |
| CloudWatch (logs/metrics) | usage-based | negligible |

**Estimated cost per ticket ≈ $0.0016** — dominated by Bedrock (~88%).
Comfortably under the **$0.05/ticket** target, with ~30× headroom.

## Monthly cost by volume

| Tickets / month | Bedrock | SES | Lambda + DDB + SQS | **Total / mo** | **Per ticket** |
|---|---|---|---|---|---|
| 1,000 | ~$1.40 | ~$0.10 | ~$0.05 | **~$1.6** | ~$0.0016 |
| 10,000 | ~$14 | ~$1.00 | ~$0.50 | **~$16** | ~$0.0016 |
| 100,000 | ~$140 | ~$10 | ~$5 | **~$155** | ~$0.0016 |

(Storage/CloudWatch add a few dollars/month at the top end; omitted for clarity.)

## What this tells us

- **The LLM is the cost.** Everything else — compute, queue, database, email —
  is rounding error at these volumes. Cost optimization means token
  optimization, which is exactly why consolidating three model calls into one
  (see [ADR 0004](decisions/0004-single-call-classification.md)) mattered: it
  cut input tokens ~45%.
- **Stress-test the assumption.** Even if the real Bedrock rate is **10× higher**
  than assumed, per-ticket cost is ~$0.016 — still well under the $0.05 target.
  A stronger (pricier) model would raise this the most.
- **Levers if cost ever matters:** lower the confidence threshold to auto-resolve
  more without a human, cache KB retrieval, or shorten the RAG context.

*Prices are illustrative and change over time; confirm current rates on the AWS
pricing pages for your region. Cost is estimated (Bedrock does not return token
usage for these calls) using the token model documented in `eval/run_eval.py`.*