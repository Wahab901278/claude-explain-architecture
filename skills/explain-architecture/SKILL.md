---
name: explain-architecture
description: >
  Read an entire codebase and explain its architecture visually — diagrams (system
  overview, module map, data flow, ERD, request lifecycle) rendered to PNG and PDF,
  plus a plain-English ARCHITECTURE.md for non-programmers and a dense AI-CONTEXT.md
  that can be fed back to any coding agent (Claude Code, Codex, Gemini CLI) to give it
  instant project understanding. Trigger when the user says "explain the architecture",
  "explain this codebase", "make an architecture diagram", "ERD", "visualize the code",
  "how does this project work", "onboarding doc", or "generate AI context for this repo".
---

# Explain Architecture

You are producing an architecture explainer for a **vibe-coder**: someone who builds
with AI but cannot read code fluently. Every output must be understandable by a smart
person who has never programmed. Visuals first, jargon last.

## Outputs (always all four)

All output goes in `docs/architecture/` inside the target repo:

| File | Audience | Purpose |
|------|----------|---------|
| `ARCHITECTURE.md` | Human (non-coder) | Plain-English walkthrough with embedded diagrams |
| `diagrams/*.png` + `architecture.pdf` | Human | Shareable visuals (PDF = all diagrams + captions in one doc) |
| `src/*.mmd` | Tooling | Editable Mermaid sources for every diagram |
| `AI-CONTEXT.md` | AI agents | Dense, structured project brief to paste/load into any agent session |

## Workflow

### Phase 1 — Scan the codebase

Do NOT read every file. Read strategically:

1. **Shape**: file tree 2–3 levels deep (`ls -R` depth-limited, or Glob). Note the top-level folders and what they suggest.
2. **Manifests**: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `composer.json`, `Gemfile`, `pom.xml` — dependencies reveal the stack.
3. **Entry points**: `main.*`, `index.*`, `app.*`, `server.*`, `cli.*`, `Dockerfile` CMD, `Procfile`, npm `scripts`.
4. **Config**: `.env.example`, `config/`, `settings.*`, `docker-compose.yml`, CI files, infra files (`*.tf`, `vercel.json`, `netlify.toml`, `fly.toml`).
5. **Data layer**: migrations, `models/`, `schema.prisma`, `*.sql`, ORM model files, `entities/`. This feeds the ERD.
6. **API surface**: route definitions, controllers, `api/` folders, OpenAPI specs, GraphQL schemas.
7. **Agent memory files**: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.claude/skills/`, `.github/copilot-instructions.md`, existing `README.md` — these tell you what past agents were told, and MUST be summarized into `AI-CONTEXT.md`.
8. **External services**: grep for SDK imports and API base URLs (stripe, supabase, firebase, openai, anthropic, twilio, s3, redis, etc.).

For large repos (>300 source files), fan out subagents per top-level directory and merge their summaries instead of reading inline.

### Phase 2 — Build the mental model

Before drawing anything, write down (internally) answers to:

- What does this app DO, in one sentence a non-coder understands?
- What are the 3–8 major parts (frontend, API, database, workers, third-party services)?
- How does data flow for the ONE most important user action? (e.g. "user posts a message")
- What data is stored, and how do the tables/collections relate?
- What external services does it depend on, and what breaks if each disappears?
- Where does the code start executing when the app boots?

If you cannot answer one of these, go back to Phase 1 for that gap.

### Phase 3 — Generate diagrams

Write Mermaid sources to `docs/architecture/src/`. Pick diagrams by what the codebase
actually contains — see `references/diagram-patterns.md` for the full decision table
and style rules. Typical set:

| # | File | Diagram | When |
|---|------|---------|------|
| 1 | `01-system-overview.mmd` | Flowchart: big boxes — user, frontend, backend, DB, external services | Always |
| 2 | `02-module-map.mmd` | Flowchart: top-level folders and what depends on what | Always |
| 3 | `03-data-flow.mmd` | Sequence diagram: the #1 user action end-to-end | Always |
| 4 | `04-erd.mmd` | ER diagram: tables/collections and relationships | If any data layer exists |
| 5 | `05-request-lifecycle.mmd` | Flowchart: HTTP request path through middleware/handlers | If it's a server |
| 6 | `06-deployment.mmd` | Flowchart: where each piece runs (Vercel, Docker, AWS…) | If infra config exists |

Rules for every diagram (details in the reference file):

- **Max ~12 nodes.** If more, split into two diagrams or zoom out.
- **Label edges with verbs**: "saves order to", "asks for prices", not bare arrows.
- **Plain-English node names**: "Payments (handles Stripe)" not `stripe_svc`.
- Every `.mmd` file starts with a `%% caption:` comment — one sentence a non-coder
  understands. The renderer puts it in the PDF.

### Phase 4 — Render to PNG + PDF

```bash
python3 <skill-dir>/scripts/render_diagrams.py docs/architecture
```

The script renders every `src/*.mmd` to `diagrams/*.png` and bundles them with their
captions into `architecture.pdf`. It tries `mmdc`, then `npx @mermaid-js/mermaid-cli`,
then falls back to a self-contained `architecture.html` (open in browser → Print → PDF)
if node is unavailable. Report which path it took. If only HTML fallback worked, tell
the user exactly: "open docs/architecture/architecture.html and print to PDF".

Verify: list the produced files and check PNGs are non-zero size before claiming success.

### Phase 5 — Write ARCHITECTURE.md (for the human)

Follow `references/architecture-md-template.md`. Non-negotiables:

- Open with "What is this app?" — one paragraph, zero jargon.
- Embed each PNG (`![...](diagrams/01-system-overview.png)`) followed by a
  "What you're looking at" paragraph in plain English.
- Include a "House tour" section: each top-level folder explained with a real-world
  analogy (e.g. "`api/` is the reception desk — every request from the outside world
  arrives here first").
- Include "Where to look when…" table: symptom → folder/file (e.g. "button text wrong →
  `src/components/`", "payment failing → `api/payments.py`").
- No sentence should require programming knowledge to parse. If a technical term is
  unavoidable, define it inline in parentheses the first time.

### Phase 6 — Write AI-CONTEXT.md (for future agents)

Follow `references/ai-context-template.md`. This is the opposite register: dense,
structured, no prose padding. It must contain everything a fresh agent session needs:

- One-line purpose, stack list, entry points, run/build/test commands
- Directory map with one-line role per folder
- Data model summary (tables, key fields, relations) in compact form
- API surface list (method + path + purpose)
- External services + which env vars they need
- Conventions found in the code (naming, patterns, state management)
- Digest of any existing CLAUDE.md / AGENTS.md / cursor rules found in Phase 1
- Pointer to the `.mmd` sources so the agent can read diagrams as text

End it with: "Regenerate with the explain-architecture skill after major changes."

### Phase 7 — Report

Tell the user:
1. What the app is (one sentence — proves you understood it).
2. Files produced, with the PDF path highlighted.
3. How to reuse `AI-CONTEXT.md`: paste it into any agent (Claude Code, Codex, Gemini
   CLI) at session start, or reference it from `CLAUDE.md` / `AGENTS.md` /
   `GEMINI.md` with one line: `Read docs/architecture/AI-CONTEXT.md first.`
4. Offer to add that pointer line to their agent memory file now.

## Guardrails

- Never invent architecture. If you didn't see it in the code, it doesn't go in a
  diagram. Mark genuine uncertainty: "(likely — inferred from config)".
- Secrets: never copy values from `.env` or config into any output. Names of env vars
  are fine; values never.
- If the repo is tiny (<10 source files), skip diagrams 2/5/6 and say why — don't pad.
- If diagrams would exceed ~12 nodes, split rather than shrink text.
- Re-runs must overwrite `docs/architecture/` cleanly — it is generated output.
