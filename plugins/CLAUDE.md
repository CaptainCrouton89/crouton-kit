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
- `$ARGUMENTS` - all args as string; `$0`, `$1` for positional (0-indexed)
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

## Creating a New Plugin

**IMPORTANT**: After creating a plugin directory, you MUST register it in `/.claude-plugin/marketplace.json`:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "What it does",
  "version": "1.0.0",
  "keywords": ["relevant", "keywords"]
}
```

Without this registration, the plugin won't be discovered by Claude Code even if the files exist.

## Key Plugins

| Plugin | Purpose |
|--------|---------|
| `devcore` | Core agents (programmer, senior-advisor), code quality rules, code-review command |
| `rpi` | Feature workflow: `/arch` → `/plan` → `/implement` → `/review` → `/fix` |
| `git-smart` | Safe commit workflow with security scanning |
| `debugging` | `/debug` and `/investigate-fix` commands |
| `knowledge-capture` | `/interview`, `/learn`, `/collaborate` |


## CI & Versioning

Pushing to `main` triggers CI that automatically bumps versions in both `plugin.json` and `marketplace.json`. Do not manually update versions.

CI determines bump type from conventional commit prefix: `feat` → minor, `fix`/`refactor`/etc → patch, `!`/`BREAKING CHANGE` → major.

## Propagating Changes

Plugin cache is versioned by `plugin.json` version. After pushing: wait for CI version bump, then `/reload-plugins`. It fetches the marketplace repo, populates a new cache entry, and loads it. No manual `git pull` or session restart needed.

**For rapid local iteration** (bypasses cache entirely):
```bash
claude --plugin-dir ./plugins/web --plugin-dir ./plugins/devcore
```

## Known Upstream Issues

Plugin cache/update bugs that affect marketplace distribution:

- [#16866 - Plugin marketplace cache not updated before install/update](https://github.com/anthropics/claude-code/issues/16866)
- [#17361 - Plugin cache never refreshes - autoUpdate doesn't update what Claude reads](https://github.com/anthropics/claude-code/issues/17361)
- [#21205 - Marketplace plugin updates accumulate git history instead of staying shallow](https://github.com/anthropics/claude-code/issues/21205)
- [#35641 - /reload-plugins doesn't fire skill discovery for marketplace plugins](https://github.com/anthropics/claude-code/issues/35641)
- [#28492 - Local plugin cache not invalidated when source files change](https://github.com/anthropics/claude-code/issues/28492)

Types: `bug`, `feature`, `task`, `epic`, `chore`
Priorities: 0=critical, 1=high, 2=medium, 3=low, 4=backlog
