# Ticket Triage — Evaluation Report

Ran the labeled eval set (50 tickets, 46 graded)
through the live classification pipeline.

| Metric | Result |
|---|---|
| Category accuracy | 97.8% (45/46) |
| Category macro-F1 | 0.979 |
| Domain (in/out of scope) accuracy | 100.0% |
| Tool-call correctness | 95.7% (44/46) |
| Latency p50 / p95 | 1.52s / 2.14s |
| Avg tokens per ticket (in/out, est.) | 450 / 120 |
| Est. cost per ticket | n/a |
| Groundedness | not run |

*Latency is measured. Token counts and cost are estimated from a documented
token model (see run_eval.py). Edge/ambiguous tickets are excluded from
accuracy and reported separately.*
