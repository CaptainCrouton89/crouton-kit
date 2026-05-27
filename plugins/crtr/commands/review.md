---
description: Launch a reviewer agent for a plan or spec artifact in a sibling pane
allowed-tools: Bash(crtr:*)
---

The user wants to hand off a review of a plan or spec artifact via `crtr job start reviewer`. Begin by following the CLI guidance below.

!`crtr job start reviewer -h`

To launch a reviewer:

```
crtr job start reviewer <absolute artifact path> --kind plan|spec [--spec-path <absolute spec path>] [--cwd <dir>]
```

`--spec-path` is for plan reviews when the plan implements a spec; omit it for spec reviews. Returns `{job_id, follow_up}`. The originating pane stays alive — block on `crtr job read result <job_id> --wait` and act on the verdict.

Note: the old `crtr agent review` reviewed the working tree; the new reviewer targets a saved plan/spec artifact. To review uncommitted code, save a plan or spec first, then pass its path here.

$ARGUMENTS
