---
name: review-plan
description: Validate implementation plans against requirements and design. Use after creating a plan to ensure full coverage and no ambiguities.
user-invocable: false
allowed-tools: Task
---

# Review Plan Against Requirements and Design

**Input:** `$ARGUMENTS`

Parse input to extract requirements path, design path, and plan path. Expected format: `{requirements-path} {design-path} {plan-path}` or topic name (resolve from `.claude/specs/{topic}/` and `.claude/plans/`).

Spawn a Task agent to review:

```
Task tool parameters:
  subagent_type: general-purpose
  model: sonnet
  description: Review plan against requirements and design
  prompt: |
    Review plan against requirements and design.

    Paths from input: $ARGUMENTS
    - Requirements: `.claude/specs/{topic}/requirements.md`
    - Design: `.claude/specs/{topic}/design.md`
    - Plan: `.claude/plans/*.plan.md`

    ## Process

    1. Read all three documents (requirements first, then design, then plan)
    2. Extract every acceptance criterion from requirements
    3. Extract every architectural decision from design
    4. Map each acceptance criterion to plan coverage: covered, partial, or missing
    5. Verify plan implements the design's architecture (not an alternative approach)
    6. Check plan quality

    **Threshold: Only flag issues that would block implementation or cause genuine confusion.**

    ### Quality Checks
    - Ambiguous language → only if implementation would stall or go wrong
    - Deferred decisions → only if missing info needed to start work
    - Conditional branches → only if unresolved decisions (valid branching is fine)
    - Unexplored complexity → only if it hides surprising work
    - Design divergence → plan contradicts design's architecture without justification

    ## Output

    If all covered and no issues: `PASS`

    If issues exist:
    1. Missing: [acceptance criterion from requirements not in plan]
    2. Design mismatch: [plan diverges from design without justification]
    3. Ambiguous: [unclear section that needs resolution]
```

Report the agent's findings to the user.