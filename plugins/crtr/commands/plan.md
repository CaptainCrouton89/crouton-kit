---
description: Start a planning session
allowed-tools: Bash(crtr:*)
---

The user has requested to start planning. Begin by following the guidance below.

!`crtr flow plan new -h`

Follow the workflow above. When ready to save, pipe the plan markdown on stdin and pass the name as a positional arg:

```
echo '<plan markdown>' | crtr flow plan new <kebab-case-name> [--spec <spec-name>]
```

Returns `{path, follow_up}`. Run the `follow_up` next.

$ARGUMENTS
