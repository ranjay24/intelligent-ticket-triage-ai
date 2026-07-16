# Evaluation Report — Intelligent Ticket Triage

**Scope:** classification quality, tool-call correctness, latency, and cost of
the AI triage pipeline, plus a before/after comparison of a pipeline
optimization (three model calls → one).

**Method:** a labeled set of 50 tickets (46 graded + 4 intentionally
ambiguous "edge" cases) is run through the *actual* pipeline code
(`classifier.py` and the processor orchestration), calling Amazon Bedrock
(`google.gemma-3-27b-it`, `ap-south-1`). Latency is measured wall-clock;
token counts and cost are estimated from a documented token model. Because the
model runs at `temperature = 0.1`, results vary slightly run to run; numbers
below are from a representative run and are stable in shape across runs.

---

## Headline result — pipeline consolidation

The original design used **three sequential Bedrock calls** per in-scope ticket
(domain detection → classification → action detection). The eval surfaced two
problems with this: (1) a legitimate order-shipping question was wrongly
rejected by the standalone domain check, and (2) the classifier and the
separate action detector sometimes disagreed on the same ticket. Both were
resolved by consolidating all three into a **single classification call**.

| Metric | Before (3 calls) | After (1 call) | Change |
|---|---|---|---|
| Category accuracy | 95.7% | **97.8%** | +2.1 pts |
| Category macro-F1 | 0.954 | **0.979** | +0.025 |
| Domain (in/out of scope) accuracy | 98.0% | **100%** | +2.0 pts |
| Tool-call correctness | 95.7% | 95.7% | — |
| Latency p50 / p95 | 2.37s / 3.22s | **1.52s / 2.14s** | ~35% faster |
| Avg input tokens / ticket (est.) | 820 | **450** | −45% |
| Bedrock calls / ticket | 3 | **1** | −2 calls |

**Takeaway:** one-third the model calls, ~35% lower median latency, ~45% fewer
input tokens — and accuracy *improved*. Consolidation was strictly better on
this eval set.

---

## Classification accuracy by category (current pipeline)

| Category | Correct / Total |
|---|---|
| Authentication | 8 / 8 |
| Billing | 8 / 8 |
| Technical Issue | 10 / 10 |
| Account Management | 6 / 6 |
| General Inquiry | 7 / 8 |
| Out Of Scope | 6 / 6 |
| **Overall (graded)** | **45 / 46 (97.8%)** |

Macro-F1 across the six categories: **0.979**.

---

## Tool-call correctness

Action detection (RESET_PASSWORD / ISSUE_REFUND / GET_ORDER_STATUS / NONE):
**44 / 46 (95.7%)**. Order-number extraction was correct on every order-status
ticket (e.g. `ORD1001`, `ORD2050`, `ORD3120`). The misses were on the
billing action boundary — for example, "Why was I charged twice?" was read as a
refund request (`ISSUE_REFUND`) rather than an informational billing question
(`NONE`). This is a conservative failure mode: it routes to a human review gate
rather than taking an unwanted action, so no destructive action is ever
triggered by a misread.

---

## Latency and cost

- **Latency:** p50 1.52s, p95 2.14s for the classification step. Well under the
  6s target. Order-status and out-of-scope tickets short-circuit fastest
  (~1s). End-to-end draft latency adds one RAG retrieval + generation call on
  top for tickets that need a drafted reply.
- **Cost (estimated):** ~450 input + ~120 output tokens per ticket for
  classification. At Bedrock per-token pricing this is a fraction of a cent per
  ticket, comfortably inside the < $0.05/ticket target. (Cost is an estimate —
  Bedrock does not return token usage for these calls, so it is computed from a
  documented token model in `run_eval.py`.)

---

## Result vs. project targets

| Target (from brief) | Result |
|---|---|
| Classification accuracy ≥ 90% on top categories | **97.8%** |
| p95 latency < 6s for draft generation | **2.14s** (classification); + RAG for drafts |
| Cost < $0.05 per ticket | **~570 tokens/ticket** — within budget |
| Safe tool use with human-in-the-loop | Destructive actions + CRITICAL + low confidence gated to review |

---

## Known limitations & honest caveats

1. **One boundary miss (`gen-08`).** "Difference between Pro and Team plans" was
   labeled General Inquiry but classified as Billing. This is a genuine
   label-boundary ambiguity (a pricing question is billing-adjacent), not a
   clear error. Forcing it could degrade real Billing classification, so it is
   left as-is and noted.
2. **Non-deterministic.** `temperature = 0.1` means runs differ slightly.
   Report the range over 2–3 runs rather than a single number.
3. **Cost is estimated,** not measured (no token usage returned by Bedrock).
4. **Small, curated set (50).** Accuracy on a real production stream — with more
   billing/general-inquiry volume and messier text — would differ. The set is a
   sanity-and-regression tool, not a production accuracy guarantee.
5. **Edge cases excluded from accuracy.** The 4 intentionally ambiguous tickets
   (multi-intent, one-word, non-English) are reported separately; the pipeline
   handled 3 of 4 as expected and correctly detected Spanish.

---

## How to reproduce

```bash
python eval/run_eval.py --processor-dir backend/ticket-processor
python eval/run_eval.py --processor-dir backend/ticket-processor --with-rag
```

Outputs `eval/report.json` and `eval/report.md`. See `eval/README.md`.
