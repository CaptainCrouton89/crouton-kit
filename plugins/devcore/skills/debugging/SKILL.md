---
name: debugging
description: Systematic debugging methodologies for hard bugs. Covers rubber ducking, code tracing, hypothesis testing, logging strategies. Use when stuck on bugs that resist quick fixes.
user-invocable: true
---

# Debugging Hard Bugs

## Rubber Ducking

Quote code snippets and explain what each chunk *should* do vs *actually* does. Don't assume—verbalize the logic. Discrepancies reveal bugs.

## Code Flow Tracing

Trace data from entry point to failure. At each transformation: what goes in, what comes out? Mark where expectations diverge.

**Failure-prone boundaries:** async, serialization, type coercion, null propagation, state mutations.

## Hypothesis Testing

1. List 3-5 possible causes
2. List 3-5 assumptions you're making
3. Test to eliminate possibilities
4. Repeat until one remains

**Don't** change code hoping it helps—that creates noise.

## Logging

Log at decision points and async boundaries, not everywhere.

**Workflow:**
1. Add targeted logs
2. Have user perform action and report output
3. Diagnose and fix
4. **After user confirms fix works:** remove all added logging

## Agent Investigation

For complex/unfamiliar code sections acting as a blackbox:

- Spawn an Explore agent to trace a specific code path and report back
- Run agents in background while continuing other investigation

**When stuck:** Spawn 2-3 senior-advisor agents in parallel with different perspectives (pragmatist, architect, skeptic).

**Avoid biasing agents:** Pass them relevant file paths and the observed behavior, but *not* your hypotheses or assumptions. Let them form independent conclusions.

## Before Fixing

- [ ] Identified exact failing line(s)?
- [ ] Understand *why* it fails?

If no, keep investigating.

## Related

- [Frontend Debugging](./frontend.md)
