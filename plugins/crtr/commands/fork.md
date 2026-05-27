---
description: Fork the current Claude Code session into a sibling pane
allowed-tools: Bash(crtr:*)
---

The user wants to fork the current Claude Code session into a sibling pane via `crtr job start fork`. Begin by following the CLI guidance below.

!`crtr job start fork -h`

To fork the current session:

```
crtr job start fork [--cwd <dir>]
```

Takes no prompt — the new pane inherits this session's context. Requires `$CLAUDE_CODE_SESSION_ID` (automatically set inside Claude Code). Returns `{job_id, follow_up}`.

$ARGUMENTS
