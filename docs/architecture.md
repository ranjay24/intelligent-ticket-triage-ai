# Architecture

![Architecture diagram](architecture.svg)

## Components

| Component | Responsibility |
|---|---|
| **React UI** | Admin console (triage, review, analytics) and customer portal, authenticated via Cognito. |
| **Amazon Cognito** | Authentication and authorization; the `Admins` group gates the admin surface. |
| **API Gateway** | REST entry point with CORS; routes to the Lambda functions. |
| **ticket-api Lambda** | Ticket CRUD, analytics, and the review actions (approve/reject). Enqueues new tickets to SQS. |
| **SQS (ticket-queue)** | Decouples ingestion from AI processing so the API responds instantly and processing scales independently. |
| **ticket-processor Lambda** | SQS consumer. Runs the single classification call, RAG drafting, tool execution, the review gate, and persists the result. |
| **Amazon Bedrock** | The AI layer (`google.gemma-3-27b-it`) — one call returns category, priority, sentiment, language, confidence, and action. A second call drafts the reply. |
| **S3 Knowledge Base** | Help-center articles by category, retrieved for grounded (RAG) replies. |
| **DynamoDB** | `tickets` (with a `status` GSI), `customers` (with an `email` GSI), and `orders`. |
| **Amazon SES** | Sends the customer email on auto-resolve, out-of-scope, and approval. |
| **attachment-api / attachment-processor** | Presigned S3 upload/download URLs; an S3 event attaches the uploaded file to the ticket. |
| **CloudWatch + SNS** | Custom metrics, structured logs, and an error alarm that notifies via SNS. |

## Flow (editable — renders on GitHub)

```mermaid
flowchart TD
    UI[React UI] -->|auth JWT| COG[Cognito]
    UI --> GW[API Gateway]
    GW --> API[ticket-api Lambda]
    API -->|enqueue| SQS[(SQS ticket-queue)]
    SQS -->|trigger| PROC[ticket-processor Lambda]

    API --> DDB[(DynamoDB)]
    PROC --> DDB
    PROC -->|classify + draft| BR[Amazon Bedrock]
    PROC -->|RAG| KB[(S3 Knowledge Base)]
    PROC -->|email| SES[Amazon SES]
    API -->|email on approve| SES

    GW --> ATT[attachment-api]
    ATT --> S3A[(S3 Attachments)]
    S3A -->|S3 event| ATTP[attachment-processor]
    ATTP --> DDB
```

## Sequence — ticket in → reply out

```mermaid
sequenceDiagram
    participant C as Customer
    participant GW as API Gateway
    participant API as ticket-api
    participant Q as SQS
    participant P as ticket-processor
    participant AI as Bedrock
    participant KB as S3 KB
    participant DB as DynamoDB
    participant M as SES

    C->>GW: POST /tickets
    GW->>API: invoke
    API->>Q: enqueue ticket (status NEW)
    API-->>C: 201 Created
    Q->>P: deliver message
    P->>AI: classify (1 call)
    alt Out of scope
        P->>DB: status CLOSED
        P->>M: courtesy email
    else Confident, no destructive action
        P->>KB: retrieve articles
        P->>AI: draft reply (RAG)
        P->>DB: status RESOLVED
        P->>M: send reply
    else Needs a human
        P->>DB: status PENDING_REVIEW
    end
```

## Sequence — review + tool call (human-in-the-loop)

```mermaid
sequenceDiagram
    participant A as Admin
    participant API as ticket-api
    participant T as Tool (reset/refund/order)
    participant DB as DynamoDB
    participant M as SES

    A->>API: POST /reviews/{id}/approve
    API->>DB: load ticket (must be PENDING_REVIEW)
    API->>T: execute action (only now)
    T-->>API: result
    API->>DB: status RESOLVED + history
    API->>M: send reply
    API-->>A: 200 resolved
```

See [`decisions/`](decisions/) for the design trade-offs behind these choices.
