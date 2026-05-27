---
description: Spawn a fresh claude in a sibling pane (async; prints job id)
allowed-tools: Bash(crtr:*)
---

The user wants to spawn a fresh sibling claude pane via `crtr job start prompt`. Begin by following the CLI guidance below.

!`crtr job start prompt -h`

To spawn: pipe the prompt text on stdin.

```
echo '<prompt text>' | crtr job start prompt [--cwd <dir>]
```

Returns `{job_id, follow_up}`. Use `job_id` with `crtr job read status <job_id>` or `crtr job read result <job_id>` to monitor.

$ARGUMENTS
