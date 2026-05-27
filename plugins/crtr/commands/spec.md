---
description: Start a spec session
allowed-tools: Bash(crtr:*)
---

The user has requested to start a spec. Begin by following the guidance below.

!`crtr flow spec new -h`

Follow the workflow above. When ready to save, pipe the spec markdown on stdin and pass the name as a positional arg:

```
echo '<spec markdown>' | crtr flow spec new <kebab-case-name>
```

Returns `{path, follow_up}`. Run the `follow_up` next.

$ARGUMENTS
