# crtr plugin (crouton-kit)

Slash-command entrypoints into the `crtr` CLI. Role: **routing only** —
give users `/crtr:foo` shortcuts that invoke `crtr foo` and surface its
agent-facing prompt to the conversation.

## Scope

- Slash-command shims in `commands/` that call `crtr <subcommand>`.
- Frontmatter limited to `description` + `allowed-tools: Bash(crtr:*)`.
- Body shape: one-line intro + `!crtr <subcommand>` + `$ARGUMENTS`.

## Boundary

- **Routing logic / intent dispatch** lives in the CLI's agent prompts
  (`~/Code/cli/crouter/src/prompts/`). Slash commands here must NOT
  duplicate that logic — let the prompt do the work.
- **Foundational CLI behavior** → `~/Code/cli/crouter`.
- **Convenient, loosely-coupled extensions** →
  `~/Code/cli/crouter-official-marketplace`.

If a command file here is doing more than printing the CLI prompt and
forwarding `$ARGUMENTS`, the logic probably belongs in `crouter` instead.

## Why this layer exists

The CLI prompt (`crtr <subcommand>` output) is the source of truth for
agent behavior, but users want short slash-command entry points in
Claude Code. This plugin is that thin bridge — nothing more.
