---
description: Validate conclusions/findings with independent verification agents
allowed-tools: Task(*), Read(*), Grep(*), Glob(*)
argument-hint: [context]
---

Validate findings or conclusions from prior analysis. Each major issue gets independent verification.

**Input:** `$ARGUMENTS` or recent conversation context containing findings/conclusions to validate.

**Execution:**
1. Extract major findings (skip trivial/obvious ones)
2. Spawn parallel sonnet agents, one per finding
3. Each agent independently verifies: read relevant code, confirm or refute. Be cognizant of library versions.
4. Report: ✓ confirmed, ✗ refuted, or ⚠ partially correct (with explanation)

**Output:** Validation summary with confidence assessment. Flag any findings that don't hold up under scrutiny.
