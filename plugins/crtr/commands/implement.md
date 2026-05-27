---
description: Launch an implementer for an approved plan in a new pane
allowed-tools: Bash(crtr:*)
---

The user wants to hand off implementation of an approved plan to a fresh agent.

!`crtr job start implementer -h`

Resolve the plan's absolute path with `crtr flow plan show <plan-name>` (returns `.path`), then pass it positionally to `crtr job start implementer`:

```
crtr job start implementer <absolute plan path> [--cwd <project dir>]
```

Returns `{job_id, follow_up}`. Monitor with `crtr job read status <job_id>` / `crtr job read logs <job_id>`, or block for completion with `crtr job read result <job_id> --wait`.

$ARGUMENTS
