# CLI Design Reference

Deep reference for principles, patterns, anti-patterns, and citations. Read this when SKILL.md has already named the decision and you need the supporting detail.

## Authoritative Sources

The CLI design canon is small and worth knowing by name.

- **POSIX Utility Conventions** ([spec](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)) — the 30-year foundation. Single-dash short flags, `--` ends options, `-` means stdin/stdout. Argument syntax (`-a -b -c` vs `-abc`). Bedrock.
- **GNU Coding Standards** ([CLI section](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html)) — POSIX plus long options, `--help` / `--version` requirement, `getopt_long` conventions.
- **clig.dev** — Command Line Interface Guidelines, the modern synthesis (2024 update). The most cited contemporary reference. Read it end-to-end if you're designing a real CLI.
- **The Art of Unix Programming, Eric S. Raymond** ([online](http://www.catb.org/esr/writings/taoup/html/)) — the Rule of Silence, Rule of Composition, Rule of Least Surprise. The philosophy layer.
- **Heroku CLI Style Guide** — pragmatic "human-first" CLI design. Self-contained binary, multi-platform, non-intrusive auto-update.
- **docopt** ([site](http://docopt.org/)) — usage strings as the contract. Read the philosophy even if you don't use the library; it influences how good `--help` text reads.

## Stream Contract Details

The data/diagnostics split is universal across Unix CLI design:

- **stdout**: results, query answers, structured data, the thing the user/script wants to consume.
- **stderr**: progress, warnings, errors, status, prompts, "wrote 3 files".
- **Exit code**: success/failure flag for the caller's branch.

The diagnostic test: redirecting stdout to a file should leave the user with exactly the data they wanted captured, and redirecting stderr to `/dev/null` should leave them with no decoration but still get the data.

Common violations:
- Progress bars on stdout (`tar -v`, some Python tools).
- "Successfully written to /tmp/foo" on stdout — should be stderr.
- Errors on stdout in `--json` mode (npm `--json` is the famous case; see [npm/cli#2150](https://github.com/npm/cli/issues/2150)).
- Diagnostics on stdout for MCP servers (breaks JSON-RPC; see [MCP stdout pollution](https://community.postman.com/t/mcp-server-stdout-pollution-causing-invalid-json-rpc-messages-in-claude-desktop/89753)).

## Exit Code Conventions

Universal: **0 = success, non-zero = failure**. Beyond that, code meaning is per-tool. Common conventions:

| Code | Meaning | Example |
|---|---|---|
| 0 | Success | Anything that worked |
| 1 | General error | Default failure code |
| 2 | Misuse / usage error | Bad flags, missing required args |
| 5 | Conflict / already-exists | `mkdir` on existing dir, `git push` rejected |
| 64-78 | `sysexits.h` codes | BSD convention, rarely used outside C |
| 126 | Permission denied | Command not executable |
| 127 | Command not found | Shell builtin convention |
| 128+N | Killed by signal N | `kill -9` produces 137 (128+9) |
| 130 | Interrupted (Ctrl-C) | SIGINT = signal 2, 128+2 |

`git diff` is the canonical "useful non-zero": exit 1 means "differences exist" (not an error condition; useful for `if`).

Don't invent new codes unless callers will branch on them. Document the ones you use in `--help`.

## Color and TTY Detection

The detection pattern, in any language:

```python
# Python
import sys, os
COLOR_ENABLED = (
    sys.stdout.isatty()
    and os.environ.get("NO_COLOR") is None
    and os.environ.get("TERM") != "dumb"
)
if os.environ.get("FORCE_COLOR") == "1":
    COLOR_ENABLED = True
```

```typescript
// Node
const COLOR_ENABLED =
  process.stdout.isTTY &&
  process.env.NO_COLOR === undefined &&
  process.env.TERM !== "dumb";
if (process.env.FORCE_COLOR === "1") COLOR_ENABLED = true;
```

Standard env vars to respect:
- `NO_COLOR` — set to anything disables color ([no-color.org](https://no-color.org/)).
- `FORCE_COLOR` — set to `1` forces color even in non-TTY contexts.
- `TERM=dumb` — disables anything beyond plain text.
- `CLICOLOR` / `CLICOLOR_FORCE` — BSD convention, used by some tools.

Flag overrides: `--color=auto|always|never` (the canonical form, used by `ls`, `grep`, `git`, `ripgrep`).

Color escape sequences: `\x1b[1m` bold, `\x1b[2m` dim, `\x1b[31m` red, `\x1b[32m` green, `\x1b[33m` yellow, `\x1b[36m` cyan, `\x1b[35m` magenta, `\x1b[90m` gray, `\x1b[0m` reset.

## Machine Output Formats

### `--json` (most common)

A JSON object or array on stdout. Typically a single line for streaming, or pretty-printed when explicitly requested. Conventions:

- One JSON document on stdout.
- Field names stable across versions, or include `schema_version`.
- Errors structured: `{"error": "code", "message": "...", "details": {...}}`.

Example (gh CLI): `gh pr list --json number,title,author` returns a JSON array; `--jq '.[] | select(.author.login == "foo")'` filters inline.

### `--porcelain` (git, derived from "git plumbing/porcelain")

Plain-text, machine-stable output. Version-suffixed when the format evolves: `--porcelain=v1`, `--porcelain=v2`. Same idea as `--json` but predates structured-data conventions.

Format example (`git status --porcelain=v1`):
```
 M README.md
?? new-file.txt
A  staged-file.txt
```

Two-character status codes in fixed columns. Trivially parseable.

### `--format` / `-o` (template-driven)

The caller specifies the output template. Examples:

- `docker ps --format "table {{.Names}}\t{{.Status}}"` — Go templates
- `kubectl get pods -o jsonpath='{.items[*].metadata.name}'` — JSONPath
- `kubectl get pods -o yaml | -o json | -o wide | -o name` — preset modes

More flexible than fixed `--json`, but harder to use correctly.

### JSONL (newline-delimited JSON)

One complete JSON object per line. Right for streams: agent output, event logs, anything unbounded.

```
{"event": "agent-spawned", "id": "agent-001", "ts": "2026-05-12T..."}
{"event": "agent-report", "id": "agent-001", "summary": "..."}
{"event": "agent-completed", "id": "agent-001"}
```

Each line is complete — partial reads don't break parsing. Cheaper than wrapping in an array (no buffering, no closing bracket). Tools that read this well: `jq -c`, Python `json.loads` per line, `awk`.

## Command Shape Reference

### Flat verbs

```
curl https://example.com
tar -xzf archive.tar.gz
rg "pattern" path/
jq '.users | map(.name)' data.json
```

Works for focused tools. Past ~10 verbs it becomes unmanageable.

### Verb-noun (kubectl, cargo)

```
kubectl get pods
kubectl describe deployment my-app
kubectl delete pod my-pod
cargo build
cargo test
cargo publish
```

Strong predictability: once you know the verbs, you predict the structure across all resource types. Good for tools where most operations apply to most objects.

### Noun-verb (docker, gh)

```
docker container run alpine
docker image build .
docker network create mynet
gh pr list
gh pr create
gh repo clone owner/name
```

Better when objects have distinct verbs that don't transfer ("repos have `clone`, PRs don't"). The shape implies hierarchy explicitly.

### Mixing (anti-pattern)

```
# tool's CLI evolved organically and mixes shapes:
mytool deploy --app foo     # verb action with flag-target
mytool config set key val   # noun-verb-args
mytool users list           # noun-verb (different convention!)
mytool start                # verb only
```

Pick one. Document the choice. Stick to it through future commands.

## Tool-Specific Patterns

### git: Plumbing vs Porcelain

Git distinguishes:
- **Plumbing** (low-level, stable): `git cat-file`, `git hash-object`, `git rev-parse`. Output format guaranteed stable.
- **Porcelain** (high-level, human-friendly): `git log`, `git status`, `git diff`. Output evolves between versions.

`--porcelain` flag on porcelain commands flips to machine output that's also stable. Format versioned (`--porcelain=v1`, `--porcelain=v2`) to allow evolution without breaking old scripts.

The split is the answer to "how do I keep human output evolvable while keeping scripts stable?" — separate the contract.

### gh (GitHub CLI): JSON Projection + Inline Filtering

```
gh pr list --json number,title,author
gh pr list --json number,title,author --jq '.[] | select(.author.login == "foo")'
gh pr list --json number --template '{{range .}}#{{.number}}\n{{end}}'
```

The pattern: `--json field1,field2` selects fields; `--jq` runs jq inline; `--template` runs Go templates inline. Avoids piping through `jq` separately (cheaper, fewer tokens for agents). `gh auth status` exposes a health-check pattern: prints credential state for inspection.

### kubectl: Verb-Noun + Output Modes

Strictly verb-noun: `kubectl get pods`, `kubectl describe deployment foo`. Resource types accept singular/plural/abbreviated (`pod`, `pods`, `po` are equivalent).

Output flags: `-o json | yaml | wide | name | custom-columns=... | jsonpath=...`. The same data, multiple shapes; caller picks.

Declarative vs imperative: `kubectl apply -f file.yaml` is idempotent; `kubectl create` is one-shot. `--dry-run=client` and `--dry-run=server` for preview.

### Terraform: Plan/Apply

```
terraform plan -out=plan.tfplan        # save plan
terraform apply plan.tfplan            # execute the saved plan
terraform plan -json                   # structured plan output
```

Plan is preview; apply executes. `-out` saves the plan as binary so `apply` can execute exactly that plan with no drift between preview and execution. `-json` output includes `format_version` so scripts can detect breaking changes.

### ripgrep, fd, fzf: Smart Defaults

These modern reimaginings invert the historical Unix tradition. Instead of plain output by default with flags to add features, they ship with sensible defaults and offer flags to tone them down:

- ripgrep: colors, filenames, line numbers by default. Respects `.gitignore`. `--smart-case`: case-insensitive unless query has uppercase.
- fd: same color and ignore defaults vs `find`'s plain output.
- fzf: interactive fuzzy finder with TTY-only behavior.

All auto-detect TTY and disable color when piped (`--color=auto` is the default).

### HTTPie: Friendly-by-Default

```
http GET https://api.example.com/users
echo '{"name":"x"}' | http POST https://api.example.com/users
```

JSON is the default content type for request/response (no flag needed). Output is colorized and indented in a TTY, plain when piped (`--pretty=auto`). Mode flags: `--pretty=all|colors|format|none`.

### Cargo: Verb-Based with Categories

```
cargo build           # build commands
cargo check
cargo test            # test commands
cargo publish         # publish commands
cargo add serde       # manifest commands
```

`cargo --help` groups verbs by intent. No nesting; subcommands are flat but categorized in help text.

## Configuration Layering

The standard precedence, highest to lowest:

1. **Command-line flags** — always win.
2. **Environment variables** — context-specific overrides.
3. **Project config** — `.env`, `package.json`, `pyproject.toml`, `.toolrc`.
4. **User config** — `~/.config/<tool>/config.{toml,yaml,json}` (XDG-friendly).
5. **System config** — `/etc/<tool>/`.
6. **Built-in defaults** — last resort.

XDG Base Directory: prefer `$XDG_CONFIG_HOME/<tool>/` (defaults to `~/.config/<tool>/`) over dotfiles. Prefer `$XDG_CACHE_HOME` and `$XDG_DATA_HOME` for cache and data.

Secrets never go in env vars or config files — they leak through `env`, logs, child processes. Use credential files (`~/.netrc`, `~/.aws/credentials`) or system keychains.

## Agent-CLI Economics

The token cost angle is concrete and measurable:

- **MCP vs CLI overhead** (MindStudio, production data): 93-tool MCP server injects ~55,000 tokens upfront; CLI equivalent ~1,365 tokens — a **35× overhead** before any work happens.
- **Reliability**: complex 5-step workflows ran at 100% via CLI; 72% via MCP.
- **Per-task cost** (Haiku pricing): well-designed CLI task ~1,000–3,000 tokens; verbose CLI ~5,000–10,000; unfiltered MCP 35,000+. For 50 tasks/session, the difference is $0.15 vs $5.25.

The cost drivers are decoration and unfilterable verbosity:
- ASCII tables with borders cost ~30% more tokens than equivalent JSON.
- ANSI escape codes that leak into capture: dead weight.
- Help text and tips appended to every command: dead weight.
- Default output that returns 20 fields when 3 are needed: dead weight.

Mitigation: ship `--json` with field projection (`--json field1,field2`), `--quiet` that means *quiet* (not "slightly less chatty"), and stable schemas.

## Anti-Pattern Catalog

### Color in Pipes

ANSI escapes leak into piped output. Downstream `grep` fails on multiline patterns; `less` displays garbage.

**Cause**: missing `isatty()` check, or color override flag broken.

**Filed against**: [Fedify CLI #257](https://github.com/fedify-dev/fedify/issues/257), [pino-pretty #231](https://github.com/pinojs/pino-pretty/issues/231), [yarn #5733](https://github.com/yarnpkg/yarn/issues/5733), [npm #7568](https://github.com/npm/npm/issues/7568), [nvm #2497](https://github.com/nvm-sh/nvm/issues/2497).

**Fix**: detect `isatty(stdout)` at startup; honor `NO_COLOR` and `FORCE_COLOR`; expose `--color=auto|always|never`.

### Interactive Prompt in Non-TTY

CLI prompts "Are you sure? [y/N]" and hangs forever in CI, agents, or `< /dev/null`.

**Cause**: prompt unconditionally; no `--yes` or `--non-interactive` fallback.

**Filed against**: [Claude CLI #9026](https://github.com/anthropics/claude-code/issues/9026), [codex #20919](https://github.com/openai/codex/issues/20919), [GitLab forum: non-TTY login](https://forum.gitlab.com/t/error-cannot-perform-an-interactive-login-from-a-non-tty-device/59936).

**Fix**: detect `isatty(stdin)`; if false, refuse with instructions or honor `--yes`. Use env var fallbacks (`CI=true` is common).

### stdout/stderr Confusion

Progress bars land on stdout, polluting JSON; errors land on stdout, hidden in normal output.

**Cause**: convenience — emit everything on stdout to keep the code simple.

**Filed against**: [npm #2150 (`--json` errors on stdout)](https://github.com/npm/cli/issues/2150), [Azure CLI #19365](https://github.com/Azure/azure-cli/issues/19365), [nerdctl #3772](https://github.com/containerd/nerdctl/issues/3772), [curl #12416](https://github.com/curl/curl/issues/12416), [MCP stdout pollution](https://community.postman.com/t/mcp-server-stdout-pollution-causing-invalid-json-rpc-messages-in-claude-desktop/89753).

**Fix**: data to stdout, everything else to stderr. Audit in `--json` mode especially.

### Decorated JSON

`--json` output includes ANSI escapes, leading prefixes, or trailing helpful tips.

**Cause**: shared output pipeline that decorates everything.

**Fix**: `--json` mode bypasses all decoration. Test: `cmd --json | python -c 'import sys,json; json.loads(sys.stdin.read())'` must succeed.

### Flag Explosion

Single command has 40 flags because every option got bolted on. Users can't discover functionality.

**Cause**: flat CLI structure; no commitment to subcommand organization.

**Examples**: AWS CLI v1 (criticized for this); contrast Azure CLI and kubectl which used subcommand structure.

**Fix**: introduce subcommand grouping; pick verb-noun or noun-verb; refactor over a deprecation cycle.

### Alias Chaos

`npm install` / `npm add` / `npm i` — three names for one operation. Scripts and docs reference different ones; tooling has to support all.

**Cause**: aliases added for convenience without deprecating the originals.

**Fix**: pick one canonical name. Aliases only for single-character shortcuts (`-i`). Document the canonical form everywhere.

### Unstable JSON Schema

Field names change in minor versions; scripts break.

**Cause**: no versioning policy; format treated as evolvable like human output.

**Examples**: [AWS CLI v1→v2 migration](https://docs.aws.amazon.com/cli/latest/userguide/cliv2-migration.html); [Azure CLI breaking changes](https://techcommunity.microsoft.com/blog/azuretoolsblog/azure-cli-breaking-change-pre-announcement/4403454).

**Fix**: include `schema_version` field. Deprecate old field names for 2+ releases before removal. Publish a schema changelog.

### Silent Truncation

Output cut off at terminal width when piped, or at internal limits. Data silently dropped.

**Examples**: [rtk #827 (LLM tool truncating diffs at 8K tokens)](https://github.com/rtk-ai/rtk/issues/827), [gemini-cli #5943 (conversation save/resume lossy)](https://github.com/google-gemini/gemini-cli/issues/5943), [OpenClaw #19239](https://github.com/openclaw/openclaw/issues/19239).

**Fix**: emit full output; if truncating is necessary, include a `"truncated": true` marker. Fail rather than drop silently.

### Pager Auto-Launch in Non-TTY

`less` opens when stdout isn't a TTY; CLI hangs waiting for keypress that never comes.

**Cause**: unconditional `exec less`.

**Fix**: only launch pager when stdout is a TTY *and* output exceeds screen height. Respect `PAGER` env var. Provide `--no-pager`.

### Stack Trace on Stderr

Internal panic surfaces as a Python/Node/Java traceback. User sees an "Error: KeyError: 'foo' at line 84 ..." they can't act on.

**Cause**: no error wrapping at the top level.

**Fix**: catch at the entry point; print a one-line human message to stderr; gate full traceback behind `--debug` or `--verbose`.

### Smuggled State

`cmd-a` writes to `~/.cache/tool/state`; `cmd-b` silently reads it. Agent calls `cmd-b` from a fresh shell and gets unexplained errors.

**Fix**: pass state explicitly via flags or stdin. State files are fine as a cache or convenience, but the CLI must work without them.

### Secrets in Flags

`tool deploy --password=hunter2` — visible in `ps aux`, saved to shell history.

**Fix**: accept secrets via `--password-file`, stdin, or system credential store. Document this in `--help`.

## Agent-Orchestration CLIs

CLIs in the agent-orchestration genre (Claude Code, aider, OpenHands, Goose, Cursor, sisyphus) face tensions absent from traditional CLIs.

### Long-running operations vs Unix philosophy

Traditional Unix CLIs do one thing and exit. Agent sessions run for hours. Resolutions vary:

- **sisyphus**: stateless ephemeral orchestrator respawned each cycle; all state on disk. The CLI is a thin shell over daemon RPC; long-running agents are tmux panes.
- **OpenHands**: event-sourced. Every action is an immutable event in a log; state replays from events. Multi-agent coordination via shared event stream.
- **goose**: continuous agent process; state implicit (filesystem changes).
- **Claude Code**: stateless per invocation, with session resumption via on-disk JSONL transcripts.

### Interactive vs scriptable

- **aider, Cursor**: chat REPL-first. Agents struggle to drive these — they assume a keyboard.
- **sisyphus, OpenHands**: daemon-first. Humans use a TUI; agents call CLI subcommands.
- **goose**: agent-first standalone; humans tail logs.

The lesson: pick a primary mode. Trying to be both an interactive REPL and a scriptable CLI usually fails at both.

### Cross-agent state

How agents share information when they can't talk directly:

- **sisyphus**: messages queue + report queue + shared session directory.
- **OpenHands**: event stream subscriptions.
- **MCP**: a protocol, not a CLI; agents call methods on shared servers.

### Tell-agent-X-do-Y addressing

- **sisyphus**: `sis tell <target> <text>` — async queue, target inspects on next cycle. `<target>` is `orchestrator`, `agent-001`, etc.
- **OpenHands**: post an event; agents see it via subscription.
- **goose**: can't — agent is autonomous; you watch its logs.
- **Cursor**: SDK hooks (`agent.sendMessage()`); not a CLI surface.

### Watch UX

- **sisyphus**: tmux-native (one pane per agent, dashboard in separate window).
- **OpenHands**: browser-first (VNC, web dashboard).
- **aider**: REPL is the watch (no separate surface).
- **Claude Code**: terminal-streaming output.

### MCP vs CLI

MCP (Model Context Protocol) is deliberately *not* a CLI. Tools become RPC methods on a server; agents call them programmatically. Trade-offs:

- **MCP**: typed methods, deterministic discovery via `tools/list`, but high token overhead (full schema injected upfront).
- **CLI**: familiar to agents (bash-native), composable via pipes, but parsing is fragile and exit-code-driven.

Production data (MindStudio): CLI workflows ran 35× cheaper in tokens and 28 percentage points more reliably on a 5-step task than the equivalent MCP server. The reverse trade-off — discoverability — favors MCP when the agent doesn't know what's available.

For an agent-orchestration CLI, treat CLI design as primary and add MCP as a secondary surface only when discoverability genuinely matters more than token cost.

## Sources

### Foundational guides

- [clig.dev — Command Line Interface Guidelines](https://clig.dev/)
- [GNU Coding Standards: CLI](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html)
- [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)
- [The Art of Unix Programming — Eric S. Raymond](http://www.catb.org/esr/writings/taoup/html/)
- [docopt: CLI Description Language](http://docopt.org/)
- [Heroku CLI Philosophy and Design](https://devcenter.heroku.com/articles/heroku-cli)
- [no-color.org — the NO_COLOR convention](https://no-color.org/)

### Tool documentation

- [Git: Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
- [GitHub CLI: Formatting and JSON](https://cli.github.com/manual/gh_help_formatting)
- [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)
- [Docker CLI Reference](https://docs.docker.com/reference/cli/docker/)
- [Terraform Plan + JSON Output](https://developer.hashicorp.com/terraform/internals/json-format)
- [HTTPie Documentation](https://httpie.io/docs/cli)

### Agent-CLI research

- [CLI Tools vs MCP: Better AI Agents With Less Context](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/)
- [MCP vs CLI in Agentic Workflows: 35× Token Overhead (MindStudio)](https://www.mindstudio.ai/blog/mcp-vs-cli-agentic-workflows-token-overhead-reliability)
- [Writing CLI Tools That AI Agents Actually Want to Use](https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no)
- [Making your CLI agent-friendly (Speakeasy)](https://www.speakeasy.com/blog/engineering-agent-friendly-cli)
- [Building Effective AI Agents (Anthropic)](https://www.anthropic.com/research/building-effective-agents)
- [Equipping agents with Agent Skills (Anthropic)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Model Context Protocol Architecture](https://modelcontextprotocol.io/docs/learn/architecture)

### Anti-pattern citations

- Color in pipes: [Fedify #257](https://github.com/fedify-dev/fedify/issues/257), [pino-pretty #231](https://github.com/pinojs/pino-pretty/issues/231), [yarn #5733](https://github.com/yarnpkg/yarn/issues/5733), [npm #7568](https://github.com/npm/npm/issues/7568), [nvm #2497](https://github.com/nvm-sh/nvm/issues/2497)
- stdout pollution: [npm/cli #2150](https://github.com/npm/cli/issues/2150), [Azure CLI #19365](https://github.com/Azure/azure-cli/issues/19365), [nerdctl #3772](https://github.com/containerd/nerdctl/issues/3772), [curl #12416](https://github.com/curl/curl/issues/12416)
- Non-TTY hangs: [Claude Code #9026](https://github.com/anthropics/claude-code/issues/9026), [codex #20919](https://github.com/openai/codex/issues/20919)
- Silent truncation: [rtk #827](https://github.com/rtk-ai/rtk/issues/827), [gemini-cli #5943](https://github.com/google-gemini/gemini-cli/issues/5943)
- Schema instability: [AWS CLI v1→v2 migration](https://docs.aws.amazon.com/cli/latest/userguide/cliv2-migration.html), [Azure CLI breaking changes](https://techcommunity.microsoft.com/blog/azuretoolsblog/azure-cli-breaking-change-pre-announcement/4403454)
- MCP server stdout: [postman.com community thread](https://community.postman.com/t/mcp-server-stdout-pollution-causing-invalid-json-rpc-messages-in-claude-desktop/89753)

### Agent-orchestration CLIs

- [Aider Documentation](https://aider.chat/docs/)
- [OpenHands GitHub](https://github.com/OpenHands/OpenHands)
- [Goose by Block](https://github.com/block/goose)
- [Cursor TypeScript SDK](https://cursor.com/blog/typescript-sdk)
- [Continue.dev async agents](https://blog.continue.dev/building-async-agents-with-continue-cli)
