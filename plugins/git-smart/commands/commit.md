---
description: Review changes, create logical commits, and push safely
argument-hint: [optional: commit scope]
---

Review my changes and commit them safely.

**Scope:** $ARGUMENTS

## Git State

**Branches:**
```
!`git branch -a 2>/dev/null | head -20`
```

**Status:**
```
!`git status --short`
```

**Staged changes:**
```
!`git diff --cached --stat`
```

**Unstaged changes:**
```
!`git diff --stat`
```

**Recent commits (style reference):**
```
!`git log --oneline -8`
```

## Phase 1: Security & Quality Review

Before any commits, use a **haiku agent** to scan changed files for:

### Blockers (must fix before commit)
- **Secrets**: API keys, tokens, passwords, private keys, .env values
- **Credentials**: AWS keys, database URLs with passwords, auth tokens
- **Merge conflicts**: Unresolved `<<<<<<<`, `=======`, `>>>>>>>` markers
- **Large binaries**: Files >1MB, node_modules, build artifacts

### Warnings (remove unless intentional)
- **Debug code**: `console.log`, `debugger`, `print()`, `var_dump`, `dd()`—unless codebase standard
- **TODO/FIXME**: New ones being added (check diff, not existing code)
- **Commented code**: Large blocks of commented-out code

### Rules Check
The agent should also check changed files against any applicable `.claude/rules/*.md` files. Only flag **clear violations**, not suggestions.

**Agent output**: `BLOCK: <reason>` or `PASS`

If BLOCK: Stop and report. User may instruct you to fix, but do not proceed until user responds.
If PASS: Continue to Phase 2.

## Phase 2: Prep

1. Update `.gitignore` if needed (node_modules, build dirs, .env, etc.)
2. Stage appropriate files

## Phase 3: Commit Strategy

**Small changes** (<3 files, single concern): Single commit
**Large changes** (3+ files, multiple concerns): Group into logical commits

Commit message format: `type(scope): subject`
- Match style from recent commits above
- Types: feat, fix, docs, style, refactor, test, chore

## Phase 4: Push

**Branch check:**
- If on `main`/`master` AND other branches exist: Warn before pushing, suggest creating a branch
- If only branch or on feature branch: Push normally

`git push origin <branch>`

## Output

List commits created with their messages.
