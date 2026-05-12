---
name: cli-design
description: Design CLIs for humans and LLM agents — subcommand shape, output streams, exit codes, JSON modes, TTY-aware color, structured errors, mutation safety. Use when building or refactoring a CLI, adding machine-readable output, writing --help, deciding stdout vs stderr, or making a tool agent-friendly.
---

# CLI Design

A CLI has two readers now: the human typing at a prompt and the LLM agent invoking it from a shell tool. Most production CLIs were designed only for the first, and the failure modes diverge sharply once an agent starts calling them. The `--help` text is the agent's tool description. The output format is the response schema. Exit codes are error codes. Designed poorly, a CLI costs an agent roughly 35× the tokens of a well-designed one on equivalent workflows (MindStudio, measured against MCP equivalents) — and that's before the agent burns retries on errors it can't parse.

The good news: most of the rules that make a CLI agent-friendly also make it script-friendly and pipeline-friendly. The Unix philosophy and agent-friendliness converge on the same answers. The mistakes are specific and well-cataloged.

For tool-specific patterns, principle citations, and a long-form anti-pattern catalog with GitHub issues, see [reference.md](reference.md).

## The Two-Reader Lens

Every output path on every command should have a default human form and a machine form available on demand. Don't pick one — design both.

Where the split shows up:

- **Output format**: `git status` for humans, `git status --porcelain` for scripts. Human format can evolve between versions; porcelain format is a versioned contract.
- **Color**: enabled in a TTY, automatically disabled when stdout is piped. Respect `NO_COLOR=1`; honor `FORCE_COLOR=1` as the override.
- **Prompts**: only when stdin is a TTY. In non-TTY contexts, fail with instructions or honor `--yes` / `--non-interactive`. A CLI that prompts in a pipe hangs an agent indefinitely — this is the single most common production break.
- **Progress**: spinners and bars in a TTY, nothing when piped. Or always to stderr, so capture is clean.

The cost of getting this wrong is concrete and well-documented. A CLI that emits ANSI in pipes corrupts downstream `grep`. A CLI that prompts in a non-TTY hangs CI and agent workflows. A CLI that decorates JSON output with table borders is unparseable. These bug reports exist against npm, yarn, AWS CLI, Claude Code, codex — every project relearns the lesson.

## Stream Discipline

**stdout is data the caller wants to capture. stderr is everything else.**

Progress, warnings, "fetching...", success confirmations — all stderr. The contract: `sis list -j | jq` should produce clean JSON even when the daemon prints "connecting to socket..." along the way. The diagnostic test: `cmd > /dev/null` should hide nothing the user wanted to see, and `cmd 2>/dev/null` should hide all decoration.

The Rule of Silence applies: when a command succeeds and has nothing useful to print, say nothing. "✓ Task completed" on stdout is decorative and breaks composition. Modern dev tools relax this for friendliness — fine, but route the friendly message to stderr.

## Machine Output Is a Contract

The moment you ship `--json` or `--porcelain`, the shape is a versioned API. Renaming a field breaks every script in the wild — and every agent that learned to parse it.

- **Include a `schema_version` field** (or use a versioned flag like `--porcelain=v2`, the way git does). Callers can branch on it; you can evolve safely.
- **Prefer JSONL for streams.** One complete JSON object per line. Partial reads don't break parsing, no closing bracket to wait for, cheaper to consume in pieces. Use a JSON array only when the entire result is bounded and small.
- **Make output deterministic.** Sort by a stable field; same input, same output. Random ordering or embedded timestamps break diffs and caching.
- **Field selection beats post-filtering.** `gh pr list --json number,title` is leaner than `--json '*' | jq '{number,title}'`. Save the caller a step and save tokens — agents pay per byte.
- **In `--json` mode, errors are structured too.** `{"error":"validation_failed","code":"INVALID_EFFORT","message":"...","valid_values":[...]}`. Agents branch on the code; humans read the message.

## Errors as Road Signs

An error is feedback the caller uses to correct itself. An opaque error produces retry loops; a road sign produces recovery. Every error needs three pieces: what was received, what was expected, and what to do next.

```
# Useless — agent loops on the same call
Error: invalid argument

# Recoverable — exact fix is implied
Error: --effort must be one of: low, medium, high, xhigh (got: 'xmedium')

# Recoverable with a path
Error: deck file not found: ./questions.json
       Pass an absolute path, or run from the directory containing the file.
```

Exit codes are the second channel. **0 on success, non-zero on any failure** is universal. Beyond that, document any specific codes the caller should branch on: `git diff` exits 1 to signal "differences exist" (a useful condition, not an error). Don't invent codes unless callers will branch on them — most CLIs need only `0` and `1`. If you do specialize, write them down: `2` for usage error, `5` for conflict, `127` for not-found are the conventional choices.

## Command Shape

Past about seven top-level verbs, organize them. Three shapes work; mixing them doesn't.

- **Flat verbs** (`tar`, `curl`, `rg`, `jq`): fast to type, breaks down past ~10 commands. Right for a focused tool with one purpose.
- **Verb-noun** (`kubectl get pods`, `cargo build`): predictable when the same verbs apply to many objects. The shape is exploration-friendly — knowing `kubectl get` predicts that `kubectl describe` and `kubectl delete` exist. For agents, this is deterministic tree search through `--help`.
- **Noun-verb** (`docker container create`, `gh pr list`): better when objects have many distinct operations that don't share verbs across types. Pairs naturally with `--json field,field` projections.

Pick one and apply it uniformly. The worst CLIs mix shapes (`tool deploy --app foo` next to `tool config set key val` next to `tool users list`). Be deliberate about aliases — `npm install`, `npm add`, `npm i` look helpful in isolation but force scripts and agents to remember three names for one operation. Pick the canonical name and document the others as aliases, not equals.

## Inputs: Flags, Environment, Stdin

The standard precedence is **flags > env vars > project config > user config > defaults**. Flags always win, so scripts can inject overrides without touching state.

A few rules with sharp edges:

- **Accept stdin when content is the natural input.** Long prompts, file contents, queries. By convention, a bare `-` as a positional argument means "read from stdin"; pair it with an explicit `--stdin` flag when ambiguity matters.
- **Never accept secrets via flags.** `ps aux` reveals them; shell history saves them. Use `--password-file`, stdin, or a credentials file.
- **Respect standard env vars.** `NO_COLOR`, `FORCE_COLOR`, `PAGER`, `EDITOR`, `XDG_*`, `TMPDIR`. Don't reinvent these.
- **Don't smuggle state across invocations.** If `cmd-a` writes to `~/.cache/tool/state` and `cmd-b` silently depends on it, agents calling `cmd-b` in a fresh shell will fail. Pass state explicitly.

## Mutation Safety

For destructive or expensive operations, separate preview from execution. The pattern compounds: it makes agents safer (they can plan before acting) and humans saner (no surprise commits).

- **`--dry-run` for "show what would happen."** Should be cheap, side-effect-free, and structurally identical to the real run.
- **Plan/apply for complex changes.** `terraform plan -out=file` saves a plan; `terraform apply file` executes exactly that plan. No drift between preview and execute.
- **Confirmation prompts only in a TTY.** In non-TTY, require `--yes` or fail. Never assume.
- **Idempotency wherever possible.** Running `apply -f config.yaml` twice should converge to the same state as once. This is more valuable than perfect rollback.

## Help Is the Tool Description

For agents, `--help` is the only documentation that reliably gets read. Treat it the way you would a function description in a tool schema.

- **Lead with one-line examples** before formal option descriptions. Models pattern-match on examples to construct calls correctly — this is the CLI analog of `input_examples` in tool schemas.
- **Show the output shape.** When a command produces structured data, say so: "Output: JSON array of `{id, name, status}` objects."
- **Cross-reference related commands.** "See also: `sis status` for live state." Helps both humans and agents discover the right command.
- **Make it reachable two ways**: `cmd --help` and `cmd help <sub>`. Both are common patterns and cheap to support.

## Anti-Patterns to Memorize

Each of these is a real production bug, repeatedly:

- **Color in pipes** — ANSI escapes leak when stdout isn't a TTY. Detect or honor `NO_COLOR`.
- **Prompt in non-TTY** — CLI hangs forever in CI and agents. Detect stdin TTY; fail or use `--yes`.
- **stdout pollution** — status messages or progress on stdout corrupts machine output. Move to stderr.
- **Decorated JSON** — table borders, prefixes, or ANSI inside `--json` output. Keep machine modes strictly plain.
- **Flag explosion** — 40-flag commands. Split into subcommands or split the tool.
- **Alias chaos** — same operation under three names. Pick one canonical, deprecate the rest.
- **Unstable JSON schema** — silent field renames between versions. Add `schema_version`; deprecate over releases.
- **Silent truncation** — output cut to terminal width when piped. Emit full data or fail loudly.
- **Pager in non-TTY** — `less` auto-launches when output is captured. Disable when stdout isn't a TTY.
- **Stack trace on stderr** — internal panic surfaces to users. Wrap with context; gate full trace behind `--debug`.
- **Smuggled state** — command B depends on `cd` or env from command A. Pass state explicitly.
- **Secrets in flags** — visible in `ps` and shell history. Use stdin or files.

For each anti-pattern with the GitHub issues that filed them and the canonical fix, see [reference.md](reference.md).
