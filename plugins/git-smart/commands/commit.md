---
description: Stage and commit changes into logical commits
argument-hint: [scope] [--push] [--all] [--pr]
allowed-tools: Bash(git:*), SlashCommand(/git-smart:pr:*)
disable-model-invocation: true
---

Stage and commit changes into logical commits.

**Args:** $ARGUMENTS

Parse flags from args:
- `--push` → push to remote after committing
- `--all` → commit ALL uncommitted changes (not just conversation-relevant ones)
- `--pr` → after committing, run the `/git-smart:pr` command to open a PR
- Remaining positional text → scope filter

## Context

**Git repo:** !`git rev-parse --is-inside-work-tree 2>/dev/null || echo "NOT_A_GIT_REPO"`

If "NOT_A_GIT_REPO": check for git repos in immediate subdirectories. If found, commit changes in each repo that has uncommitted work. If none found, inform the user and stop.

**Status:**
```
!`git status --short 2>/dev/null || true`
```

**Recent commits (style reference):**
```
!`git log --oneline -n 8 2>/dev/null || true`
```

## Process

### 1. Determine change set

- **Default (no `--all`):** Only stage files relevant to what was discussed or worked on in this conversation. Ignore unrelated dirty files.
- **`--all`:** Stage everything. For files that shouldn't be committed (build artifacts, secrets, temp files), either add them to `.gitignore` or `git checkout`/delete them so working tree is **clean** when done. **Ask the user before deleting or reverting any files.**
- **Scope provided:** Further filter to files matching the scope.

### 2. Stage & analyze

Stage the determined files. Review staged diff for logical groupings.

### 3. Commit

Create commits. Small changes (<3 files, single concern) = single commit. Large changes = group into logical commits.

**Format:** `type(scope): subject`
- Match style from recent commits
- Types: feat, fix, docs, style, refactor, test, chore

### 4. Push (if `--push`)

Run `git push`. If no upstream, use `git push -u origin HEAD`.

### 5. Clean up (if `--all`)

Verify `git status --short` is empty. If not, resolve remaining files (gitignore or remove) until status is clean.

### 6. Create PR (if `--pr`)

Invoke the `/git-smart:pr` command via the SlashCommand tool. It handles pushing the branch, creating the PR, and monitoring CI. Forward any args the user provided that `/pr` understands (target branch, `--merge`/`--rebase`, `-a`).

## Output

List commits created with their messages. If pushed, include remote and branch. If `--pr`, include the PR URL.
