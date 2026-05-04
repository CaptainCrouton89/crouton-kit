---
description: Full feature workflow - requirements, design, plan, implement via parallel subagents
argument-hint: <topic or description>
disable-model-invocation: true
---

# Feature Development Pipeline

**Input:** $ARGUMENTS

You orchestrate a full feature development workflow: requirements, design, planning, implementation, review, validation, testing. Dispatch each phase via the Task tool and synthesize results.

## Phase 1a: Requirements

1. Dispatch `rpi:requirements-writer` via the Task tool with the topic/description from the input
2. The agent investigates, drafts, converses with the user, saves, and validates
3. Capture from its return: requirements path, pipeline state path, scope assessment

## Phase 1b: Design

1. Dispatch `rpi:design-lead` via the Task tool. Provide: requirements path, pipeline state path, scope assessment
2. The agent reads, investigates, proposes, converses with the user, saves, and validates
3. Capture from its return: design path, context doc paths (if any), updated scope assessment

## Phase 2: Planning

1. Dispatch `rpi:planning-lead` via the Task tool. Provide: requirements path, design path, pipeline state path, context doc paths (if any), scope assessment
2. The agent works autonomously — creates plan, runs advisor review, validates
3. Capture from its return: plan path, implementation structure, recommended subagent count

## Phase 2.5: Validation Planning

1. Dispatch `rpi:validation-lead` via the Task tool. Provide: requirements path, design path, plan path, context document paths
2. The agent inventories existing infrastructure, proposes reusable tools, writes the validation plan
3. Capture from its return: validation plan path, infrastructure created/reused

## Phase 3: Implementation (repeat per phase)

Read the plan and partition the work:

1. Group the current phase's tasks into **disjoint task groups** — each group owns its files; no two groups edit the same files
   - Use the dependency graph in the plan to enforce ordering between groups when needed
   - Use the planning-lead's recommended subagent count: 2 for ≤4 groups, 3 for 5-8, 4 for 8+

2. Dispatch parallel `devcore:programmer` subagents via the Task tool — one per group
   - Each subagent's prompt includes: the specific tasks for its group, plan path, requirements path, design path, file ownership boundaries, integration points with other groups (shared types, interfaces, APIs with exact contracts), context doc paths
   - Subagents implement and return when done
   - Constraint in every prompt: do not run tests or typechecks (other subagents may be mid-edit)

3. Wait for all subagents in the current dependency layer to complete before launching dependent groups

4. After all phase tasks complete, run Phase Review

### Phase Review (after each major implementation phase)

Run review before proceeding to the next phase or to testing:

1. Dispatch parallel `rpi:reviewer` subagents via the Task tool — scaled to phase change size:
   - Small (<10 files): 1 reviewer covering all concern areas
   - Medium (10-25 files): 2 reviewers, split by concern area (e.g., correctness vs quality)
   - Large (>25 files): 3 reviewers, split by vertical slice or concern area
   - Provide each: file list, plan path, requirements path, design path, assigned concerns

2. Each reviewer returns a structured findings report

3. Synthesize and present consolidated findings to the user:
   - High signal: recommend fixing before continuing
   - Medium/low: user's call

4. For approved fixes, dispatch `devcore:programmer` subagents to apply them. Group fixes by file ownership so subagents don't collide. Provide each: specific fix instructions per issue (what's wrong, where, what the fix should achieve — not exact code).

### Phase Validation (after review fixes, before next phase)

1. Re-dispatch `rpi:validation-lead` with prompt "validate phase N"
2. The agent runs proof scripts and returns pass/fail with evidence
3. If failures: dispatch `devcore:programmer` subagent(s) with the failure evidence to fix
4. Re-invoke validation until all exit criteria pass
5. Only proceed to the next phase when validation passes

If multi-phase plan and more phases remain, return to Phase 3 for the next phase. For very large plans, tell user to clear chat and re-run `/rpi:rpi` instead.

## Phase 4: Testing

After all implementation phases pass review:

1. Read the test plan (`.claude/plans/{topic}.tests.plan.md`) produced by the planning-lead
2. Dispatch a `devcore:programmer` subagent with the test plan
   - Prompt: implement tests per the test plan, referencing the actual implementation (not just the plan). Tests should verify real behavior, not just exercise code paths.
   - This subagent CAN run tests — it's the only one writing code at this point
3. After tests are written, dispatch a `devcore:programmer` subagent (or run yourself) to execute the full test suite and fix any failures
4. Re-dispatch `rpi:validation-lead` with "run full cross-phase validation" — final smoke test across all phases
5. If validation fails, fix and re-validate

State: "Feature complete. Implementation reviewed, tests passing."

## Rules

- Stay in coordination role during implementation — do not implement yourself
- Never skip a phase or proceed without the prior phase completing
- The priority is excellent code, not speed
