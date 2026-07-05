# Template — AI-CONTEXT.md (the agent-facing document)

Register: dense, structured, factual. No analogies, no prose padding. This file is
pasted into fresh agent sessions (Claude Code, Codex, Gemini CLI) to give instant
project understanding. Optimize for tokens: tables and terse lines over paragraphs.
Replace «guillemets»; drop sections that don't apply. Never include secret VALUES —
env var names only.

---

# AI Context: «project name»

> Machine-oriented project brief. Generated «date» by explain-architecture skill.
> Diagram sources (readable as text): `docs/architecture/src/*.mmd`.
> Regenerate with the explain-architecture skill after major changes.

## Purpose
«One line: what the app does and for whom.»

## Stack
«Comma list: language(s) + versions, framework, DB, key libs, package manager,
deploy targets.»

## Commands
```bash
# install:  «cmd»
# dev:      «cmd»
# build:    «cmd»
# test:     «cmd»
# lint:     «cmd»
# migrate:  «cmd»
```

## Entry points
- «`path` — what starts here (server boot / CLI / cron)»

## Directory map
| Path | Role |
|---|---|
| «`api/`» | «HTTP routes; FastAPI; one file per resource» |
| … | … |

## Data model
«One line per entity: `User(id, email, name) 1-* Order(id, user_id, status, total) 1-* OrderItem`.
Note ORM + where schema lives. Full ERD: `src/04-erd.mmd`.»

## API surface
| Method | Path | Purpose |
|---|---|---|
| «POST» | «/v1/messages» | «main chat completion endpoint» |
| … | … | … |

## External services
| Service | Used for | Env vars (names only) |
|---|---|---|
| «Stripe» | «payments» | «STRIPE_SECRET_KEY» |

## Conventions observed
«Bullets: naming patterns, error-handling style, state management, test layout,
where new code of each kind goes. Only what's actually consistent in the code.»

## Pre-existing agent instructions (digest)
«Summarize any CLAUDE.md / AGENTS.md / GEMINI.md / .cursorrules found. Quote hard
rules verbatim; note file of origin. If none: "None found."»

## Known sharp edges
«Bullets: fragile files, ordering requirements, TODO/HACK/FIXME hotspots, things
that MUST run before others (migrations, codegen).»
