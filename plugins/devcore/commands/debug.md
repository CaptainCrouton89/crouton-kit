---
description: Diagnose root cause of an issue using adaptive multi-perspective investigation. Use when debugging bugs, errors, test failures, or unexpected behavior — especially intermittent, cross-module, or "stuck" problems where a single-pass read isn't enough.
argument-hint: <description of issue / further advice>
---

Debug the issue described in `$ARGUMENTS` and/or recent conversation context. Diagnose root cause—don't fix.

## Phase 1: Reconnaissance

Read the key files yourself—don't delegate this. You need firsthand context to coordinate effectively.

- Entry points and failure points
- Data flow through the bug area
- `git log`/`git blame` near the failure (recent changes are high-signal)
- Error messages, stack traces, or symptoms

## Phase 2: Assess Difficulty & Scale Response

Based on recon AND user's language, classify and spawn:

### Simple (clear error, obvious area, likely 1 cause)
Investigate solo. Use Explore subagents for code tracing if the area is large.

### Medium (unclear cause, multiple possible origins, crosses 2-3 modules)
Spawn **2-3 parallel subagents** (`devcore:senior-advisor`), each with a *concrete task* (not just a vague perspective):
- **Data Flow Tracer**: "Trace the value of X from [entry point] through [these files] to [failure point]. Report every transformation and where the value diverges from expected."
- **Assumption Auditor**: "List every assumption this code makes about [types/nullability/ordering/timing/env]. For each, find evidence it holds or could be violated."
- **Change Investigator**: "Run `git log` and `git blame` on [these files]. Identify changes in the last N commits that touch the failure area. Flag regressions or behavioral changes."

### Hard (intermittent, race conditions, user says "nasty"/"impossible"/"been stuck", crosses many modules)
Dispatch **3-5 parallel `devcore:senior-advisor` subagents** via the Task tool. Each gets precise scope—not vague roles:
- **End-to-End Tracer**: Trace data from system entry to failure, documenting every transformation, boundary crossing, and state mutation
- **Assumption Breaker**: Enumerate and systematically test every assumption—types, null, ordering, timing, env vars, config, dependency versions
- **Git Archaeologist**: `git log`/`git blame`/`git bisect` the failure area. Correlate changes with when the bug was first reported. Check dependency updates.
- **Boundary Inspector**: Focus exclusively on async boundaries, serialization/deserialization, external service calls, shared mutable state, and concurrency
- **Reproducer** *(if applicable)*: Write a minimal failing test or reproduction script that isolates the bug

After all subagents return, **challenge their theories against each other**. When one posts a hypothesis, look for evidence in the others that disproves it. The theory that survives is most likely correct. If hypotheses conflict and evidence is thin, dispatch a follow-up subagent to test the most likely candidate.

**Scale-up signals:**
- User language: "nasty", "intermittent", "been stuck", "impossible", "no idea", "weird", "flaky"
- Recon reveals: race conditions, shared mutable state, multiple interacting systems, no clear error message
- Failure is non-deterministic or environment-dependent

## Phase 3: Synthesize & Report

After investigation completes:

1. **Root Cause**: Exact failing line(s) and *why* it fails
2. **Evidence**: Code snippets, data flow, git blame findings
3. **Confidence**: High / Medium / Low — if not high, state what's uncertain
4. **Recommended Fix**: Concrete approach, not vague direction

If root cause isn't found, report what was eliminated and what remains to investigate.

## Constraints

- **No code changes**—investigate only (reproduction tests are the exception)
- **Don't bias investigators**: Give them file paths, observed behavior, and concrete tasks. Do NOT share your hypotheses—let them form independent conclusions.
- **Isolated contexts**: Investigators run in forked contexts. They return clean summaries, not raw output. Don't let noisy debug output pollute the orchestrator.
- Prefer `git blame`/`git log` to understand how code arrived at its current state
