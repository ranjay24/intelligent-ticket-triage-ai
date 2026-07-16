# 0003 — Confidence threshold for auto-resolution

**Status:** Accepted

## Context
Non-destructive, non-critical tickets auto-resolve — but only if the model is
confident enough. We needed a threshold below which a ticket goes to a human.

## Decision
Auto-resolve requires classification **confidence > 0.85**; at or below `0.85`
the ticket is sent to review (`LOW_CONFIDENCE`). The value is a single constant
in the processor, so it can be tuned (and should become an env var).

## Alternatives considered
- **Lower (e.g. 0.70)** — higher auto-resolution rate, more wrong auto-sends.
- **Higher (e.g. 0.95)** — very safe, but almost everything goes to a human.

## Consequences
- Conservative default that favors safety over automation rate.
- The eval showed the model emits coarse confidence values (≈0.75 / 0.85 / 0.95),
  so the threshold behaves like a step: at `0.85`, the 0.85-confidence tickets go
  to review; dropping to ~0.80 sharply increases auto-resolution.
- Tunable per business appetite: the eval harness can report the auto-resolution
  rate at different thresholds to pick the operating point.
