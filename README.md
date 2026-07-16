# Intelligent Customer Support — Ticket Triage & Resolution Assistant

A serverless, AI-powered support system that auto-classifies incoming tickets,
drafts grounded replies from a knowledge base, safely executes backend actions
(order status, password reset, refund) with a human-in-the-loop gate for
sensitive ones, and auto-resolves confident tier-1 requests — leaving humans to
review only what actually needs judgment.

Built on AWS (serverless) with Amazon Bedrock for the AI layer and a React
admin/customer UI.

---

## What it does

- **Ingests** tickets via a REST API (and can be extended to email).
- **Classifies** each ticket in a single model call — category, priority,
  sentiment, language, confidence, and the required action.
- **Drafts a reply** grounded on a help-center knowledge base (RAG) with source
  citations.
- **Acts** on the customer's behalf through tools: `getOrderStatus`,
  `resetPassword`, `issueRefund`.
- **Escalates** to a human when a ticket is a destructive action, is CRITICAL,
  or the model is not confident — otherwise it auto-resolves and emails the
  customer.
- **Notifies + observes** via SES email, CloudWatch metrics/logs, and alarms.

Evaluated at **97.8% classification accuracy** and **p50/p95 latency of
1.52s / 2.14s** on a 50-ticket labeled set — see
[`eval/EVAL_REPORT.md`](eval/EVAL_REPORT.md).

---

## Architecture (AWS)

```
                    ┌──────────────┐
   Customer  ─────► │ API Gateway  │
   / Admin UI       └──────┬───────┘
                           │
                 ┌─────────▼──────────┐        ┌──────────────┐
                 │  ticket-api Lambda │───────►│   SQS queue  │
                 │  (CRUD, approve,   │        └──────┬───────┘
                 │   reject, analytics)│               │
                 └─────────┬──────────┘               ▼
                           │              ┌────────────────────────┐
             ┌─────────────┼─────────┐    │ ticket-processor Lambda│
             ▼             ▼         ▼    │  1. classify (Bedrock) │
       DynamoDB        Cognito     SES    │  2. RAG draft (S3 KB)  │
      (tickets,        (auth,     (email) │  3. tools / review gate│
       customers,      Admins             │  4. write + email      │
       orders)         group)             └───────────┬────────────┘
                                                       │
   Attachments:  UI ─► attachment-api (presigned S3 URL)
                  S3 ─► attachment-processor (S3 event) ─► DynamoDB

   Observability: CloudWatch (metrics, logs, alarms) ─► SNS
```

A rendered diagram is in [`docs/architecture.md`](docs/architecture.md).

**Ticket lifecycle:**

```
NEW ─► AI triage ─┬─ Out of scope ───────────────► CLOSED
                  ├─ Confident, no action ───────► RESOLVED (auto + email)
                  ├─ Order-status tool succeeds ─► RESOLVED (auto + email)
                  └─ Destructive / CRITICAL / low ► PENDING_REVIEW
                        confidence                     │
                                          ┌────────────┴───────────┐
                                     approve                    reject
                                          │                        │
                          run tool + email + RESOLVED           REJECTED
```

---

## Tech stack

| Layer | Service |
|---|---|
| Ingestion / API | API Gateway + SQS |
| Compute | AWS Lambda (Python 3.11) |
| Storage | DynamoDB (tickets, customers, orders), S3 (attachments, KB) |
| Auth | Amazon Cognito (`Admins` group → admin role) |
| AI layer | Amazon Bedrock (`google.gemma-3-27b-it`) — classification + drafting |
| Retrieval | S3 knowledge base + category retrieval (RAG) |
| Notification | Amazon SES (email) |
| IaC | AWS SAM (CloudFormation) |
| Observability | CloudWatch metrics, logs, alarms; X-Ray |
| Frontend | React + Vite + Tailwind, `react-oidc-context` (Cognito), Recharts/Chart.js |

---

## Repository structure

```
.
├── backend/
│   ├── ticket-api/            # REST API: CRUD, approve/reject, analytics
│   ├── ticket-processor/      # SQS consumer: classify, RAG, tools, resolve
│   ├── attachment-api/        # presigned upload/download URLs
│   └── attachment-processor/  # S3 event → attach file to ticket
├── frontend/                  # React admin + customer UI
├── eval/                      # eval set, runner, report
├── docs/                      # architecture + decision log
├── template.yaml              # SAM/CloudFormation stack
└── README.md
```

---

## Prerequisites

- AWS account with Bedrock model access enabled in `ap-south-1`
- AWS CLI, SAM CLI, Python 3.11, Docker (for `sam build`)
- Node.js 18+ (frontend)
- An Amazon Cognito user pool + app client, with an `Admins` group
- A verified SES sender identity (and verified recipients while in the SES
  sandbox)

---

## Setup & deploy

### 1. Backend (SAM)

```bash
sam build
sam deploy --guided      # first time; then just: sam deploy
```

Note the stack outputs — `ApiUrl`, `AttachmentsBucket`, table names, `QueueUrl`.

### 2. Knowledge base

Upload help-center articles to the KB bucket under category prefixes
(`Authentication/`, `Billing/`, `Technical/`, `AccountManagement/`,
`GeneralInquiry/`, `OutOfScope/`). The retriever reads these per category.

### 3. Frontend

```bash
cd frontend
npm install

# .env
echo "VITE_API_BASE_URL=<ApiUrl without trailing /tickets>" >> .env

npm run dev      # local
npm run build    # production bundle
```

Add your app's URL (local `http://localhost:5173` and your deployed URL) to the
Cognito app client's **Allowed callback URLs** and **Allowed sign-out URLs**.

---

## Configuration (environment variables)

Backend (set in `template.yaml` function environments; all have safe defaults):

| Variable | Used by | Purpose |
|---|---|---|
| `TABLE_NAME`, `CUSTOMERS_TABLE`, `ORDERS_TABLE` | api, processor | DynamoDB tables |
| `QUEUE_URL` | ticket-api | SQS queue |
| `BUCKET_NAME` | attachment fns | attachments bucket |
| `FROM_EMAIL` | api, processor | SES sender (use a verified domain in prod) |
| `KB_BUCKET` | processor | knowledge-base bucket |

Frontend (`.env`, prefixed `VITE_`):

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | API Gateway base URL |
| `VITE_REDIRECT_URI` | (optional) overrides `window.location.origin` |

---

## Evaluation

A labeled 50-ticket eval set + a runner that scores the real pipeline:

```bash
python eval/run_eval.py --processor-dir backend/ticket-processor
```

Reports classification accuracy / macro-F1, tool-call correctness, latency
p50/p95, and estimated cost. Full write-up in
[`eval/EVAL_REPORT.md`](eval/EVAL_REPORT.md); details in `eval/README.md`.

---

## Observability

- Custom CloudWatch metrics (namespace `TicketTriageAI`): `TicketsCreated`,
  `TicketsProcessed`, `PendingReview`, `TicketResolved`, `EmailSent`,
  `ApiError`, tool metrics, etc.
- Structured JSON logs per stage (`AI_PROCESSING_STARTED`,
  `CLASSIFICATION_COMPLETE`, `REVIEW_REQUIRED`, `AI_PROCESSING_COMPLETED`).
- An alarm on API errors publishing to SNS.

---

## Security notes

- Least-privilege IAM per function (SAM policy templates + scoped statements).
- Cognito-gated UI; admin-only routes behind an `Admins` group check.
- Attachment download URLs are restricted to the ticket's own S3 prefix.
- Destructive actions (refund, password reset) require explicit human approval.
- Wildcard CORS is used for the demo; restrict `AllowOrigin` to your domain in
  production.

---

## Teardown

```bash
sam delete
```

The attachments bucket uses `DeletionPolicy: Retain`; empty and delete it
manually if you want it removed.

---

## Known limitations & future work

- SQS→processor has no dead-letter queue / partial-batch response yet (a poison
  message retries the whole batch). Tracked as a hardening item.
- Shared code (`email_sender`, `observability`, `response`, `tools`) is
  duplicated per function; a Lambda Layer would centralize it.
- KB retrieval loads all articles in a category; a vector store would scale
  better and improve citation precision.
- No PII redaction / Bedrock Guardrails step yet before sending text to the LLM.
- Stretch: multi-language replies, Bedrock-vs-Vertex A/B, voice ingestion.

See [`docs/decisions/`](docs/decisions/) for the key design trade-offs.
