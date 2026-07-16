# Decision Log

Architecture Decision Records (ADRs) capturing the key trade-offs made while
building this system. Each records the context, the decision, the alternatives
considered, and the consequences (including the downsides).

| # | Decision |
|---|---|
| [0001](0001-sqs-between-api-and-processing.md) | Queue (SQS) between the API and AI processing |
| [0002](0002-human-in-the-loop-for-sensitive-actions.md) | Human-in-the-loop only for destructive / critical tickets |
| [0003](0003-confidence-gate-threshold.md) | Confidence threshold for auto-resolution |
| [0004](0004-single-call-classification.md) | One classification call instead of three |
| [0005](0005-bedrock-managed-inference.md) | Bedrock (managed) for the AI layer |
