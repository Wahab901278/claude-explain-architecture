# Template — ARCHITECTURE.md (the human-facing document)

Register: friendly explainer. Zero unexplained jargon. Analogies over abstractions.
Replace everything in «guillemets»; drop sections that don't apply.

---

# «Project name» — How it works

*Generated «date» by the explain-architecture skill. Diagrams: `diagrams/` (PNG),
`architecture.pdf` (all-in-one), `src/` (editable sources).*

## What is this app?

«One paragraph. What it does for its users, in words you'd use at dinner.
No stack names in the first sentence.»

**Built with:** «stack, one line, each term glossed: "Next.js (the framework that
builds the web pages), Postgres (the database)…"»

## The big picture

![System overview](diagrams/01-system-overview.png)

**What you're looking at:** «2–4 sentences. Walk left to right: the user does X,
which travels to Y, which stores/fetches Z. Name what's yours vs rented
(third-party services).»

## House tour — what each folder is for

![Module map](diagrams/02-module-map.png)

«One bullet per top-level folder, each with a real-world analogy:»

- **`api/`** — the reception desk. Every request from the outside world arrives here
  first and gets routed to the right department.
- **`core/`** — «analogy»
- …

## Following one action through the app

![Data flow](diagrams/03-data-flow.png)

**What you're looking at:** «Narrate the sequence diagram as a story, step by step.
"When you hit Send: (1) the app packages your message… (2)…"»

## What the app remembers (the database)

![ERD](diagrams/04-erd.png)

**What you're looking at:** «Each box is like a spreadsheet. Explain the 2–3 most
important relationships in words: "Every Order belongs to one User; one User can
have many Orders."»

## «Optional: The checkpoints every request passes» 

![Request lifecycle](diagrams/05-request-lifecycle.png)

«Narrate: bouncer (auth) → form check (validation) → the actual work.»

## «Optional: Where it all runs»

![Deployment](diagrams/06-deployment.png)

«Which pieces run where, what each hosting service is, roughly what happens if one
goes down.»

## Where to look when…

| You want to… | Go to |
|---|---|
| «Change what a page looks like» | «`src/components/` — the visual building blocks» |
| «Change what happens on submit» | «file» |
| «See/-change what data is stored» | «file» |
| «Fix "payment failed"» | «file» |
| «Change an email the app sends» | «file» |

## Things to be careful with

«3–6 bullets: the load-bearing walls. Files where a small change breaks a lot,
env vars that must exist, external services that cost money per call, anything
marked TODO/HACK/FIXME that looked scary. Honest, specific, no fearmongering.»

## Words used in this codebase

«Mini-glossary of project-specific terms an AI or the code uses: "provider = one of
the 22 AI services the proxy can route to", etc. 5–10 entries max.»

---

*To give any AI coding agent instant understanding of this project, paste
`AI-CONTEXT.md` (same folder) at the start of a session.*
