# 0004 — One classification call instead of three

**Status:** Accepted (replaced an earlier three-call design)

## Context
The original pipeline made three sequential Bedrock calls per in-scope ticket:
domain detection → classification → action detection. The evaluation harness
surfaced two problems: a legitimate order-status question was wrongly rejected by
the standalone domain check, and the classifier and action detector sometimes
disagreed on the same ticket.

## Decision
Consolidate all three into a **single classification call** that returns scope,
category, priority, sentiment, language, confidence, and the action (including
order-id extraction).

## Alternatives considered
- **Keep three calls** — cleaner separation of concerns and each step is easy to
  isolate, but 3× the latency/cost and the components can disagree.
- **Two calls (merge domain into classify, keep action separate)** — partial win,
  but keeps the classifier/action disagreement.

## Consequences
Measured on the 50-ticket eval set:
- Bedrock calls per ticket **3 → 1**; median latency **2.37s → 1.52s**; input
  tokens **~820 → ~450**; category accuracy **95.7% → 97.8%** (the order-status
  miss was fixed and domain accuracy hit 100%).
- Trade-off: one larger prompt is slightly harder to debug than three focused
  ones, and a single call means a single point of parse failure — mitigated by a
  safe low-confidence fallback that routes to review.
