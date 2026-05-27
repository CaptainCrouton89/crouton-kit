---
description: Block until a spawned agent job completes; prints result
allowed-tools: Bash(crtr:*)
---

The user wants to await a spawned agent's result via `crtr job read result`. Begin by following the CLI guidance below.

!`crtr job read result -h`

To wait for a job and collect its result:

```
crtr job read result <job_id> --wait
```

Blocks up to 10 minutes. Returns `{job_id, status, result}` where `status` is `done|failed|canceled|timeout`.

$ARGUMENTS
