---
name: commands-authoring
description: Guide to writing slash commands for Claude Code. Use when creating commands that set mode, constraints, or workflows invoked via /command-name.
user-invocable: false
paths:
  - "**/commands/**/*.md"
---

# Writing Slash Commands

Commands specify **constraints and mode**, not instructions. Claude already knows how to do most things — commands tell it what to do differently.

**Commands and skills are the same thing now.** `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both produce `/deploy` and use the same frontmatter. Existing `commands/` files keep working. Prefer skills when you need bundled scripts, reference files, or per-skill hooks — see the skills-authoring skill for the full feature set.

## Structure

```markdown
---
description: One-line description (shows in /help)
allowed-tools: Tool(pattern:*), Tool(pattern:*)
argument-hint: [arg1] [arg2]
---

Prompt content. Set role, constraints, then get out of the way.
```

## Features

- `$ARGUMENTS` — all args as a single string
- `$ARGUMENTS[N]` or `$N` — positional arg by 0-based index (`$0` is first)
- `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}` — runtime substitutions
- Inline bash: a `!` immediately followed by a backtick-wrapped command (e.g. the bang-prefix form around `git status`). Output is included in context. The literal pattern is intentionally not shown verbatim here because the preprocessor evaluates it on raw text **including inside fenced code blocks**, which would run the example at command-load time.
- Multi-line bash: open a fenced code block whose opener is three backticks immediately followed by `!`, and close it with a normal triple-backtick fence. Each line runs as a separate shell command; Claude sees the combined output.
- `@path/to/file.ts` — file reference (contents included inline)

Inline bash runs at **template expansion time** — it does not require `allowed-tools`. The `allowed-tools` field only governs tools the model can call at runtime.

## Key Rules

1. **Minimal tokens** — every line costs context
2. **Constraints > procedures** — say what to do differently, not how
3. **Don't restate knowledge** — skip things Claude already knows
4. **Limit allowed-tools** — only enable what's needed
5. **One concern** — focused commands, not kitchen sinks

## Invocation Control

Most commands should be **user-only** or **agent-only** — rarely both.

| Field | Who can invoke | Description in context | Use when |
|-------|---------------|----------------------|----------|
| *(default)* | User + Agent | Yes | Rare — general-purpose commands |
| `disable-model-invocation: true` | User only | **No** | Actions with side effects (commit, deploy, send) |
| `user-invocable: false` | Agent only | Yes | Background knowledge, auto-applied patterns |

**Default to `disable-model-invocation: true`** for most commands. Agent auto-invocation is a footgun — commands that modify state, run tools, or trigger workflows should require explicit user intent. Reserve agent-invocable commands for read-only reference or context-injection where autonomous discovery is the point.

## Other Frontmatter

| Field | Purpose |
|-------|---------|
| `model` | Override model (haiku for cheap, opus for capability) |
| `effort` | Override effort level: `low`, `medium`, `high`, `max` |
| `argument-hint` | Document expected args for autocomplete |
| `paths` | Glob patterns — only activate when working with matching files |
| `context: fork` | Run in an isolated subagent context |
| `agent` | Subagent type when `context: fork` is set (`Explore`, `Plan`, etc.) |
| `hooks` | Command-scoped hooks (same format as `hooks.json`, nested in frontmatter) |
| `shell` | `bash` (default) or `powershell` for inline shell execution |

## Commands vs Skills

Functionally identical — same frontmatter, same invocation. Choose the file layout:

| Single `.md` in `commands/` | Directory in `skills/` |
|-----------------------------|------------------------|
| Quick prompts, single file | Needs bundled scripts or reference files |
| Existing muscle memory | Per-skill hooks via `hooks:` frontmatter |
| <200 lines | Progressive disclosure across multiple `.md` files |

If a command needs to grow supporting files or bundled scripts, convert it to a skill directory.

## Anti-Patterns

- Missing `description` (won't appear in `/help` or Skill tool)
- `allowed-tools: Bash(*)` (overly permissive)
- Absolute file paths (use `@` references instead)
- No `argument-hint` when args are expected
- Long procedural instructions (use constraints instead)
