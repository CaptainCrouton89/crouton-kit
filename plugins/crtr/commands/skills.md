---
description: Work with crtr skills
allowed-tools: Bash(crtr:*)
---

The user wants to work with crtr skills. Begin by following the CLI guidance below.

!`crtr skill -h`

Use the branches above. Key patterns:
- Discover: `crtr skill find list` or `crtr skill find search <query>` (add `--search-body` to also grep SKILL.md bodies)
- Read: `crtr skill read show <name>` (use `--frontmatter` to include YAML)
- Author guide: `crtr skill author guide [--topic <topic>]` (omit `--type` for the picker; add `--type playbook|primer|reference|runbook|freeform` for the full workflow)
- Scaffold: `crtr skill author scaffold <plugin:name> [--type <type>] [--description <text>]`
- Toggle: `crtr skill state enable <name>` or `crtr skill state disable <name>`

$ARGUMENTS
