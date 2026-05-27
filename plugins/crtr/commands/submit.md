---
description: Inside a crtr-spawned session, deliver result back to the parent job record
allowed-tools: Bash(crtr:*)
---

The user wants to submit a result back to the parent crtr job via `crtr job submit`. Begin by following the CLI guidance below.

!`crtr job submit -h`

Write the result payload to a JSON file, then pass its path to `--context-file`:

```
crtr job submit "$CRTR_JOB_ID" --context-file <path-to-result.json> [--kill-pane]
```

`$CRTR_JOB_ID` is injected automatically in crtr-spawned panes. The file at `--context-file` must contain a JSON object — it becomes `result.json`. Pass `--kill-pane` from reviewer agents to close the spawned pane after submission. Returns `{submitted, pane_kill_scheduled}`.

$ARGUMENTS
