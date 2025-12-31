---
description: Comprehensive code review with scaled agent analysis
argument-hint: [scope|plan-path]
---

Review code changes. Scale depth and strategy based on change size.

**Input**: $ARGUMENTS (optional scope: "commit", "branch", or path to plan file)

## 1. Determine Scope

Infer what to review from context (priority order):

1. **Conversation changes** (default): Files modified this session
2. **Uncommitted changes**: Staged + unstaged if no conversation history
3. **Branch changes**: Commits since diverging from main (feature branches)
4. **Last commit**: HEAD changes (fallback)

**Inference rules:**
- Conversation history + changed files → review conversation changes
- Feature branch + commits ahead of main → review branch
- Uncommitted changes only → review those
- If multiple signals conflict, spawn haiku agent to analyze git state and recommend scope

**Ask user only when truly ambiguous** (e.g., dev branch, no conversation history, uncommitted changes could go either way).

## 2. Gather Context

Explore agent collects:
- CLAUDE.md files in affected directories
- Applicable `.claude/rules/*.md` (check `paths` frontmatter)
- Relevant plan file

This agent should return all the instructions, rules, and guidelines relevant to the reviewed code.

## 3. Review Concerns

All reviews must cover these concerns:

- **Edge Cases** — Null/empty/boundary handling, missing conditional branches
- **Dead Code/Bloat** — Unused code, duplication, redundant logic
- **Error Paths** — Useless fallbacks? Right exceptions? Missing error handling?
- **Compliance** — CLAUDE.md/rules adherence, or plan adherence if provided
- **Logic Bugs** (opus) — Incorrect logic, wrong conditions, off-by-one, state bugs
- **Security** (opus) — Injection, XSS, auth issues, data exposure
- **Code Smells** — Anti-patterns, complexity, poor separation
- **Pattern Consistency** — Naming, architecture, conventions vs codebase
- **Idiomatic Code** — Language idioms, modern patterns, best practices

## 4. Scale & Allocate Agents

Choose strategy based on change size and structure:

**Small changes (<10 files, single domain):**
- 3-4 agents, each covering multiple concerns
- Example: Agent 1 (compliance + patterns), Agent 2 (bugs + security, opus), Agent 3 (smells + edge cases + errors)

**Medium changes (10-25 files, mixed domains):**
- 6-8 agents
- Split by concern OR by vertical slice
- Bug detection and security always get dedicated opus agents
- Example: 2 opus (bugs, security), 4 sonnet (compliance, patterns, smells, edge-cases+errors+bloat)

**Large changes (>25 files, multiple features):**
- 8-12 agents
- Prefer vertical slices: each agent reviews all concerns for one feature/module
- PLUS dedicated opus agents for bugs and security across everything
- Don't overload any single agent—split file sets if needed

**Guiding principles:**
- Bug detection agents: max 10-15 files each
- Vertical slice agents: max 8-10 files each
- Concern-focused agents: can handle more files but fewer concerns
- Use opus for logic bugs and security; sonnet for everything else

**Agent output expectations:**
- **Terse for clean code**: If a concern area looks good, one line max ("Edge cases: adequately handled")
- **Detail only for issues**: Full explanation, file:line, evidence only when flagging problems
- Don't explain why correct code is correct—only explain what's wrong and why

## 5. Validate Issues

Validation strategy:
- ~1 validation agent per 3 issues found
- Cluster issues by functionality/files to avoid re-reading same code
- Each validator focuses on one cluster

Validation by type:
- **Bugs/Security**: Opus verifies issue is real and exploitable/broken
- **Compliance**: Sonnet confirms rule applies and is actually violated
- **Smells/Patterns/Idioms**: Sonnet confirms significance (not subjective nitpick)
- **Edge Cases/Errors**: Sonnet verifies the path is actually reachable and unhandled

## 6. Output

```
## Code Review (scope: <type>, <N> files)

### High Signal (blocking)

- **Unvalidated user input in SQL query** [Security]
  `src/db/queries.ts:142` — User-provided `sortBy` interpolated directly into query string.

- **Race condition in cache invalidation** [Logic Bug]
  `src/cache/manager.ts:89` — Cache read and write not atomic; stale data possible under concurrent requests.

### Medium Signal (recommended)

- **Catch block swallows error context** [Error Paths]
  `src/api/handlers.ts:67` — Logs generic message, discards stack trace. Rethrow or log full error.

### Low Signal (optional)

- **Inconsistent naming: `getUserData` vs `fetchUserProfile`** [Pattern Consistency]
  `src/services/user.ts:23` — Other data fetchers use `fetch*` prefix.

---
Found 4 issues: 2 high, 1 medium, 1 low.
Run `/devcore:delegate-fixes` to address.
```

Issue format: `**description** [Concern]` on first line, `file:line` + context on second.

## False Positive Exclusions

Do NOT flag:
- Pre-existing issues (not introduced by these changes)
- Linter-catchable issues
- Subjective style preferences
- Silenced violations (ignore comments)
- Speculative "might be" problems
- Dead code that's actually used (verify before flagging)
