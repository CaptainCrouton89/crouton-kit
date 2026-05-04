---
description: Code review, quality audit, and fix delegation with parallel subagents
argument-hint: [path] [review|audit|fix|full]
disable-model-invocation: true
---

Analyze and fix code using parallel subagents dispatched via the Task tool. Mode and effort scale to input.

## Mode Detection

Infer from `$ARGUMENTS` (first match wins):

| Input | Mode | Example |
|-------|------|---------|
| `fix` (alone or with prior findings) | **Fix** | `/review fix` |
| Path without `review` keyword | **Audit** | `/review src/auth/` |
| `full` | **Audit** (entire codebase) | `/review full` |
| Path + `review` | **Review** (scoped) | `/review src/auth/ review` |
| *(no args, uncommitted changes exist)* | **Review** | `/review` |
| *(no args, clean tree)* | **Audit** (entire codebase) | `/review` |

Explicit mode keyword always overrides inference.

---

## Phase 1: Context Gathering

Runs before any analysis mode. Dispatch one Explore subagent via the Task tool to collect:

- CLAUDE.md files and applicable `.claude/rules/*.md` from affected directories
- Relevant plan files or design docs
- **Review mode only**: PR description, linked tickets, commit messages
- Codebase conventions: naming patterns, error handling style, architecture norms

Share gathered context with all subsequent subagents via their dispatch prompts.

## Phase 2: Classification

Classify the target to determine review depth:

| Change Type | Depth | Rationale |
|-------------|-------|-----------|
| Hotfix / security patch | **Maximum** | High-risk, time-pressured |
| New feature | **Standard** | Balanced |
| Refactor | **Behavior-focused** | Verify equivalence only |
| Test-only | **Intent-focused** | Are tests checking developer intent or AI assumptions? |
| Documentation | **Minimal** | Low risk |

Classification informs subagent scaling and which concerns get opus vs sonnet.

---

## Mode: Review

Analyze code **changes** for correctness, security, and quality.

### Scope

Infer from context (first match wins):

1. **Post-implementation** — If this conversation made code changes, review exactly those files/changes. Don't ask.
2. **Uncommitted changes** — If working tree is dirty, review the diff. Don't ask.
3. **Ambiguous** — No conversation changes and clean tree. Ask: recent commits, branch diff vs main, or specific path?

### Concerns (ordered by AI risk multiplier)

| Concern | Model | AI Risk | Focus |
|---------|-------|---------|-------|
| Security | opus | 2.74× | Input validation, XSS, injection, auth, deserialization, credential handling |
| Error Handling | opus | 2× | Missing guardrails, swallowed errors, no cleanup in error paths, generic catch blocks |
| Logic Bugs | opus | 1.75× | Incorrect conditions, off-by-one, state bugs, operation ordering, edge cases |
| Over-engineering | sonnet | high | Abstractions without justification, defensive code against impossible states, premature patterns |
| Dead Code/Bloat | sonnet | 1.64× | Unused code, duplication (4× with AI), redundant logic |
| Compliance | sonnet | — | CLAUDE.md/rules/plan adherence |
| Pattern Consistency | sonnet | — | Naming, architecture, conventions vs codebase |

### Subagent Scaling

Dispatch subagents in parallel via the Task tool:

| Change Size | Subagent tasks | Grouping |
|-------------|----------------|----------|
| Small (<10 files) | 3-4 | Grouped concerns |
| Medium (10-25 files) | 6-8 | Split by concern or vertical |
| Large (>25 files) | 8-12 | Vertical slices + cross-cutting opus tasks |

### Validation Phase

After review subagents return, dispatch validation subagents (~1 per 3 issues):
- **Bugs/Security** (opus): Confirm issue is real and exploitable/broken
- **Everything else** (sonnet): Confirm significance — reject subjective nitpicks

### False Positive Exclusions

Do NOT flag:
- Pre-existing issues outside the diff
- Linter-catchable issues (formatting, import order)
- Subjective style preferences
- Silenced violations with documented rationale
- Speculative problems without evidence
- "Improvements" to working code not in scope

---

## Mode: Audit

Scan codebase or path for **structural issues** — code that works but shouldn't exist.

### Target

`$ARGUMENTS` path, or entire codebase (excluding vendor/generated/fixtures/node_modules).

### Concerns

**AI-Generated Structural Waste:**
- Cargo-culted patterns — applied because training data had them, not because they're needed
- Over-abstraction — enterprise patterns on simple problems
- Defensive coding against impossible states — null checks on non-nullable paths, error handling for unreachable code
- Hallucinated dependencies — imports/patterns referencing things that don't exist or aren't used
- Duplicate functionality — reimplementing what already exists in the codebase (4× more common with AI)

**General Structural Issues:**
- Unnecessary indirection / wrapper layers
- Purposeless state or config
- Clever-but-confusing code
- Dead/unreachable logic
- Feature flags / backwards-compat shims with no migration plan
- Redundant validation at internal boundaries (validate at edges, trust internals)

### Subagent Scaling

Dispatch subagents in parallel via the Task tool:

| Scope | Tasks | Assignment |
|-------|-------|------------|
| Single directory | 1-2 sonnet | By file cluster |
| Small project (<10 dirs) | 3-5 sonnet | One per top-level dir |
| Large project (10+ dirs) | 6-10 sonnet | One per vertical, plus 1 opus cross-cutting |

Each subagent reports: `file:line`, issue, why it's wrong, severity (high/med/low).

---

## Mode: Fix

Delegate fixes for issues identified **in this conversation**. If no issues exist, inform user and stop.

### Process

1. **Categorize** issues from prior analysis:
   - **Obvious** — One clear fix. Single file or mechanical change.
   - **Likely** — Tradeoffs exist but one approach recommended.
   - **Complex** — Design decisions or architectural impact.

2. **Propose** — Present categorized list. Wait for approval.

3. **Execute** — Dispatch fix subagents via the Task tool:
   - **Obvious**: haiku subagents in parallel
   - **Likely**: haiku subagents or `devcore:programmer` based on scope
   - **Complex**: Offer `devcore:senior-advisor` for analysis first, then `devcore:programmer` for implementation

4. **Skip subagents for <3 simple changes** — implement directly.

---

## Synthesis (Judge Layer)

Before producing final output, synthesize all subagent findings:

1. **Deduplicate** — Merge overlapping observations from different subagents
2. **Resolve conflicts** — When subagents disagree, weigh tradeoffs and pick one position
3. **Filter** — Remove low-confidence findings, subjective preferences, and false positives
4. **Prioritize** — Rank by: severity × confidence × AI risk multiplier
5. **Evidence check** — Every finding must cite `file:line` and concrete evidence

Target: <10% false positive rate. If unsure, drop the finding.

## Output Format

All modes produce the same structure:

```
## [Review|Audit] — <scope>, <N> files, depth: <standard|maximum|behavior>

### Critical

- **Issue title** [Category]
  `file:line` — Evidence and explanation.

### High

- **Issue title** [Category]
  `file:line` — Evidence and explanation.

### Medium

- **Issue title** [Category]
  `file:line` — Evidence and explanation.

---
Found N issues: X critical, Y high, Z medium. (Low-confidence findings filtered.)
Run `/review fix` to address.
```

No "low signal" tier — if it's not worth acting on, don't report it.

Fix mode outputs a completion summary per issue.

## Workflow

1. Dispatch context-gathering subagent (Explore)
2. Classify change type and depth
3. Partition work per scaling rules
4. Dispatch parallel subagents via Task tool
5. Collect results; dispatch validation subagents (review mode only)
6. Synthesize: deduplicate, filter, prioritize
7. Present consolidated output
