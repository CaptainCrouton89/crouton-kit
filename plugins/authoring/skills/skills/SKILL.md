---
name: skills-authoring
description: Guide to writing SKILL.md files for Claude Code. Use when creating skills that provide on-demand reference, methodology, or workflow guidance.
user-invocable: true
paths:
  - "**/SKILL.md"
  - "**/skills/**/*.md"
---

# Writing Skills

Skills are on-demand reference material Claude loads when relevant — not every session. They're ideal for methodology, domain knowledge, and complex workflows that would bloat CLAUDE.md.

**Commands are now skills.** `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both produce `/deploy` and use the same frontmatter. Existing `commands/` files keep working, but new work should go in `skills/` — skills can bundle supporting files, scripts, and per-skill hooks that commands cannot.

## Structure

```
skill-name/
├── SKILL.md              # Required: overview and navigation
├── reference.md          # Optional: detailed docs
├── examples.md           # Optional: usage examples
└── scripts/              # Optional: bundled utilities
    └── validate.py
```

## Required Frontmatter

```yaml
---
name: skill-name
description: What it does. Specific capabilities. Use when [trigger scenarios].
---
```

The `description` field drives automatic discovery. Include keywords users would naturally say. Front-load the key use case — descriptions longer than 250 characters get truncated in the skill listing.

**Bad**: `Helps with documents`
**Good**: `Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDFs, forms, or document extraction.`

## Optional Frontmatter

| Field | Purpose |
|-------|---------|
| `argument-hint` | Autocomplete hint for expected args: `[issue-number]` |
| `allowed-tools` | Restrict available tools (space-separated or YAML list) |
| `model` | Override model (opus/sonnet/haiku) |
| `effort` | Override effort level: `low`, `medium`, `high`, `max` (Opus 4.6 only) |
| `context: fork` | Run in isolated subagent context |
| `agent` | Agent type when forked: `Explore`, `Plan`, `general-purpose`, or custom |
| `user-invocable: false` | Hide from slash menu (agent-only) |
| `disable-model-invocation: true` | Prevent autonomous invocation (user-only) |
| `paths` | Glob patterns — only activate when working with matching files |
| `hooks` | Skill-scoped hooks (same format as `hooks.json`, nested in frontmatter) |
| `shell` | `bash` (default) or `powershell` for inline shell execution |

## Invocation Control

Default: both user and Claude can invoke. Two fields restrict this:

- **`disable-model-invocation: true`** — user-only. Description is not loaded into context. Use for actions with side effects (`/commit`, `/deploy`).
- **`user-invocable: false`** — agent-only. Description stays in context so Claude can find it. Use for background reference that isn't a meaningful user action.

## Passing Arguments

```yaml
---
name: fix-issue
description: Fix a GitHub issue
argument-hint: [issue-number]
---

Fix GitHub issue $ARGUMENTS following our coding standards.
```

**Substitutions:**
- `$ARGUMENTS` — all args as a single string
- `$ARGUMENTS[N]` or `$N` — positional arg by 0-based index (`$0` is first)
- `${CLAUDE_SESSION_ID}` — current session ID
- `${CLAUDE_SKILL_DIR}` — directory containing this `SKILL.md` (use for bundled scripts)

Indexed args use shell-style quoting: `/migrate "hello world" second` → `$0` = `hello world`, `$1` = `second`. If the skill doesn't include `$ARGUMENTS`, Claude Code appends `ARGUMENTS: <value>` to the end.

## Injecting Dynamic Context

Shell commands run **before** the skill is sent to Claude — Claude sees the output, not the command. The syntax is a `!` immediately followed by a backtick-wrapped command (e.g. the bang-prefix form around `gh pr diff`). The literal pattern is intentionally not shown verbatim in this file because the preprocessor evaluates it on raw text **including inside fenced code blocks**, which would run the example at skill-load time.

For multi-line commands, open a fenced code block whose opener is three backticks immediately followed by `!`, and close it with a normal triple-backtick fence. Each line inside runs as a separate shell command, and Claude sees the combined output.

This is preprocessing, not tool use — bundled and managed skills aren't affected by `disableSkillShellExecution`, but user/project/plugin skills are.

## Skill vs Reference Manual

The litmus test: **does this teach judgment or describe an API?**

A skill helps someone who doesn't know *what to do* — it provides decision frameworks, heuristics, and principles they can reason from. A reference manual helps someone who already knows what to do but forgot *how* — it provides API surfaces, tables, and exhaustive listings.

If your SKILL.md reads like a man page, you've written a reference doc wearing a skill's clothes. Extract the reference material to `reference.md` and rewrite SKILL.md around the decisions.

**Skill markers:**
- Teaches a framework for thinking about a class of problems
- Includes "when to use" and "when not to use"
- Someone unfamiliar with the domain makes better decisions after reading it
- Prose over tables — heuristics compose, lookup rows don't

**Reference markers:**
- Lists API surfaces, event taxonomies, or CLI commands
- Assumes the reader already knows *why* they're here
- Tables and code examples dominate
- No decision frameworks

Most skills need both — SKILL.md for the judgment layer, `reference.md` for the lookup layer. The mistake is combining them.

## Writing for Token Efficiency

LLM reasoning degrades as context grows — research shows meaningful accuracy drops around 3k tokens. Every line in a skill competes for attention with the rest of the agent's context.

**Budget ~150 lines for SKILL.md.** This forces density.

- Lead with the decision, not the mechanism. "When you need X" before "how X works."
- If a section exceeds 20 lines without teaching judgment, move it to `reference.md`.
- Tables are expensive — a 3-line prose summary often teaches the same thing as a 25-row table.
- Example reasoning chains > example outputs. Show *how to think*, not *what to produce*.
- One well-placed "don't" prevents more bad behavior than three paragraphs of explanation.

**The test:** Can someone reading your SKILL.md for 30 seconds make a better decision than they would without it? If they have to read the whole thing to get value, you've buried the judgment.

## Progressive Disclosure

Keep SKILL.md under 500 lines. Put detailed reference in supporting files:

```markdown
For detailed patterns, see [patterns.md](patterns.md)
For examples, see [examples.md](examples.md)
```

Claude reads additional files only when needed — this keeps context lean.

## Running in a Subagent

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly: find files, read code, summarize findings.
```

With `context: fork`, SKILL.md content becomes the task prompt for a fresh subagent. Only meaningful for skills with explicit instructions — reference-only skills will return empty. The inverse pattern (custom subagent that preloads skills as reference) lives in the subagent definition, not here.

## Extended Thinking

Include the word `ultrathink` anywhere in the skill content to enable extended thinking when the skill runs.

## When to Use Skills vs Other Tools

- **Skills**: Complex methodology, detailed reference, domain knowledge, workflows
- **Rules**: Auto-applied constraints for matching files — declarative, not procedural
- **CLAUDE.md**: Universal project context — short, always-loaded
- **Hooks**: Deterministic enforcement that cannot be ignored

## Best Practices

- Match directory name to `name` field
- Front-load trigger keywords in the description (first 250 chars matter most)
- Focus SKILL.md on overview and principles; link to reference files for depth
- Bundle scripts in `scripts/` and invoke via `${CLAUDE_SKILL_DIR}/scripts/foo.sh`
- Use `context: fork` for skills that should run in isolation
- Use `paths` to scope activation — avoids polluting unrelated work
