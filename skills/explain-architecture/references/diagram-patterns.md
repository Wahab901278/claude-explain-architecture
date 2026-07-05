# Diagram patterns — which diagram, when, and how

Every diagram must pass the **grandma test**: a smart non-programmer should get the
gist in 10 seconds from the shapes and labels alone.

## Universal style rules

- `%% caption: <one plain-English sentence>` as the FIRST line of every `.mmd` file.
  The renderer prints it under the title in the PDF.
- Max ~12 nodes. Over that: split into overview + zoom-in diagrams.
- Edge labels are verbs: `-->|saves the order|`, `-->|asks for prices|`.
- Node labels are roles, not filenames: `Payments (talks to Stripe)`, not `stripe.ts`.
  Put the filename in parentheses only when the human will need to find it.
- Group related nodes with `subgraph` blocks named in plain English
  ("Runs on your server", "Third-party services", "The database").
- Use a consistent shape language:
  - `([User])` stadium — people
  - `[Service]` rectangle — code you own
  - `[(Database)]` cylinder — storage
  - `{{External API}}` hexagon — third-party services
- Theme: default/neutral. No custom colors unless distinguishing "your code" vs
  "external" (then: one classDef for external, light gray fill).

## 1. System overview (always) — `flowchart LR`

The 30,000-foot view. User on the left, external services on the right.

```mermaid
%% caption: The big picture — how a user's click travels through the app and back.
flowchart LR
    U([User's browser]) -->|clicks, types| FE[Frontend<br/>the visible app]
    FE -->|sends requests| API[Backend API<br/>the brain]
    API -->|reads / writes| DB[(Database<br/>where data lives)]
    API -->|charges cards| STRIPE{{Stripe}}
    API -->|sends emails| MAIL{{Email service}}
```

## 2. Module map (always) — `flowchart TD`

Top-level folders as boxes, arrows = "imports from / calls". Answers "what is each
folder for and what talks to what". Derive edges from actual imports, not guesses.

```mermaid
%% caption: What each folder does and which folders depend on which.
flowchart TD
    subgraph "The app's code"
        CLI[cli/ — commands you type]
        API[api/ — receives web requests]
        CORE[core/ — shared logic everything uses]
        PROV[providers/ — one adapter per AI service]
    end
    CLI --> API
    API --> CORE
    API --> PROV
    PROV --> CORE
```

## 3. Primary data flow (always) — `sequenceDiagram`

ONE user action, end to end. Pick the action the app exists for (checkout for a shop,
send-message for a chat app). Number of participants ≤ 6.

```mermaid
%% caption: Step by step: what happens when a user sends a message.
sequenceDiagram
    actor U as User
    participant FE as Frontend
    participant API as Backend
    participant DB as Database
    U->>FE: types message, hits send
    FE->>API: POST /messages
    API->>DB: save message
    API-->>FE: saved ✓
    FE-->>U: message appears in chat
```

## 4. ERD (if data layer exists) — `erDiagram`

Source it from migrations / ORM models / `schema.prisma` / SQL files — never from
imagination. Include: table names, relationships with cardinality, and only the
5–8 most meaningful columns per table (id, foreign keys, the "business" fields).
Skip timestamps/updated_at noise.

```mermaid
%% caption: What the app remembers: each box is a "spreadsheet" of stored data, lines show how they connect.
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "appears in"
    USER {
        int id PK
        string email
        string name
    }
    ORDER {
        int id PK
        int user_id FK
        string status
        decimal total
    }
```

NoSQL: still use `erDiagram` — collections as entities, embedded docs as
`||--|{ ... : embeds`.

## 5. Request lifecycle (if server) — `flowchart LR`

The gauntlet a request runs: middleware, auth, validation, handler, response.
Show error exits as dashed arrows.

```mermaid
%% caption: The checkpoints every web request passes through before getting an answer.
flowchart LR
    IN([Request arrives]) --> AUTH{Logged in?}
    AUTH -- no --> R401[401 rejected]
    AUTH -- yes --> VAL{Valid input?}
    VAL -- no --> R400[400 rejected]
    VAL -- yes --> H[Handler does the work]
    H --> RESP([Response sent])
```

## 6. Deployment (if infra config exists) — `flowchart TB`

Where each piece physically runs. Source from Dockerfile, docker-compose, vercel.json,
fly.toml, terraform, CI deploy steps. Subgraph per platform/host.

```mermaid
%% caption: Where each part of the app actually runs on the internet.
flowchart TB
    subgraph "Vercel (frontend hosting)"
        FE[Next.js app]
    end
    subgraph "Fly.io (server hosting)"
        API[API server]
        WORK[Background worker]
    end
    subgraph "Supabase (managed)"
        DB[(Postgres)]
    end
    FE --> API
    API --> DB
    WORK --> DB
```

## Optional extras (only when clearly present)

- **State machine** (`stateDiagram-v2`): order status, job lifecycle, auth session —
  when the code has an explicit status/state enum with transitions.
- **Event flow** (`flowchart` with queue hexagons): pub/sub, webhooks, background
  jobs — when there's a queue/broker (Redis, SQS, Celery, BullMQ).
- **C4-style context** (`C4Context` if mermaid version supports it, else flowchart):
  for multi-service systems / monorepos with several deployables.

## Anti-patterns

- One mega-diagram with 30 nodes. Split it.
- Diagramming the file tree verbatim. The module map shows ROLES, not `ls` output.
- Unlabeled arrows. An arrow without a verb is a guess the reader has to make.
- Class diagrams of every class. Vibe-coders don't need UML; they need "what talks
  to what and why".
- Copying example diagrams from this file into output. These are shape references;
  every real diagram comes from the actual code.
