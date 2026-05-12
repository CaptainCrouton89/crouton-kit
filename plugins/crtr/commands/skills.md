---
description: How to use the `crtr skill` command family
allowed-tools: Bash(crtr:*)
---

# `crtr skill` — quick reference

`crtr` ships skills (markdown reference with frontmatter) you can pull on demand.

```
crtr skill list              # what's installed
crtr skill show <name>       # print SKILL.md body to stdout
crtr skill grep <pattern>    # search across skill bodies
crtr skill where <name>      # show {scope, plugin, path}
crtr skill new <plugin>:<name> --description "..."
```

When the user's task matches a skill's description, run `crtr skill show <name>` and apply the guidance. Ambiguous names exit `4` — disambiguate with `<plugin>:<skill>`.
