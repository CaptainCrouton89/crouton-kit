---
description: Get help with the hookify plugin
allowed-tools: ["Read"]
---

# Hookify Plugin Help

Explain how the hookify plugin works and how to use it.

## Overview

The hookify plugin makes it easy to create custom hooks that prevent unwanted behaviors. Instead of editing `hooks.json` files, users create simple markdown configuration files that define patterns to watch for.

## How It Works

### 1. Hook System

Hookify installs generic hooks that run on these events:
- **PreToolUse**: Before any tool executes (Bash, Edit, Write, etc.)
- **PostToolUse**: After a tool executes
- **Stop**: When Claude wants to stop working
- **UserPromptSubmit**: When user submits a prompt

These hooks read configuration files from `.claude/hookify.*.local.md` and check if any rules match the current operation.

### 2. Configuration Files

Rules can be placed in **two locations**:
- `~/.claude/hookify.*.local.md` - **Global rules** (apply to all projects)
- `.claude/hookify.*.local.md` - **Project rules** (apply to current project only)

Example rule file:

```markdown
---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
---

⚠️ **Dangerous rm command detected!**

This command could delete important files. Please verify the path.
```

**Key fields:**
- `name`: Unique identifier for the rule
- `enabled`: true/false to activate/deactivate
- `event`: bash, file, stop, prompt, or all
- `pattern`: Regex pattern to match

The message body is what Claude sees when the rule triggers.

### 3. Creating Rules

**Option A: Use /hookify command**
```
/hookify Don't use console.log in production files
```

This analyzes your request and creates the appropriate rule file.

**Option B: Create manually**
Create `.claude/hookify.my-rule.local.md` with the format above.

**Option C: Analyze conversation**
```
/hookify
```

Without arguments, hookify analyzes recent conversation to find behaviors you want to prevent.

## Available Commands

- **`/hookify`** - Create hooks from conversation analysis or explicit instructions
- **`/hookify:help`** - Show this help (what you're reading now)
- **`/hookify:list`** - List all configured hooks
- **`/hookify:configure`** - Enable/disable existing hooks interactively

## Example Use Cases

**Prevent dangerous commands:**
```markdown
---
name: block-chmod-777
enabled: true
event: bash
pattern: chmod\s+777
---

Don't use chmod 777 - it's a security risk. Use specific permissions instead.
```

**Warn about debugging code:**
```markdown
---
name: warn-console-log
enabled: true
event: file
pattern: console\.log\(
---

Console.log detected. Remember to remove debug logging before committing.
```

**Require tests before stopping:**
```markdown
---
name: require-tests
enabled: true
event: stop
pattern: .*
---

Did you run tests before finishing? Make sure `npm test` or equivalent was executed.
```

## Pattern Syntax

Use Python regex syntax:
- `\s` - whitespace
- `\.` - literal dot
- `|` - OR
- `+` - one or more
- `*` - zero or more
- `\d` - digit
- `[abc]` - character class

**Examples:**
- `rm\s+-rf` - matches "rm -rf"
- `console\.log\(` - matches "console.log("
- `(eval|exec)\(` - matches "eval(" or "exec("
- `\.env$` - matches files ending in .env

## Dynamic Command Interpolation

Messages can include shell commands that get executed and replaced with their output. Use the syntax `!​`command`` (exclamation mark followed by backticks).

**Example - Show Linear issues when linear is mentioned:**
```markdown
---
name: linear-issues
enabled: true
event: prompt
pattern: \blinear\b
---

**Your Linear Issues:**
!​`linear issue list --limit 10`
```

When this rule triggers, the `!​`linear issue list --limit 10`` will be replaced with the actual output of that command.

**Notes:**
- Commands timeout after 5 seconds
- Errors are shown as `(error: ...)`
- Empty output shows as `(no output)`
- Great for showing context like git status, issue lists, etc.

## Important Notes

**No Restart Needed**: Hookify rules (`.local.md` files) take effect immediately on the next tool use. The hookify hooks are already loaded and read your rules dynamically.

**Block or Warn**: Rules can either `block` operations (prevent execution) or `warn` (show message but allow). Set `action: block` or `action: warn` in the rule's frontmatter.

**Rule Files**: Rules can be global (`~/.claude/`) or project-local (`.claude/`). Project rules should be git-ignored (add `.claude/*.local.md` to .gitignore).

**Disable Rules**: Set `enabled: false` in frontmatter or delete the file.

## Troubleshooting

**Hook not triggering:**
- Check rule file is in `.claude/` directory
- Verify `enabled: true` in frontmatter
- Confirm pattern is valid regex
- Test pattern: `python3 -c "import re; print(re.search('your_pattern', 'test_text'))"`
- Rules take effect immediately - no restart needed

**Import errors:**
- Check Python 3 is available: `python3 --version`
- Verify hookify plugin is installed correctly

**Pattern not matching:**
- Test regex separately
- Check for escaping issues (use unquoted patterns in YAML)
- Try simpler pattern first, then refine

## Getting Started

1. Create your first rule:
   ```
   /hookify Warn me when I try to use rm -rf
   ```

2. Try to trigger it:
   - Ask Claude to run `rm -rf /tmp/test`
   - You should see the warning

4. Refine the rule by editing `.claude/hookify.warn-rm.local.md`

5. Create more rules as you encounter unwanted behaviors

For more examples, check the `${CLAUDE_PLUGIN_ROOT}/examples/` directory.
