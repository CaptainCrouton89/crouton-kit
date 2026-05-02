---
name: rules-authoring
description: Guide to writing .claude/rules/*.md files — auto-applied constraints scoped by file patterns. Use when creating or updating rules for code conventions, quality standards, or file-specific guidance.
user-invocable: false
paths:
  - ".claude/rules/**/*.md"
  - "**/rules/**/*.md"
---

# Writing Rules

Rules are constraints Claude follows automatically when working with matching files. They live in `.claude/rules/` or a plugin's `rules/` directory.

## Structure

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "**/*.test.ts"
---

Declarative constraints here.
```

## Path Patterns

- `**/*.ts` — all TypeScript files
- `src/**/*` — everything under src/
- `{src,lib}/**/*.ts` — multiple directories
- Omit `paths` entirely for rules that apply everywhere

Rules without `paths` load every session. Rules with `paths` only load when Claude works with matching files.

## Writing Constraints

**Be declarative** — state what should/shouldn't be done, not step-by-step procedures.

**Be specific** — "Use 2-space indentation" not "format properly."

**Skip the obvious** — don't restate best practices Claude already knows. Only specify what's unique to your project.

**One topic per file** — `testing.md`, `security.md`, not `everything.md`. Organize with subdirectories for grouping.

**Provide alternatives** — never write "Don't do X" without saying what to do instead.

## When to Use Rules vs Other Tools

- **Rules**: File-type-specific conventions that are advisory (Claude should follow but there's no hard enforcement)
- **CLAUDE.md**: Universal project context loaded every session
- **Hooks**: Must be enforced deterministically — cannot be ignored
- **Skills**: Reference material loaded on-demand, not automatically

## Anti-Patterns

- Procedural instructions (use commands or skills instead)
- Rules that apply to every file type (use CLAUDE.md or omit `paths`)
- Duplicating CLAUDE.md content
- Over-broad path patterns that match unrelated files
- Rules longer than ~30 lines (split into multiple files or use a skill)
