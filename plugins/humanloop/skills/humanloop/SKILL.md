---
name: humanloop
description: Pause agent execution to have the human validate decisions, choose between options, or answer freetext — via the `hl` CLI, which blocks on an interactive TUI and returns answers as JSON. Use for material design decisions, approval gates, and picks between meaningful alternatives. Not for trivial yes/no confirmations the agent should decide itself.
allowed-tools: Bash(hl:*), Write, Read
---

# humanloop — Human-in-the-Loop Decision Skill

Use the `hl` CLI to ask the human a structured set of questions and block until they answer. It opens a TUI (auto-splits a tmux pane when `$TMUX` is set), persists progress to disk, and returns JSON.

## When to use this

Reach for `hl` when the next step materially depends on a human judgment you cannot make alone:

- **Design decisions** with real tradeoffs (Postgres vs SQLite, library choice, data model).
- **Approval gates** before an irreversible or expensive action (schema migration, mass refactor, deploy).
- **Picks between alternatives** where you have 2+ reasonable options and no strong reason to prefer one.
- **Batches of 2+ structured questions**. For a single freetext question, ask inline — `hl` is for batched, structured review.

## When NOT to use this

- Trivial yes/no the agent should answer itself (e.g. "should I write tests?" — yes).
- Questions with obvious correct answers given the code and context.
- Routine confirmations (Claude Code already prompts for destructive tool calls).
- Single freetext questions where a chat reply is lower friction.

## Audience and content philosophy

The deck is read by a busy, technical human. Write with **progressive disclosure** so the reader can stop at any layer:

| Field | Role | Guidance |
|-------|------|----------|
| `title` | Inbox label | Noun-phrase topic (≤4 words). The *thing* being decided, not the decision. `Database`, not `Use Postgres`. |
| `subtitle` | TL;DR | One plain-English sentence framing the choice or stakes. Action-ready if the call is obvious. No jargon, no library names without context. |
| `body` | ELI12 explanation | Plain language up top — audience is a smart engineer joining the codebase. Tuck anything denser (technical specifics, alternatives considered, edge cases) under a heading like `## Details` or `## Alternatives` so the reader can skip past. Every layer below the TL;DR is optional reading. |
| `options[]` | Genuine alternatives | Two or more real picks. Empty array = freetext-only. |
| `allowFreetext` | Comment + escape hatch | Set true when you want a comment alongside a choice, or to let the human write their own answer. |

**Avoid**: walls of jargon, raw schema dumps or stack traces in `body`, titles that bury the topic, subtitles that restate the title, options that are not real alternatives.

## Workflow

1. Write a deck JSON file matching `hl schema`.
2. Run `hl create <file>`. Blocks on the TUI; prints a JSON result on success.
3. Parse the output. Match answers to questions by `id` — **never by index**, since the human can skip questions.
4. Act on the answers.

## Input example (pyramid content)

```json
{
  "title": "Capture pipeline decisions",
  "interactions": [
    {
      "id": "db",
      "title": "Database",
      "subtitle": "Postgres or SQLite for the new capture store?",
      "body": "Two services will write at the same time, which is the crux.\n\nPostgres handles concurrent writes natively. SQLite serializes them — fine at low traffic, but we expect bursts.\n\n## Details\nSQLite WAL still serializes writers; Postgres uses MVCC.",
      "options": [
        {"id": "pg", "label": "Postgres"},
        {"id": "sqlite", "label": "SQLite"}
      ],
      "allowFreetext": true
    },
    {
      "id": "retry",
      "title": "Retry policy",
      "subtitle": "How aggressively should we retry publish failures?",
      "body": "Affects the reliability budget. Too aggressive and we hammer downstream during outages; too lax and transient blips become user-visible.",
      "options": [],
      "allowFreetext": true
    }
  ]
}
```

## Output shape

```json
{
  "responses": [
    { "id": "db", "selectedOptionId": "pg", "freetext": "Yes — concurrent writes are non-negotiable" },
    { "id": "retry", "freetext": "Exponential backoff capped at 5 attempts, then DLQ" }
  ],
  "completedAt": "2026-04-20T15:23:00.000Z"
}
```

- `selectedOptionId` is present when the human picked one of the listed options.
- `freetext` is present when the human typed a comment or freetext answer.
- The human **can skip questions** — `responses` may be shorter than `interactions`. Always look up by `id`.

## Invocation

```
hl create deck.json                     # block, print JSON to stdout
hl create deck.json --output ans.json   # write JSON to file instead
hl create deck.json --no-visuals        # skip haiku-generated visual context (faster)
hl create deck.json --no-tmux           # force TUI in current pane inside tmux
hl schema                               # print the input JSON schema
```

Typical end-to-end flow:

```bash
# 1. Write the deck
cat > /tmp/d.json <<'EOF'
{"interactions":[{"id":"x","title":"Database",
 "subtitle":"Postgres or SQLite for the capture store?",
 "body":"Concurrent writes are the crux. Postgres handles them natively; SQLite serializes.",
 "options":[{"id":"pg","label":"Postgres"},{"id":"sqlite","label":"SQLite"}],
 "allowFreetext":true}]}
EOF

# 2. Block on the TUI, capture JSON
hl create /tmp/d.json > /tmp/answers.json

# 3. Look up the answer by id
jq '.responses[] | select(.id=="x")' /tmp/answers.json
```

## Key behaviors

- **tmux auto-split.** When `$TMUX` is set, the TUI opens in a new pane to the right; the caller keeps focus. Disable with `--no-tmux`.
- **Progress persistence.** Responses are atomically written to `<file>.progress.json` after every change. If the process is killed, the next `hl create <file>` resumes from where the human left off. The progress file is deleted on full completion; partial files are preserved.
- **Visual context.** With a session id (auto-detected from the most recent Claude Code session in cwd, or pass `--session-id`), Haiku generates a short ANSI context block per interaction grounded in the conversation history. Disable with `--no-visuals`.

## Exit codes

- `0` — success; JSON emitted to stdout or the file passed to `--output`.
- `1` — error on stderr. Common causes: missing file, invalid JSON, empty `interactions` array, no TTY. The error message enumerates the fix.

If the caller captures stdin and the TUI cannot attach, run inside tmux so `hl` can auto-dispatch to a new pane.

## Authoring tips

- **Minimize questions.** Every question costs the human's attention. Ask only what materially changes the next step.
- **Title = topic, not decision.** `Database` ✓, `Use Postgres` ✗. Helps the human scan the inbox.
- **Subtitle is the TL;DR.** If the reader stops here, can they still act? If not, rewrite.
- **Body is ELI12, not engineer-to-engineer.** The reader is technical and can connect dots — do not dump jargon. Push denser material below a `## Details` (or `## Alternatives`) heading so it is skippable.
- **Give real options.** Options should be genuine alternatives, not one real answer and filler.
- **Keep ids short and meaningful.** They show up in the code reading the answers back.
