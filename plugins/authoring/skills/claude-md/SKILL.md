---
name: claude-md-authoring
description: Best practices for writing effective CLAUDE.md files. Use when creating, updating, or auditing CLAUDE.md files for projects or directories.
user-invocable: false
paths:
  - "**/CLAUDE.md"
---

# Writing Effective CLAUDE.md Files

## Philosophy

CLAUDE.md is a curated set of **guardrails and pointers**, not a comprehensive manual. Every line is scarce real estate. Focus on constraints and gotchas — things Claude would get wrong without guidance.

## What to Include

Prioritize in order:
1. **Critical constraints and gotchas** — non-obvious rules, what breaks if ignored
2. **Key commands** — build, test, lint (the 80% cases)
3. **Architecture overview** — how major components relate, 2-3 sentences max
4. **Conventions that differ from defaults** — only what's surprising

## What to Exclude

- Anything Claude can infer from reading code
- Standard language/framework conventions
- Detailed API documentation (link to docs instead)
- Long explanations or tutorials
- File-by-file codebase descriptions
- Information that changes frequently

## Writing Rules

- Short declarative bullets > paragraphs
- Never write "Never X" without the preferred alternative
- When referencing other docs, pitch *when/why* to read them (e.g., "For FooError, see docs/foo.md")
- If guidance exceeds ~5 lines, it belongs in a skill or rule instead

## Root vs Subdirectory

**Root** (~100-200 lines): Project-wide constraints, build/test commands, architecture. Loaded every session.

**Subdirectory** (<50 lines): Only create when:
- Directory has >5 files or >3 subdirectories
- Local conventions differ from project standards
- Non-obvious constraints specific to this directory

Don't repeat parent CLAUDE.md content. Don't explain what's obvious from the directory name.

## When to Use Something Else

- **>5 lines of domain knowledge** → Skill (loaded on-demand, not every session)
- **File-type-specific constraints** → Rule with `paths` frontmatter
- **Deterministic enforcement** → Hook (can't be ignored)

## Auditing Existing CLAUDE.md

For each line, ask: "Would Claude's behavior change if I removed this?" If no, cut it.

Signs of bloat:
- >300 lines
- Claude ignores rules despite them being there (context dilution)
- Generic best practices Claude already knows
- Duplicated information from parent CLAUDE.md files

When adding content, always propose **pruning alongside additions**. The file should get tighter over time, not longer.
