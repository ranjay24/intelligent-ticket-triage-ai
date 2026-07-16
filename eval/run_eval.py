"""
Evaluation harness for the Intelligent Ticket Triage system.

It imports your REAL pipeline modules (domain_validator, classifier,
action_detector, and optionally reply_generator) from the ticket-processor
folder and runs the 50-ticket labeled set through them exactly the way the
processor does. It reports:

  - Classification accuracy + macro-F1 (category)
  - Domain-detection accuracy (in-scope vs out-of-scope)
  - Tool-call correctness (actionType)
  - Latency p50 / p95 (measured, real)
  - Estimated cost per ticket (transparent token estimate x your price)
  - Groundedness (only with --with-rag: does the reply cite a real KB source?)

Nothing is written to DynamoDB and no emails are sent.

USAGE (from the repo root):
  python eval/run_eval.py --processor-dir backend/ticket-processor
  python eval/run_eval.py --processor-dir backend/ticket-processor --with-rag
  python eval/run_eval.py --processor-dir backend/ticket-processor \
      --price-in 0.0006 --price-out 0.0006

Requires: AWS credentials + Bedrock access in your environment
(the same ones `sam deploy` uses).
"""

import argparse
import importlib
import json
import os
import statistics
import sys
import time
from collections import defaultdict


# ---- transparent token-estimate constants (documented assumptions) ----
# Rough fixed prompt overhead per model call, in tokens. These are estimates
# used only for the cost model; latency below is measured, not estimated.
OVERHEAD_TOKENS = {"domain": 180, "classify": 430, "action": 250}
OUTPUT_TOKENS = {"domain": 5, "classify": 120, "action": 40}


def est_tokens_for_text(text):
    return max(1, len(text) // 4)


def load_pipeline(processor_dir):
    processor_dir = os.path.abspath(processor_dir)
    if not os.path.isdir(processor_dir):
        sys.exit(f"processor-dir not found: {processor_dir}")
    sys.path.insert(0, processor_dir)

    mods = {}
    try:
        mods["classifier"] = importlib.import_module("classifier")
    except Exception as e:
        sys.exit(f"Failed to import classifier from {processor_dir}: {e}")

    # Optional (needs S3 KB access + env)
    try:
        mods["reply_generator"] = importlib.import_module("reply_generator")
    except Exception:
        mods["reply_generator"] = None

    return mods


def predict(ticket, mods):
    """Mirror the processor's orchestration for a single ticket."""
    subject = ticket["subject"]
    description = ticket["description"]

    calls = ["classify"]  # single consolidated call
    t0 = time.perf_counter()

    classification = mods["classifier"].classify_ticket(subject, description)
    latency = time.perf_counter() - t0

    category = classification.get("category", "General Inquiry")
    confidence = classification.get("confidence", 0.0)
    action_type = classification.get("actionType", "NONE")
    domain = "OUT_OF_SCOPE" if category == "Out Of Scope" else "SUPPORTED"

    # Cost estimate
    text_tokens = est_tokens_for_text(subject + " " + description)
    in_tokens = sum(OVERHEAD_TOKENS[c] + text_tokens for c in calls)
    out_tokens = sum(OUTPUT_TOKENS[c] for c in calls)

    return {
        "domain": domain,
        "category": category,
        "actionType": action_type,
        "confidence": confidence,
        "latency": latency,
        "in_tokens": in_tokens,
        "out_tokens": out_tokens,
    }


def macro_f1(pairs, labels):
    """pairs: list of (expected, predicted). Returns macro-F1 over labels."""
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    for exp, pred in pairs:
        if exp == pred:
            tp[exp] += 1
        else:
            fp[pred] += 1
            fn[exp] += 1

    f1s = []
    for lab in labels:
        p = tp[lab] / (tp[lab] + fp[lab]) if (tp[lab] + fp[lab]) else 0.0
        r = tp[lab] / (tp[lab] + fn[lab]) if (tp[lab] + fn[lab]) else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


def run_rag_groundedness(tickets, preds, mods):
    """For SUPPORTED tickets, check the reply cites a real (non-empty) source
    and isn't the generic fallback."""
    gen = mods.get("reply_generator")
    if gen is None:
        return None

    grounded = 0
    total = 0
    for t, p in zip(tickets, preds):
        if p["domain"] == "OUT_OF_SCOPE":
            continue
        total += 1
        ticket_obj = {
            "subject": t["subject"],
            "description": t["description"],
            "category": p["category"],
            "priority": t["expected"].get("priorityHint", "LOW"),
        }
        try:
            result = gen.generate_reply(ticket_obj)
            sources = result.get("sources", [])
            reply = (result.get("reply") or "").lower()
            is_fallback = "support team will investigate" in reply
            if sources and not is_fallback:
                grounded += 1
        except Exception as e:
            print(f"  [rag] {t['id']} failed: {e}")
    return {"grounded": grounded, "total": total,
            "score": (grounded / total) if total else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processor-dir", required=True,
                    help="Path to backend/ticket-processor")
    ap.add_argument("--eval-set",
                    default=os.path.join(os.path.dirname(__file__), "eval_set.json"))
    ap.add_argument("--limit", type=int, default=0, help="Only run first N tickets")
    ap.add_argument("--with-rag", action="store_true",
                    help="Also measure groundedness (needs S3 KB access)")
    ap.add_argument("--price-in", type=float, default=0.0,
                    help="USD per 1K input tokens (set from Bedrock pricing)")
    ap.add_argument("--price-out", type=float, default=0.0,
                    help="USD per 1K output tokens (set from Bedrock pricing)")
    ap.add_argument("--out-dir",
                    default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()

    data = json.load(open(args.eval_set, encoding="utf-8"))
    tickets = data["tickets"]
    if args.limit:
        tickets = tickets[: args.limit]

    mods = load_pipeline(args.processor_dir)

    print(f"Running {len(tickets)} tickets through the pipeline...\n")

    preds = []
    for i, t in enumerate(tickets, 1):
        p = predict(t, mods)
        preds.append(p)
        exp = t["expected"]
        ok_cat = "OK" if p["category"] == exp["category"] else "XX"
        print(f"[{i:2}/{len(tickets)}] {t['id']:9} {ok_cat} "
              f"pred={p['category']:<18} exp={exp['category']:<18} "
              f"act={p['actionType']:<16} {p['latency']:.2f}s")

    # ---- metrics ----
    graded = [(t, p) for t, p in zip(tickets, preds)]
    non_edge = [(t, p) for t, p in graded if not t.get("edge")]

    def acc(pairs, field, exp_field=None):
        exp_field = exp_field or field
        if not pairs:
            return 0.0, 0, 0
        hits = sum(1 for t, p in pairs
                   if p[field] == t["expected"][exp_field])
        return hits / len(pairs), hits, len(pairs)

    cat_acc, cat_hits, cat_n = acc(non_edge, "category")
    dom_acc, dom_hits, dom_n = acc(graded, "domain")
    act_acc, act_hits, act_n = acc(non_edge, "actionType")

    cat_f1 = macro_f1(
        [(t["expected"]["category"], p["category"]) for t, p in non_edge],
        data["categories"],
    )

    latencies = sorted(p["latency"] for p in preds)
    p50 = statistics.median(latencies)
    p95 = latencies[max(0, int(round(0.95 * len(latencies))) - 1)]

    avg_in = sum(p["in_tokens"] for p in preds) / len(preds)
    avg_out = sum(p["out_tokens"] for p in preds) / len(preds)
    cost_per_ticket = (avg_in / 1000 * args.price_in) + (avg_out / 1000 * args.price_out)

    rag = run_rag_groundedness(tickets, preds, mods) if args.with_rag else None

    # ---- report ----
    print("\n" + "=" * 60)
    print("EVAL REPORT")
    print("=" * 60)
    print(f"Tickets evaluated        : {len(tickets)}  ({len(non_edge)} graded, "
          f"{len(tickets) - len(non_edge)} edge)")
    print(f"Category accuracy        : {cat_acc*100:5.1f}%  ({cat_hits}/{cat_n})")
    print(f"Category macro-F1        : {cat_f1:5.3f}")
    print(f"Domain accuracy          : {dom_acc*100:5.1f}%  ({dom_hits}/{dom_n})")
    print(f"Tool-call correctness    : {act_acc*100:5.1f}%  ({act_hits}/{act_n})")
    print(f"Latency p50 / p95        : {p50:.2f}s / {p95:.2f}s")
    print(f"Avg tokens (in / out)    : {avg_in:.0f} / {avg_out:.0f}  (estimated)")
    if args.price_in or args.price_out:
        print(f"Est. cost per ticket     : ${cost_per_ticket:.4f}")
    else:
        print(f"Est. cost per ticket     : set --price-in/--price-out to compute")
    if rag is not None:
        print(f"Groundedness             : {rag['score']*100:5.1f}%  "
              f"({rag['grounded']}/{rag['total']})")
    print("=" * 60)

    # misclassifications
    misses = [(t, p) for t, p in non_edge
              if p["category"] != t["expected"]["category"]]
    if misses:
        print("\nCategory misclassifications:")
        for t, p in misses:
            print(f"  {t['id']:9} pred={p['category']:<18} "
                  f"exp={t['expected']['category']}")

    # ---- write machine-readable + markdown ----
    report = {
        "n": len(tickets),
        "category_accuracy": cat_acc,
        "category_macro_f1": cat_f1,
        "domain_accuracy": dom_acc,
        "tool_call_correctness": act_acc,
        "latency_p50": p50,
        "latency_p95": p95,
        "avg_tokens_in": avg_in,
        "avg_tokens_out": avg_out,
        "est_cost_per_ticket": cost_per_ticket if (args.price_in or args.price_out) else None,
        "groundedness": rag,
    }
    with open(os.path.join(args.out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md = f"""# Ticket Triage — Evaluation Report

Ran the labeled eval set ({len(tickets)} tickets, {len(non_edge)} graded)
through the live classification pipeline.

| Metric | Result |
|---|---|
| Category accuracy | {cat_acc*100:.1f}% ({cat_hits}/{cat_n}) |
| Category macro-F1 | {cat_f1:.3f} |
| Domain (in/out of scope) accuracy | {dom_acc*100:.1f}% |
| Tool-call correctness | {act_acc*100:.1f}% ({act_hits}/{act_n}) |
| Latency p50 / p95 | {p50:.2f}s / {p95:.2f}s |
| Avg tokens per ticket (in/out, est.) | {avg_in:.0f} / {avg_out:.0f} |
| Est. cost per ticket | {('$%.4f' % cost_per_ticket) if (args.price_in or args.price_out) else 'n/a'} |
| Groundedness | {('%.1f%%' % (rag['score']*100)) if rag else 'not run'} |

*Latency is measured. Token counts and cost are estimated from a documented
token model (see run_eval.py). Edge/ambiguous tickets are excluded from
accuracy and reported separately.*
"""
    with open(os.path.join(args.out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\nWrote report.json and report.md to {args.out_dir}")


if __name__ == "__main__":
    main()
