---
name: modes-authoring
description: Guide to writing ai-cli mode files. Use when creating modes for non-interactive Claude Code sessions — preconfigured agent runs with locked-in system prompts, model selection, and prompt wrappers.
user-invocable: false
paths:
  - "**/modes/**/*.md"
  - "**/.ai/modes/**/*.md"
---

# Writing ai-cli Modes

Modes are markdown files that configure non-interactive Claude Code sessions via the Agent SDK. Each mode defines a system prompt, model, and optional prompt wrapper — producing a preconfigured, fire-and-forget agent.

## File Location

| Location | Scope | Precedence |
|----------|-------|------------|
| `.claude/.ai/modes/<name>.md` | Project-local | Wins over built-in |
| `ai-cli/modes/<name>.md` | Built-in (bundled) | Fallback |

## Required Frontmatter

```yaml
---
model: opus
system-prompt-mode: append
---
```

| Field | Required | Values | Default |
|-------|----------|--------|---------|
| `model` | Yes | Any valid model ID | — |
| `system-prompt-mode` | No | `append`, `replace` | `append` |

- **`append`** — mode's system prompt is appended to the default Claude Code system prompt. The agent retains all standard capabilities.
- **`replace`** — mode's system prompt completely replaces the default. Use for fully custom agent personas.

## Body: System Prompt

Everything after the frontmatter (before `## Prompt Wrapper` if present) becomes the system prompt content.

```markdown
---
model: claude-sonnet-4-5-20250929
system-prompt-mode: append
---

You are a security auditor. Report vulnerabilities only — never edit code.

Focus on: injection, auth bypass, data exposure, SSRF.
```

## Prompt Wrapper (Optional)

A `## Prompt Wrapper` heading defines a template applied to the user's `-p` argument. Use `{{prompt}}` as the placeholder.

```markdown
---
model: opus
system-prompt-mode: append
---

You are a systematic debugger. Investigate only — no code changes.

## Prompt Wrapper

Debug the following issue. Diagnose root cause — don't fix.

Issue description:
{{prompt}}
```

Without a prompt wrapper, the `-p` argument is passed directly as the user prompt.

## Usage

```bash
# Built-in mode
ai -m review -p "src/auth/"

# Project-local mode
ai -m security-audit -p "check the API layer"

# List all available modes (built-in + local)
ai -l
```

## Design Principles

1. **Constraints over procedures** — tell the agent what to focus on and what not to do, not step-by-step instructions
2. **Pick the right model** — haiku/sonnet for cheap triage, opus for deep analysis
3. **`append` for most modes** — the agent keeps Claude Code's full toolset; you're just narrowing its focus
4. **`replace` sparingly** — only when you need a completely custom persona
5. **Prompt wrappers for structure** — frame the user's input when the mode expects a specific format

## Examples: Built-in Modes

- **`general`** — sonnet, append, no wrapper. Minimal: "direct, efficient assistant"
- **`debug`** — opus, append, wrapper frames input as "Issue description". Multi-phase methodology in system prompt.
- **`review`** — opus, append, wrapper frames input as review target. Detailed concern taxonomy in system prompt.

## Composability

Modes are callable from hooks, scripts, and other tools:

```bash
# In a pre-commit hook
ai -m validate-commit -p "$(git diff --cached)"

# In a CI script
ai -m review -p "$(git diff origin/main...HEAD)"
```
