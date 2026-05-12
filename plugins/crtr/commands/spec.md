---
description: How to use the `crtr spec` command family
allowed-tools: Bash(crtr:*)
---

# `crtr spec` — quick reference

Run bare to enter a spec session (prints a prompt that drives spec writing). Save with `--name` once the spec is settled.

```
crtr spec                          # print the spec prompt to start a session
crtr spec --name <kebab-name>      # save spec content (pipe markdown or pass as arg)
crtr spec list                     # list specs for the current directory
crtr spec show <name>              # print the body of a saved spec
crtr spec path [name]              # absolute path of a spec or the specs dir
crtr spec edit <name>              # open the spec in $EDITOR
```

Specs settle **behavior** (what), not mechanism (how). Plans come after.
