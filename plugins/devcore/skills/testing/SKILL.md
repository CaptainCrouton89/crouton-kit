---
name: testing
description: Test writing and fixing methodology. Covers TDD, investigating failures, and delegating fixes to agents. Use when writing tests or diagnosing test failures.
user-invocable: true
---

# Writing and Fixing Tests

## Investigate First

A failing test signals one of two things:
1. **The test is wrong** — outdated expectations, flaky setup, incorrect assertions
2. **The code is broken** — regression, missing edge case, integration failure

**Don't assume.** Read the failure, trace the code path, determine which is true before changing anything.

**Common signs the test is wrong:**
- Assertions don't match documented behavior
- Test relies on implementation details that changed intentionally
- Flaky failures that pass on retry

**Common signs the code is broken:**
- Test matched previously working behavior
- Multiple tests fail in related areas
- Error messages indicate actual bugs (null refs, type errors, missing data)

## TDD

When adding new functionality, write tests first:

1. **Red** — Write a failing test that specifies the behavior
2. **Green** — Write minimal code to pass the test
3. **Refactor** — Clean up while tests stay green

Benefits:
- Forces you to clarify requirements before coding
- Prevents over-engineering (you only write what's needed)
- Catches regressions immediately

**Skip TDD when:** fixing obvious bugs, exploratory prototyping, or when the test setup cost exceeds the implementation.

## Delegating Test Fixes

When using agents to fix test failures:

1. **Agent makes the fix and exits** — no test execution
2. **Orchestrator runs tests** after agent returns
3. **Repeat** if failures remain

**Why agents don't run tests:**
- Prevents chasing cascading failures
- Avoids wasted context on test output parsing
- Forces agents to report blockers instead of attempting workarounds

**In agent instructions, include:**
```
Fix the failing test. Do NOT run the test suite—make your change and exit.
```

If an agent encounters ambiguity about whether to fix the test or the code, it should stop and report a blocker.

## Before Fixing

- [ ] Read the failure message and stack trace?
- [ ] Identified whether test or code is wrong?
- [ ] Understand the expected vs actual behavior?

If no, keep investigating.
