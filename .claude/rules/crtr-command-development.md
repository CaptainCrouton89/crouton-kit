---
paths:
  - "**/crtr/commands/**"
  - "**/crtr/commands/*.md"
---

`plugins/crtr/commands/*.md` files must be thin passthroughs to the `crtr` CLI. The CLI's own help output (`crtr <family> -h`) and default prompt are the single source of truth for how the agent should behave — slash command files must not duplicate that content.

**Required shape**: frontmatter (`description`, `allowed-tools: Bash(crtr:*)`), one short framing sentence, an inline `!`crtr <family>`` invocation, and `$ARGUMENTS`. Nothing else.

**Do not** put usage instructions, subcommand lists, behavioral guidance, examples, or workflow steps in the markdown. If the agent needs to be directed to do something when a slash command fires, surface that direction from `crtr <family>`'s output (edit the CLI in `crouter/src/`), not from the `.md` file.

**Why**: duplicating content across the CLI and the slash command files causes drift — the two go out of sync, and end users running `crtr <family>` from a shell get different guidance than agents invoking the slash command. Keeping the markdown trivial means there is one place to update behavior: the CLI.
