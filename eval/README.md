# Evaluation Harness

Scores the ticket-triage AI pipeline against a labeled set of 50 tickets.
It imports your real pipeline code (`domain_validator`, `classifier`,
`action_detector`, optionally `reply_generator`) and runs each ticket through
it the same way the processor Lambda does — so it measures the actual prompts,
not a copy. Nothing is written to DynamoDB and no emails are sent.

## What it measures

- **Category accuracy** and **macro-F1** — the headline "≥90% on top categories" metric
- **Domain accuracy** — in-scope vs out-of-scope detection
- **Tool-call correctness** — did it pick the right action (RESET_PASSWORD / ISSUE_REFUND / GET_ORDER_STATUS / NONE)
- **Latency p50 / p95** — measured wall-clock per ticket
- **Estimated cost per ticket** — transparent token estimate × your Bedrock price
- **Groundedness** (with `--with-rag`) — does the drafted reply cite a real KB source

Edge/ambiguous tickets (`edge: true`) are excluded from accuracy and reported separately.

## Prerequisites

Same AWS credentials + Bedrock access you use for `sam deploy`
(the pipeline calls Bedrock in `ap-south-1`). For `--with-rag` you also need
read access to the KB S3 bucket.

## Run

From the repository root:

```bash
# core metrics (classification, action, latency)
python eval/run_eval.py --processor-dir backend/ticket-processor

# also measure groundedness (needs the KB bucket)
python eval/run_eval.py --processor-dir backend/ticket-processor --with-rag

# include a cost estimate (set the prices from the Bedrock pricing page)
python eval/run_eval.py --processor-dir backend/ticket-processor \
    --price-in 0.0006 --price-out 0.0006

# quick smoke test on the first 5 tickets
python eval/run_eval.py --processor-dir backend/ticket-processor --limit 5
```

## Output

- Console table + per-ticket pass/fail and a list of misclassifications
- `report.json` — machine-readable metrics
- `report.md` — a drop-in table for your eval report / README

## Notes

- **Latency is real** (measured around the model calls). **Token/cost numbers
  are estimates** from a documented model in `run_eval.py` — Bedrock doesn't
  return token usage for these calls, so tune `--price-in/--price-out` with the
  real per-1K-token price and treat cost as an estimate.
- Two runs will differ slightly: the models run at `temperature > 0`, so a
  single run isn't gospel. For the report, run 2–3 times and note the range.
- To grow the set, add entries to `eval_set.json` with an `expected` block.
