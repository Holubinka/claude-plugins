# Mermaid Diagram Examples

Ready-to-use templates, one per diagram type, in the order the Decision Guide in
[`SKILL.md`](SKILL.md) introduces them.

Every template below is drawn from one worked subject — an order-fulfilment service with an
HTTP API, background jobs, Postgres, and external payment and shipping providers. It is a
**shape to copy, not a system to reproduce**: replace the nouns with the ones in front of you.

**The note under each diagram is the point.** It says what that diagram type earns its place
for. Read those even if you skip the code.

**Anchor every diagram you draw to real code, and say where.** A diagram whose subject you
reconstructed from memory reads exactly like one you verified — that is what makes it
dangerous. Name the file you read, and re-read it before reusing the diagram later.

---

## 1. Flowchart — classifying one item against a chain of rules

A branching process with four terminal buckets, which is exactly what a flowchart is for.

```mermaid
flowchart TD
    P(["one line item from the submitted order"]) --> PKG["record the item's warehouse<br/>on the order"]
    PKG --> SKIP{"skippable?"}
    SKIP -->|"digital · already fulfilled"| S[["skipped[] — with the reason"]]
    SKIP -->|no| FLAG{"needs review?"}
    FLAG -->|"restricted · oversized · export-controlled"| F[["flagged[] — reason + who decides"]]
    FLAG -->|no| DOM{"in stock?"}
    DOM -->|"no"| C[["backordered[] — with the ETA"]]
    DOM -->|"yes"| R[["pickable[] — + bin location"]]

    style F fill:#ff6b6b,color:#fff
```

**Why the warehouse is recorded first.** The two early exits below it leave the loop body, so an
item counted after them would contribute nothing. **A flowchart earns its place when the *order*
of the steps is the point** — that is the whole difference between this and a bulleted list of
the four buckets.

---

## 2. Flowchart — a request that hands off to background work

Two background jobs chained by an enqueue, which no sequence diagram would show as clearly.

```mermaid
flowchart LR
    A["POST /orders"] --> B["OrderService.submit<br/>parse payload → customer/items"]
    B --> C{"already submitted?<br/>(idempotency key)"}
    C -->|yes| C200["200 — existing order, created: false"]
    C -->|no| D[("insert into orders")]
    D --> E{{"enqueue payment job"}}
    E --> F["201 — response returns now,<br/>the job runs after it"]

    E -.-> G["runPaymentJob"]
    G --> H["secrets.get PAYMENT_API_KEY"]
    H --> I[["PaymentClient.authorize — idempotent by order id"]]
    I --> J[("update orders.payment_state")]
    J --> K{{"enqueue fulfilment job"}}
    K -.-> L["warehouse picker"]
    L --> M[("shipments · shipment_items<br/>tracking_events")]
```

**Dashed edges mean "hands off to a job", not "calls".** The response at `F` is already on the
wire while `G` runs — and drawing that distinction is most of why this diagram exists. A reader
who thinks `F` waits for `M` will design the wrong retry.

---

## 3. Sequence Diagram — one write through the rings

The canonical `route → service → repository` shape, with validation ahead of the handler.
Copy this when the flow is a plain write; reach for §2 instead when the interesting part is what
happens after the response.

```mermaid
sequenceDiagram
    participant C as client
    participant V as framework + schema
    participant R as orders/routes.ts
    participant S as OrderService
    participant Repo as OrderRepository
    participant D as Postgres
    participant J as JobRunner

    C->>V: POST /orders { items, idempotencyKey }
    alt body fails the schema
        V-->>C: 422 — handler never runs
    else body valid
        V->>R: req.body typed
        activate R
        R->>S: submit(workspaceId, userId, payload)
        activate S
        S->>Repo: findByIdempotencyKey(workspaceId, key)
        Repo->>D: SELECT … WHERE idempotency_key = $1
        D-->>Repo: row | undefined
        Repo-->>S: row | undefined
        alt already exists
            S-->>R: { order, created: false }
            R-->>C: 200
        else new
            S->>Repo: insert(values)
            Repo->>D: INSERT … RETURNING *
            D-->>Repo: row
            S->>J: enqueue(payment)
            Note over S,J: fire-and-forget —<br/>the payment outlives this request
            S-->>R: { order, created: true }
            R-->>C: 201
        end
        deactivate S
        deactivate R
    end
```

**Note the ring discipline: the route never talks to `D`.** If your repository has a boundary
gate, a diagram that showed the route reaching the database would be drawing a violation — which
makes this diagram a design review as well as documentation. Draw what the rules allow, or
report the divergence.

---

## 4. Class Diagram — ports and their adapters

Use a class diagram for the *shape* of a boundary — not for tables, which is what §5 is for.

```mermaid
classDiagram
    class PaymentClient {
        <<interface>>
        +readonly id
        +authorize(order) Authorization
        +capture(authId, amount) Capture
        +refund(captureId, amount) Refund
    }
    class ShippingClient {
        <<interface>>
        +quote(address, items) Rate[]
        +createLabel(shipment) Label
        +track(trackingNumber) TrackingEvent[]
    }
    class NotificationClient {
        <<interface>>
        +send(template, to, vars) messageId
    }
    class SecretsProvider {
        <<interface>>
        +get(key) string
        +set(key, value) void
    }

    class StripePaymentClient
    class AdyenPaymentClient
    class EasyPostShippingClient
    class EmailNotificationClient
    class LocalSecretsProvider
    class MockPaymentClient
    class MockShippingClient

    class Container {
        +payment(provider) PaymentClient
        +shipping ShippingClient
        +notifications NotificationClient
        +secrets SecretsProvider
    }

    PaymentClient <|.. StripePaymentClient
    PaymentClient <|.. AdyenPaymentClient
    PaymentClient <|.. MockPaymentClient
    ShippingClient <|.. EasyPostShippingClient
    ShippingClient <|.. MockShippingClient
    NotificationClient <|.. EmailNotificationClient
    SecretsProvider <|.. LocalSecretsProvider

    Container --> PaymentClient
    Container --> ShippingClient
    Container --> NotificationClient
    Container --> SecretsProvider
```

**`Container` points at the interfaces, never at the boxes on the right.** An arrow from
`Container` to `StripePaymentClient` is drawing a dependency-direction violation, and this is the
diagram type where such a violation is most visible. Note also that every port has a mock: that
is the rule, not a testing convenience.

---

## 5. ER Diagram — the tables behind one feature

Give the column types the database actually creates, so the diagram can be **checked against
`\d+ orders`** rather than believed.

```mermaid
erDiagram
    WORKSPACES {
        uuid id PK "defaultRandom()"
        text name
        timestamptz created_at
    }

    CUSTOMERS {
        uuid id PK
        uuid workspace_id FK "on delete cascade"
        text email "unique per workspace"
        text display_name
        timestamptz created_at
    }

    ORDERS {
        uuid id PK
        uuid workspace_id FK
        uuid customer_id FK
        text idempotency_key "unique with workspace_id — safe retries"
        text status "lifecycle, not payment state"
        text payment_state "null until the payment job lands"
        numeric total_cents
        timestamptz placed_at
        timestamptz updated_at
    }

    ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        text sku
        integer quantity
        numeric unit_price_cents "captured at order time, not looked up later"
    }

    SHIPMENTS {
        uuid id PK
        uuid workspace_id FK
        uuid order_id FK
        text carrier
        text tracking_number
        text status
        timestamptz shipped_at
    }

    TRACKING_EVENTS {
        uuid id PK
        uuid shipment_id FK
        text code
        text description
        timestamptz occurred_at
    }

    WORKSPACES ||--o{ CUSTOMERS : owns
    WORKSPACES ||--o{ ORDERS : owns
    WORKSPACES ||--o{ SHIPMENTS : owns
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o{ SHIPMENTS : "fulfilled by"
    SHIPMENTS ||--o{ TRACKING_EVENTS : records
```

**Say the tenancy rule once, in prose, rather than per table.** Every table here carries
`workspace_id` because tenancy is resolved at the route and every query filters on it. Drawing an
arrow for it eight times is noise; leaving it out entirely hides the rule.

---

## 6. State Diagram — a lifecycle where some states are derived

Mark which states are **stored** and which are **derived on read**. That distinction is
invisible in the code to anyone who has not opened the function, and it is the first thing a
reader of the diagram will get wrong.

```mermaid
stateDiagram-v2
    [*] --> awaiting_payment: submitted

    awaiting_payment --> paid: authorization captured
    awaiting_payment --> payment_failed: declined or expired
    payment_failed --> awaiting_payment: customer retries
    paid --> picking: warehouse accepts
    picking --> shipped: label created
    shipped --> delayed: no tracking event for DELAY_DAYS (3)
    delayed --> shipped: tracking resumes
    shipped --> delivered
    delayed --> delivered

    awaiting_payment --> cancelled
    paid --> cancelled
    picking --> cancelled

    delivered --> [*]
    cancelled --> [*]

    note right of delayed
        Derived, not stored.
        cancelled and delivered come
        straight from the DB column.
    end note
```

---

## 7. Mindmap — a hierarchy with no edges worth naming

**The moment the arrows would mean something, use §1 or §3 instead.** A mindmap has no edge
semantics at all, so using one for a system with real relationships throws that information away
silently.

```mermaid
mindmap
  root((the monorepo))
    server/
      HTTP framework
      ORM
      Postgres
      schema validation
    client/
      Next.js App Router
      React
      a query cache
      a CSS framework
    core/
      pure TS library
      two runtime dependencies
      emits no JS
    e2e/
      browser driver
      declarative flows
```

---

## What has no template here, and why

**Gantt** and **pie** are in the Decision Guide but have no template in this file, and that is
deliberate. Neither has a subject here that would be honest: there is no dated schedule to chart
and no measured distribution to slice.

**Inventing plausible numbers for a diagram is the same failure as seeding fake rows to make a
screen look fuller** — the picture reads as evidence and is not. Syntax for both is in
[`SKILL.md`](SKILL.md); bring your own real numbers.
