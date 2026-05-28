---
name: humanloop
description: Pause agent execution to have the human validate decisions, choose between options, answer freetext, or comment on a document — via the `hl` CLI. Every interaction is a kickoff that returns a job handle immediately; collect the human's answer later with `hl job result`. Use for material design decisions, approval gates, picks between meaningful alternatives, and markdown doc review. Not for trivial yes/no confirmations the agent should decide itself.
allowed-tools: Bash(hl:*), Write, Read
---

# humanloop — Human-in-the-Loop Decision Skill

Use the `hl` CLI to ask the human a structured set of questions (a *deck*) or get freeform comments on a markdown doc (a *review*). It opens a TUI (auto-splits a tmux pane when `$TMUX` is set), persists progress to disk, and returns JSON.

Every interaction is a **kickoff**: the launch call (`hl deck ask`, `hl review open`) spawns the human's TUI in a detached pane and returns a `job_id` in well under a second — it does *not* wait for the human. You collect the answer separately with `hl job result`. See **[Long-running: kick off, then collect](#long-running-kick-off-then-collect)** — this is the single most important thing to get right, because a human may take many minutes or step away entirely.

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

Every leaf reads **one JSON object from stdin** and writes one JSON object to stdout. There are no file-path arguments — pipe the input in.

1. Build the deck object (see the example below); validate it with `hl deck validate` if unsure.
2. **Kick off:** `echo '{"deck":{…}}' | hl deck ask` → returns `{job_id, dir, follow_up}` immediately. The human's TUI is now open in a pane; you are *not* blocked.
3. **Collect** (see [Long-running](#long-running-kick-off-then-collect)): `echo '{"job_id":"…","wait":true}' | hl job result` blocks until the human finishes, then prints the resolution. Run this **backgrounded**.
4. Parse the output. Match answers to questions by `id` — **never by index**, since the human can skip questions.
5. Act on the answers.

## Long-running: kick off, then collect

The human is slow and may walk away. Treat every interaction as fire-and-forget plus a deferred collect:

- **`hl deck ask` and `hl review open` return in <1s** with a `job_id`. They never wait for the human. The `follow_up` string in their output tells you the exact collect call.
- **Collect with `hl job result`** + `{"wait":true}`. This is the call that blocks until the human finishes (or `{"wait":false}` to poll once — returns `{error:"not_ready"}` exit 1 if they're not done).
- **Run the waiting collect as a backgrounded task — do not await it inline.** In Claude Code, set the Bash call to `run_in_background`; you will be notified when it completes, and you stay free to do other work meanwhile. Blocking the foreground on a human who might take 20 minutes (and overrunning the 10-minute command ceiling) is the failure this design exists to prevent.
- **Inspect without collecting:** `hl job status` → `{state: live|done|failed|canceled, kind, age_seconds, last_event}`. `hl job logs` streams JSONL events. `hl job cancel` is best-effort.
- **Mid-flight edits:** while a deck job is live, `hl deck update` rewrites its questions and the pane reloads within ~1s (answers to surviving ids are kept).

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

`hl job result` for a deck job returns a resolution envelope; the `responses` array is what you act on:

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

Every leaf is `hl <noun> <verb>`, reads one JSON object on stdin, writes one on stdout. `-h` on any node is the full spec.

```bash
# Deck (structured questions)
echo '{"deck":{…}}'                | hl deck ask        # kickoff → {job_id, dir, follow_up}
echo '{"deck":{…}}'                | hl deck validate   # preflight, no side effects
echo '{"job_id":"…","deck":{…}}'   | hl deck update     # rewrite a live deck; pane reloads

# Review (markdown doc feedback)
echo '{"file":"/abs/doc.md"}'      | hl review open     # kickoff → {job_id, output, follow_up}

# Collect / inspect any job
echo '{"job_id":"…","wait":true}'  | hl job result      # block for the human, then print result
echo '{"job_id":"…"}'              | hl job status      # state snapshot, never blocks
echo '{"job_id":"…","follow":true}'| hl job logs        # stream JSONL events

echo '{"kind":"deck"}'             | hl schema show     # JSON Schema for an input type
```

Typical end-to-end flow:

```bash
# 1. Kick off — returns immediately with a job_id
JOB=$(echo '{"deck":{"interactions":[{"id":"db","title":"Database",
  "subtitle":"Postgres or SQLite for the capture store?",
  "body":"Concurrent writes are the crux. Postgres handles them natively; SQLite serializes.",
  "options":[{"id":"pg","label":"Postgres"},{"id":"sqlite","label":"SQLite"}],
  "allowFreetext":true}]}}' | hl deck ask | jq -r .job_id)

# 2. Collect — BACKGROUND this (the human may take many minutes)
echo "{\"job_id\":\"$JOB\",\"wait\":true}" | hl job result > /tmp/answers.json

# 3. Look up the answer by id
jq '.responses[] | select(.id=="db")' /tmp/answers.json
```

## Key behaviors

- **tmux auto-split.** When `$TMUX` is set, the TUI/editor opens in a detached pane; the caller keeps focus and returns immediately. Pass `{"tmux":false}` to force the current pane (degraded: the launch call then blocks in-process).
- **Files are the source of truth.** Each job lives in its own dir (`dir` in the kickoff output): `deck.json`/`review.vim`, the live `progress.json`/autosaved feedback, the terminal `response.json`/`feedback.json` sidecar, and `job.log` (JSONL). A killed job is recoverable — re-collect by `job_id`; appearance of the sidecar is the done signal.
- **Review live-reloads.** `hl review open` opens the doc read-only; if the file is rewritten on disk while the human reviews, the pane reloads it automatically (their line-anchored comments are kept). Edit the doc and they see the latest without reopening.
- **Visual context (deck).** With a session id (auto-detected from the most recent Claude Code session in cwd, or pass `sessionId`), Haiku generates a short ANSI context block per interaction. Pass `{"visuals":false}` to skip it.

## Exit codes

- `0` — success; one JSON object (or JSONL for `job logs`) on stdout.
- non-zero — error as a JSON object on stdout: `{error, message, next}`. Codes: `bad_stdin_json | bad_input | deck_invalid | file_not_found | editor_not_found | job_not_found | not_ready | not_in_tmux | internal`. `next` tells you how to recover.

If the launch call can't open a pane (no `$TMUX`), it falls back to running in-process and blocks; run inside tmux so it can auto-dispatch to a new pane and return immediately.

## Authoring tips

- **Minimize questions.** Every question costs the human's attention. Ask only what materially changes the next step.
- **Title = topic, not decision.** `Database` ✓, `Use Postgres` ✗. Helps the human scan the inbox.
- **Subtitle is the TL;DR.** If the reader stops here, can they still act? If not, rewrite.
- **Body is ELI12, not engineer-to-engineer.** The reader is technical and can connect dots — do not dump jargon. Push denser material below a `## Details` (or `## Alternatives`) heading so it is skippable.
- **Give real options.** Options should be genuine alternatives, not one real answer and filler.
- **Keep ids short and meaningful.** They show up in the code reading the answers back.
