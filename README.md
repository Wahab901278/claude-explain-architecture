# explain-architecture

A Claude Code skill/plugin that reads your **whole codebase** and explains its
architecture **visually** — built for vibe-coders who build with AI but can't read
code fluently.

Say *"explain the architecture of this codebase"* and get, in `docs/architecture/`:

| Output | For |
|---|---|
| `architecture.pdf` + `diagrams/*.png` | You — system overview, module map, data flow, ERD, request lifecycle, deployment diagrams |
| `ARCHITECTURE.md` | You — plain-English walkthrough, "house tour" of every folder, "where to look when…" table |
| `AI-CONTEXT.md` | Your AI agents — dense project brief; paste into any fresh session (Claude Code, Codex, Gemini CLI) for instant project understanding |
| `src/*.mmd` | Editable Mermaid diagram sources |

## Install

### Claude Code — plugin (recommended)

```
/plugin marketplace add Wahab901278/claude-explain-architecture
/plugin install explain-architecture@explain-architecture-marketplace
```

### Claude Code — manual

```bash
git clone https://github.com/Wahab901278/claude-explain-architecture.git
mkdir -p ~/.claude/skills
cp -r claude-explain-architecture/skills/explain-architecture ~/.claude/skills/
```

Or per-project: copy into `<your-repo>/.claude/skills/` instead.

### Codex CLI

```bash
git clone https://github.com/Wahab901278/claude-explain-architecture.git
mkdir -p ~/.codex/skills
cp -r claude-explain-architecture/skills/explain-architecture ~/.codex/skills/
```

Or add one line to your repo's `AGENTS.md`:
```
For architecture explanations, follow <path>/skills/explain-architecture/SKILL.md
```

### Gemini CLI

Add the same pointer line to `GEMINI.md`, or paste `SKILL.md` into the prompt.

### Rendering requirements (optional)

PNG/PDF rendering needs any ONE of:

```bash
npm install -g @mermaid-js/mermaid-cli   # best
# — or nothing: with node installed, npx fetches it on demand
# — or nothing at all: falls back to an HTML file you print to PDF
pip install pillow                        # enables direct PDF assembly
```

The renderer auto-detects your installed Chrome/Chromium/Edge/Brave — no extra
browser download needed.

## Use

In any project:

> explain the architecture of this codebase

The skill scans strategically (manifests, entry points, migrations, routes — not
every file), draws Mermaid diagrams under strict readability rules (max 12 nodes,
verb-labeled arrows, plain-English names), renders them to PNG + one PDF, and writes
the two docs.

## Reuse the output — give any agent instant project knowledge

Add one line to your `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`:

```
Read docs/architecture/AI-CONTEXT.md first.
```

Every future agent session starts already knowing your stack, folder roles, data
model, API surface, and conventions — no re-exploring, fewer tokens, fewer wrong
guesses. Re-run the skill after big changes; it regenerates `docs/architecture/`
cleanly.

## Structure

```
.
├── .claude-plugin/
│   ├── plugin.json               # Claude Code plugin manifest
│   └── marketplace.json          # lets /plugin marketplace add work on this repo
├── skills/explain-architecture/
│   ├── SKILL.md                  # the skill: 7-phase workflow
│   ├── scripts/render_diagrams.py# .mmd -> PNG + PDF (mmdc / npx / HTML fallbacks)
│   └── references/
│       ├── diagram-patterns.md           # which diagram when + style rules
│       ├── architecture-md-template.md   # human doc template
│       └── ai-context-template.md        # agent doc template
└── README.md
```

## License

MIT
