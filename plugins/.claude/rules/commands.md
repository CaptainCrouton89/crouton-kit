---
paths:
  - "**/commands/**/*.md"
---

# Writing Slash Commands

Claude already knows how to do most things. Commands specify **constraints and mode**, not instructions.

## Structure

```markdown
---
description: One-line description (shows in /help)
allowed-tools: Tool(pattern:*), Tool(pattern:*)
argument-hint: [arg1] [arg2]
---

Prompt content here. Set role, constraints, then get out of the way.
```

## Features

- `$ARGUMENTS` - all args as string, or `$1`, `$2` for positional
- `!`git status`` - inline bash output
- `@path/to/file.ts` - file reference

## Rules

1. **Minimal tokens** - every line costs context
2. **Constraints > procedures** - say what to do differently, not how
3. **Don't restate knowledge** - skip things Claude already knows
4. **Limit allowed-tools** - only enable what's needed
5. **One concern** - focused commands, not kitchen sinks
