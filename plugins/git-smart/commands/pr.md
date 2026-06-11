---
description: Create PR, optionally merge/rebase target, monitor CI, fix failures
argument-hint: [target-branch] [--merge | --rebase] [-a] — -a enables autonomous fix/repush loop
---

Create a pull request and optionally integrate the target branch first. Monitor CI checks and report results.

With `-a`: autonomously diagnose failures, fix, repush, and repeat until CI passes or iteration cap is hit.
Without `-a`: report CI results and stop. Ask the user before taking action.

**Target branch:** ${1:-main}
**Flags:** $ARGUMENTS
- `--merge` or `--rebase` — integrate target into current branch before PR
- `-a` — enable autonomous fix/repush loop

## Context

**Working directory:** !`pwd`
**Git root:** !`git rev-parse --show-toplevel 2>/dev/null || echo "NOT A GIT REPO"`

If not inside a git repository, ask the user which repo they want to target. Do not proceed blindly.

**Current branch:**
```
!`git branch --show-current 2>/dev/null || echo "N/A"`
```

**Commits to include:**
```
!`git log --oneline origin/${1:-main}..HEAD 2>/dev/null || echo "N/A"`
```

**Changed files:**
```
!`git diff --stat origin/${1:-main}..HEAD 2>/dev/null || echo "N/A"`
```

## Safety

- Force-push only when necessary after a rebase (use `--force-with-lease`). Never force-push otherwise.
- **Never run destructive commands** (`git checkout -- .`, `git restore`, `git reset --hard`, `git clean`, `git revert`) without explicit user confirmation.
- **Without `-a`:** After CI results come in, report them and wait for user direction.
- **With `-a`:** Confirm with the user before starting the loop. Summarize what will happen. Then:
  - If a fix requires non-trivial design decisions or the same check has failed twice, **stop and ask the user**.
  - Cap at **5 fix-repush iterations** before stopping.

## Process

### 1. Ensure on a feature branch

If the current branch is the same as the target branch (e.g. both `main`), create a new branch before proceeding. Derive the name from the uncommitted changes or recent commits (e.g. `feat/add-auth-middleware`). Push and switch to it.

### 2. Integrate target (if `--merge` or `--rebase`)

If a merge strategy was provided:
- Fetch origin
- Run `git merge origin/${1:-main}` or `git rebase origin/${1:-main}`
- Resolve conflicts if trivial; otherwise stop and ask
- Push updated branch (after rebase, use `git push --force-with-lease`)

### 3. Create PR

- Push current branch if needed
- Analyze all commits for PR summary
- `gh pr create` with title + body:

```
gh pr create --title "..." --body "$(cat <<'EOF'
## Summary
<1-3 bullet points covering ALL commits>

## Test plan
<checklist>
EOF
)"
```

### 4. Monitor CI

Use `gh pr checks <pr-url> --watch` to wait for checks, then `gh pr checks <pr-url>` to inspect results.

**Without `-a`:** Report check results and stop. Let the user decide next steps.

**With `-a` (autonomous mode):**

```
iteration = 0
while PR is open and iteration < 5:
  wait for checks to complete (gh pr checks --watch)
  if all checks pass:
    report success, done
  else:
    read logs: gh run view <run-id> --log-failed
    identify failing check(s) and root cause
    fix the code
    commit, push
    iteration++
if iteration == 5:
  stop and report status to user
```

### 5. Done

Report final PR URL and status.
