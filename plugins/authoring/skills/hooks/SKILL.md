---
name: hooks
description: Guide to Claude Code hooks — lifecycle events, handler types, decision control, and common patterns. Use when creating, debugging, or planning hooks for guardrails, context injection, quality gates, notifications, or automation.
user-invocable: false
paths:
  - "**/hooks.json"
  - "**/hooks/**/*.py"
  - "**/hooks/**/*.sh"
  - "**/hooks/**/*.mjs"
  - "**/hooks/**/*.js"
  - "**/hooks/**/*.ts"
---

# Claude Code Hooks

Hooks are deterministic handlers that fire at lifecycle events. Unlike instructions, hooks **cannot be ignored** — they block, inject, or modify at the system level.

## When to Use Hooks vs Other Tools

- **Hooks**: Must happen every time, no exceptions (guardrails, formatting, enforcement)
- **Rules/CLAUDE.md**: Advisory guidance Claude should follow (conventions, preferences)
- **Skills**: On-demand reference material (knowledge, methodology)

## Hook Events

Hooks fire at three points in execution: before the user or agent acts (`UserPromptSubmit`, `PreToolUse`), after the system acts (`PostToolUse`, `Stop`), and during agent lifecycle transitions (`SubagentStart`, `TaskCompleted`). Session bookend events (`SessionStart`, `SessionEnd`) handle setup and teardown. See [reference.md](reference.md) for the full event list with blocking/injection capabilities per event.

## Handler Types

Pick based on how complex the decision is:

| Handler | Use when... |
|---------|-------------|
| **command** | Logic is deterministic — regex check, file exists, env var set. Fastest. |
| **prompt** | Decision requires judgment but no file access — "is this prompt asking for secrets?" |
| **agent** | Decision requires investigation — read files, run commands, check state. |
| **http** | Hook logic lives outside the machine — shared enforcement service, cross-team policy. |

Default to `command`. Escalate to `prompt` only when a shell script can't encode the judgment. Use `agent` sparingly — it spawns a subagent and adds real latency.

## Decision Control

All hook output must be wrapped in `hookSpecificOutput` with the matching `hookEventName`. **`hookEventName` is required** — without it, Claude Code silently drops the payload.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "injected text"
  }
}
```

See [reference.md](reference.md) for the full per-event return value spec (`permissionDecision`, `updatedInput`, `decision: "block"`, etc.).

## Matchers

Use `|` to target multiple tools: `"matcher": "Write|Edit|MultiEdit"`. MCP tools match as `mcp__servername__toolname`. Omit matcher to catch all tools for that event.

See [reference.md](reference.md) for full matcher syntax including SessionStart variants.

## Skill- and Agent-Scoped Hooks

Hooks can be declared in `SKILL.md` or agent frontmatter to scope them to that skill/agent only — useful for guardrails that shouldn't apply globally. Uses the same matcher/handler format as `hooks.json`, nested under `hooks:` in frontmatter. See [reference.md](reference.md) for a full example.

## Common Patterns

See [patterns.md](patterns.md) for comprehensive examples organized by category:
- Guardrails and enforcement
- Context injection
- Quality gates (auto-format, lint, test)
- Notifications and alerts
- Logging and auditing
- Auto-approval workflows
- Input modification and sandboxing
- Git workflow automation
- Session management
- Agent team coordination

## Best Practices

- **Async for slow operations**: Set `"async": true` for hooks that shouldn't block (tests, notifications)
- **Timeouts**: Default is 60s for sync hooks. Set explicit timeouts for fast hooks.
- **Idempotency**: Hooks may fire multiple times. Guard against duplicate processing.
- **Stop hook loops**: Always check `stop_hook_active` to prevent infinite continuation loops.
- **Minimal hooks.json**: One concern per hook. Compose multiple small hooks rather than one monolith.
