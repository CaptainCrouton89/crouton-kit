---
description: Audit codebase for structural issues and design stupidisms
allowed-tools: Task(*), Glob(*), Grep(*), Read(*)
argument-hint: [path]
---

Audit for "design stupidisms"—code that works but doesn't make sense. Focus on structural waste, not style.

**Target:** `$ARGUMENTS` (default: entire codebase, excluding vendor/generated/fixtures)

**Categories:**
- Unnecessary abstraction/indirection
- Purposeless state or config
- Cargo-culted patterns
- Clever-but-confusing code
- Dead/unreachable logic
- Overly defensive code against impossible scenarios

**Execution:**
1. Identify top-level directories/verticals in target
2. Spawn parallel sonnet agents, one per vertical
3. Each agent reports: `file:line`, issue, why it's dumb, severity (high/med/low)
4. Consolidate all findings into single prioritized list (high → low)

**Output:** Prioritized findings table. All severities shown, but narrative focuses on high-impact structural issues worth fixing.
