---
description: How to use the `crtr plan` command family
allowed-tools: Bash(crtr:*)
---

# `crtr plan` — quick reference

Run bare to enter a plan session (prints a prompt that drives plan writing). Save with `--name` once the plan is settled.

```
crtr plan                          # print the plan prompt to start a session
crtr plan --name <kebab-name>      # save plan content (pipe markdown or pass as arg)
crtr plan list                     # list plans for the current directory
crtr plan show <name>              # print the body of a saved plan
crtr plan path [name]              # absolute path of a plan or the plans dir
crtr plan edit <name>              # open the plan in $EDITOR
```

Plans turn a settled spec into actionable, ordered implementation work.
