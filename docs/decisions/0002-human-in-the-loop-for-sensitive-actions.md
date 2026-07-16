# 0002 — Human-in-the-loop only for destructive / critical tickets

**Status:** Accepted

## Context
The system can take real actions (refund, password reset) and auto-send replies.
Fully automating everything is risky; routing everything to a human defeats the
purpose (slow, no automation win).

## Decision
A ticket is escalated to `PENDING_REVIEW` only when it is **(a)** a destructive
action (`ISSUE_REFUND`, `RESET_PASSWORD`), **(b)** `CRITICAL` priority, or
**(c)** low confidence. Everything else auto-resolves and emails the customer.
Destructive tools execute **only after** a human approves.

## Alternatives considered
- **Review everything** — safest, but no automation benefit and a human
  bottleneck.
- **Auto-resolve everything** — fastest, but unacceptable risk of wrong refunds,
  resets, or a confidently-wrong reply on a critical outage.

## Consequences
- Humans spend time only where judgment matters; confident tier-1 tickets clear
  automatically.
- No refund or reset can fire without explicit approval.
- The reasons for review are recorded on the ticket (`reviewReasons`) as an audit
  trail.
- A confident-but-wrong classification on a non-destructive ticket can still
  auto-send. Mitigated by the confidence gate (ADR 0003) and grounded RAG.
