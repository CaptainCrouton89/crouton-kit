---
description: Perform a comprehensive review of code changes
argument-hint: <branch|commit>
---

Provide a code review for the code changes based on the scope argument:

- **commit** (default): Review changes since the last commit (uncommitted changes via `git diff HEAD`, or last commit via `git diff HEAD~1` if no uncommitted changes)
- **branch**: Review all changes since the current branch diverged from the main branch (use `git merge-base HEAD main` or `git merge-base HEAD dev` to find the divergence point, then `git diff <merge-base>..HEAD`)

To do this, follow these steps precisely:

1. Launch a haiku agent to determine the diff scope and check preconditions:
   - If scope is "branch": Find the merge-base with main/dev branch and verify there are changes to review
   - If scope is "commit" or unspecified: Check for uncommitted changes, fall back to last commit if none
   - Return early if there are no changes to review or changes are trivial (e.g., only whitespace, only comments)

2. Launch a haiku agent to return a list of file paths (not their contents) for all relevant instruction files:

   **CLAUDE.md files:**
   - The root CLAUDE.md file, if it exists
   - Any CLAUDE.md files in directories containing modified files

   **Rules files (.claude/rules/*.md):**
   - All rules files in `.claude/rules/` (recursively)
   - For each rule file, note the `paths` frontmatter field if present (glob pattern that scopes the rule to specific files)
   - Rules without a `paths` field apply to all files
   - Rules with a `paths` field only apply to files matching that glob pattern

3. Launch a sonnet agent to view the diff and return a summary of the changes

4. Launch 7 agents in parallel to independently review the changes. Each agent should return the list of issues, where each issue includes a description and the reason it was flagged (e.g. "CLAUDE.md adherence", "bug", "code smell"). The agents should do the following:

   **Agents 1 + 2: Instruction compliance sonnet agents**
   Audit changes for CLAUDE.md and rules compliance in parallel. Note: When evaluating compliance for a file:
   - Only consider CLAUDE.md files that share a file path with the file or parents
   - Only consider rules files where the file matches the rule's `paths` glob pattern (or the rule has no `paths` field)

   **Agents 3 + 4: Bug detection opus agents**
   Agent 3: Scan for obvious bugs. Focus only on the diff itself without reading extra context. Flag only significant bugs; ignore nitpicks and likely false positives. Do not flag issues that you cannot validate without looking at context outside of the git diff.
   Agent 4: Look for problems that exist in the introduced code. This could be security issues, incorrect logic, etc. Only look for issues that fall within the changed code.

   **Agent 5: Code smells sonnet agent**
   Look for anti-patterns, unnecessary complexity, or maintainability concerns in the changed code. Focus on:
   - Overly complex logic that could be simplified
   - Code duplication introduced by the changes
   - Poor separation of concerns
   - Hard-coded values that should be configurable

   **Agent 6: Pattern consistency sonnet agent**
   Analyze whether the changes follow established codebase patterns. This agent should read surrounding code to understand existing patterns, then verify the new code follows them. Look for:
   - Naming conventions used elsewhere in the codebase
   - Architectural patterns (e.g., how similar features are structured)
   - Error handling patterns
   - Import/export conventions

   **Agent 7: Best practices sonnet agent**
   Check for violations of language idioms, security concerns, or performance issues:
   - Language-specific best practices and idioms
   - Obvious security vulnerabilities (injection, XSS, etc.)
   - Performance anti-patterns (N+1 queries, unnecessary re-renders, etc.)
   - Missing error handling at system boundaries

   **CRITICAL: We only want HIGH SIGNAL issues.** This means:
   - Objective bugs that will cause incorrect behavior at runtime
   - Clear, unambiguous CLAUDE.md or rules violations where you can quote the exact rule being broken
   - Obvious code smells that significantly impact maintainability
   - Clear pattern violations where you can point to the established pattern being broken
   - Concrete best practice violations with demonstrable impact

   We do NOT want:
   - Subjective concerns or "suggestions"
   - Style preferences not explicitly required by CLAUDE.md or rules
   - Potential issues that "might" be problems
   - Anything requiring interpretation or judgment calls
   - Minor code smells that are debatable

   If you are not certain an issue is real, do not flag it. False positives erode trust and waste reviewer time.

5. For each issue found in the previous step, launch parallel subagents to validate the issue. These subagents should get a description of the issue. The agent's job is to review the issue to validate that the stated issue is truly an issue with high confidence.

   Validation approach by issue type:
   - **Bugs**: Opus subagent verifies the bug is real (e.g., "variable is not defined" - check if actually undefined)
   - **Instruction violations**: Sonnet subagent validates the rule is scoped for this file (CLAUDE.md in path hierarchy, or rules file with matching `paths` glob) and is actually violated
   - **Code smells**: Sonnet subagent confirms the smell is significant and not a false positive
   - **Pattern violations**: Sonnet subagent verifies the established pattern exists and is actually being violated
   - **Best practice violations**: Sonnet subagent confirms the violation has real impact

6. Filter out any issues that were not validated in step 5. This step will give us our list of high signal issues for our review.

7. Finally, output the code review results to the terminal.
   When writing your output, follow these guidelines:
   a. Keep your output brief
   b. Avoid emojis
   c. Reference relevant code, files, and line numbers for each issue
   d. For each issue type, use the appropriate citation format:
      - Instruction violations: Quote the exact text (e.g., CLAUDE.md says: "..." or .claude/rules/api.md says: "...")
      - Bugs: Explain the bug concisely (e.g., bug: variable `foo` is used before initialization)
      - Code smells: Name the smell (e.g., code smell: deeply nested conditionals reduce readability)
      - Pattern violations: Reference the pattern (e.g., pattern violation: other handlers use `try/catch`, this one doesn't)
      - Best practices: Name the violation (e.g., best practice: SQL query is vulnerable to injection)

Use this list when evaluating issues in Steps 4 and 5 (these are false positives, do NOT flag):

- Pre-existing issues (code that existed before the current changes)
- Something that appears to be a bug but is actually correct
- Pedantic nitpicks that a senior engineer would not flag
- Issues that a linter will catch (do not run the linter to verify)
- General code quality concerns (e.g., lack of test coverage, general security issues) unless explicitly required in CLAUDE.md or rules
- Issues mentioned in CLAUDE.md or rules but explicitly silenced in the code (e.g., via a lint ignore comment)

Notes:

- For "commit" scope: Use `git diff HEAD` for uncommitted changes, or `git diff HEAD~1` for last commit if no uncommitted changes
- For "branch" scope: Use `git merge-base HEAD main` (or dev) to find divergence point, then `git diff <merge-base>..HEAD`
- Create a todo list before starting
- You must cite and reference each issue with file path and line number
- For your final output, follow the following format precisely (assuming for this example that you found 3 issues):

---

## Code Review (scope: <commit|branch>)

Found 5 issues:

1. <brief description of issue> (CLAUDE.md says: "<exact quote>")
   - File: `path/to/file.ts:42-45`

2. <brief description of issue> (.claude/rules/api.md says: "<exact quote>")
   - File: `path/to/other/file.ts:17`

3. <brief description of bug> (bug: <explanation>)
   - File: `path/to/another/file.ts:88-92`

4. <brief description> (code smell: <explanation>)
   - File: `path/to/file.ts:100-115`

5. <brief description> (pattern violation: <established pattern> vs <what was done>)
   - File: `path/to/file.ts:50-55`

---

- Or, if you found no issues:

---

## Code Review (scope: <commit|branch>)

No issues found. Checked for bugs, instruction compliance, code smells, pattern consistency, and best practices.

---
