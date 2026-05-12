---
description: Build/update a dense architectural context primer for a complex subsystem
argument-hint: <topic or feature description>
disable-model-invocation: true
---

Build or update a context primer at `.claude/commands/init-context/<topic>.md` and keep `.claude/commands/init-context.md` (the `/init-context` router) in sync. Target: $ARGUMENTS

## Step 1 — Inventory

Existing primers: !`mkdir -p .claude/commands/init-context && ls .claude/commands/init-context/ 2>/dev/null || echo "(none)"`

Current `init-context.md`: !`[ -f .claude/commands/init-context.md ] && cat .claude/commands/init-context.md || echo "(not yet present)"`

Repo top level: !`ls -d */ 2>/dev/null | head -30`

Stack manifests: !`ls package.json pnpm-workspace.yaml turbo.json pyproject.toml Cargo.toml go.mod Gemfile 2>/dev/null || echo "(none at root)"`

Recent activity (last 15 commits): !`git log --oneline -15 2>/dev/null || echo "(not a git repo)"`

Decide:
- **New topic** → pick a kebab-case filename
- **Update** → if the topic fuzzy-matches an existing primer, ask the user whether to update it or create a new one
- **Reject** → if the subsystem is small/self-evident/can be understood by reading code in <5 min, tell the user and stop. Primers are for *large, complicated, or unintuitive* systems where code alone doesn't reveal intent.

## Step 2 — Parallel exploration

Dispatch 4–8 `Explore` subagents in parallel via the Task tool. Partition by slice, not by directory. Suggested slices:

- **Entry points** — HTTP routes, CLI commands, cron, event handlers, public exports
- **Data model** — schemas, types, DB tables, key invariants
- **Control flow** — how a typical request/job traverses the system end-to-end
- **External integrations** — third-party APIs, queues, services, env vars
- **Tests** — what's tested reveals what's load-bearing
- **History** — recent `git log` for this area surfaces ongoing work and pain points
- **Cross-cutting** — auth, errors, logging, feature flags as they apply here

Each subagent must return: concrete `file:line` references, the *non-obvious* facts (skip what's obvious from filenames), naming conventions, gotchas. Reject vague summaries.

## Step 3 — Verify with the user

After synthesis, you should have a working hypothesis of **what this system does and why it exists**. Confirm it. Code reveals *what*; only the user reliably knows *why*.

Use the `AskUserQuestion` tool — it batches up to 4 questions with multiple-choice options, so the user answers fast without freetext fatigue. Frame each question as "here's my read; is this right?" with your best-guess option first.

Ask when unclear:
- Business purpose / problem solved / who depends on it
- Architectural decisions that look surprising in the code
- Ownership, deprecation status, expected scale
- Which of multiple plausible flows is the canonical one

Skip when:
- The answer is greppable (don't ask, just look)
- You're already confident — don't manufacture doubt
- The detail won't change what the primer says

Keep asking (batched) until you're confident. Never guess and never write assumptions into the primer — if a fact isn't confirmed by code or the user, it doesn't go in.

## Step 4 — Write the primer

Write `.claude/commands/init-context/<topic>.md` with the structure below. Every line carries weight — no narrative filler, no padding, no restating the obvious.

```markdown
---
description: Context primer for <topic>
---

# <topic>

## Purpose
Why this exists. The business problem it solves. Who depends on it. (1–3 tight paragraphs — this is what code can't tell you.)

## Architecture
Components and responsibilities. Data/control flow. Boundaries and seams.

## File map
| Path | Role |
|------|------|
| `src/foo/bar.ts` | … |

## Key concepts
Domain terms, invariants, non-obvious constraints. Define jargon.

## Entry points
Where work enters the system, with `file:line`.

## Gotchas
Non-obvious coupling. Things that look broken but aren't. Past footguns.

## Related
- `init-context/<other-topic>.md` — how they interact
```

Density rules:
- `file:line` references over prose
- Tables over paragraphs where structure fits
- Skip anything self-evident from a 30-second skim of the code
- No "this section will cover…" meta-commentary

## Step 5 — Update `init-context.md`

Maintain `.claude/commands/init-context.md` as the router. If absent or stale, write/rewrite it:

```markdown
---
description: Load architectural context for a topic
argument-hint: <topic or question>
---

Project context primers live in `.claude/commands/init-context/`. Pick the primer(s) most relevant to: $ARGUMENTS — read them, then proceed.

**These primers are memory, not source of truth.** The code is authoritative. Before acting on anything from a primer, verify against the current code. If you find a disparity — drift, renames, removed features, new behavior — aggressively update or prune the primer file, the same way you'd maintain a memory file. If the user's changes obsolete a primer section after you've used it, update it before ending the turn.

## Index

- `<topic>.md` — <short description, ~6–10 words>
- …
```

Add/refresh the index line for the topic you just wrote. Keep descriptions to one line each, consistent shape (noun phrase, present tense, no period).

## Constraints

- Only build primers for genuinely complex systems. Push back on trivial requests.
- Always verify the directory exists before writing.
- Always update both files in the same turn.
- If updating an existing primer, diff your draft against the current file and call out what changed and why before writing.
