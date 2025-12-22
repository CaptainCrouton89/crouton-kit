# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Claude Code plugin collection**—a set of plugins that extend Claude Code with custom commands, agents, rules, and hooks. Each subdirectory (e.g., `devcore/`, `rpi/`, `git-smart/`) is a standalone plugin.

## Plugin Structure

Each plugin follows this structure:
```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata (name, version, description)
├── commands/                 # Slash commands (*.md)
├── agents/                   # Agent definitions (*.md)
├── rules/                    # Auto-applied rules (*.md with paths frontmatter)
├── hooks/                    # Lifecycle hooks (hooks.json)
├── output-styles/            # Custom output styles (*.md)
└── skills/                   # Reusable skills (SKILL.md)
```

## Writing Plugin Components

### Commands (`commands/*.md`)
Slash commands specify **constraints and mode**, not instructions. Claude already knows how to do most things.

**Structure:**
```markdown
---
description: One-line description (shows in /help)
allowed-tools: Tool(pattern:*), Tool(pattern:*)
argument-hint: [arg1] [arg2]
---

Prompt content. Set role, constraints, then get out of the way.
```

**Features:**
- `$ARGUMENTS` - all args as string, or `$1`, `$2` for positional
- `` !`git status` `` - inline bash output
- `@path/to/file.ts` - file reference

**Rules:** Minimal tokens, constraints > procedures, limit allowed-tools, one concern per command.

### Agents (`agents/*.md`)
Background workers spawned via Task tool. Same frontmatter plus:
- `model: sonnet|opus|haiku` - override default model
- `color: blue|green|...` - status display color

### Rules (`rules/*.md`)
Auto-applied constraints for matching files:
```markdown
---
paths:
  - "src/**/*.ts"
  - "**/*.test.ts"
---

Declarative constraints here.
```
Omit `paths` for rules that apply everywhere.

## Key Plugins

| Plugin | Purpose |
|--------|---------|
| `devcore` | Core agents (programmer, junior-engineer), code quality rules, code-review command |
| `rpi` | Feature workflow: `/arch` → `/plan` → `/implement` → `/review` → `/fix` |
| `git-smart` | Safe commit workflow with security scanning |
| `debugging` | `/debug` and `/investigate-fix` commands |
| `knowledge-capture` | `/interview`, `/learn`, `/collaborate` |

## Issue Tracking (bd/beads)

**IMPORTANT**: Use `bd` (beads) for ALL issue tracking. No markdown TODOs.

```bash
bd ready              # Show unblocked work
bd create "Title" -t task -p 2   # Create issue (priority 0-4)
bd update <id> --status in_progress
bd close <id>
bd sync               # Push to git
```

Types: `bug`, `feature`, `task`, `epic`, `chore`
Priorities: 0=critical, 1=high, 2=medium, 3=low, 4=backlog
