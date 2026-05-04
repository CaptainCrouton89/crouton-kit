---
description: After /rpi/plan - execute with parallel subagents
argument-hint: <plan-path or description>
---
# Implement Plan

**Input:** $ARGUMENTS

Parse the input above. It may be:
- A direct path to a plan file
- A topic name (look in `.claude/plans/{topic}.plan.md`)
- A description with guidance on what to prioritize, skip, or handle differently

Extract the plan reference and any implementation guidance.

## Objective

Execute the implementation plan using parallel `devcore:programmer` subagents dispatched via the Task tool. Maximize parallelism while respecting dependencies. Each subagent owns disjoint files.

## Process

### 1. Read the Plan

- Load the plan document provided as input
- If the plan references sub-plans (large multi-phase plans), **implement only the current phase**
- Extract the task list, dependency graph, and integration points

### 2. Assess Scale & Subagent Count

Count the plan's independent task groups (tasks with no mutual dependencies that can run in parallel).

| Independent groups | Files touched | Strategy |
|-------------------|---------------|----------|
| 1-3               | 1-5           | Implement directly or single subagent |
| 2-4               | 5-15          | **2 parallel subagents** |
| 4-8               | 10-30         | **3 parallel subagents** |
| 8+                | 25+           | **4 parallel subagents** (cap) |

Use the higher of the two columns to pick the tier. Never spawn more subagents than independent task groups.

**Scale-up signals** (bump one tier): shared interfaces requiring tight coordination, multiple languages/frameworks, or changes spanning both infrastructure and application layers.

For small plans, dispatch a single `devcore:programmer` subagent (or implement directly) and skip to Phase Completion.

### 3. Partition Tasks

Group tasks into disjoint sets where:
- Each group owns clear file boundaries (no two groups edit the same files)
- Within a group, tasks can be done sequentially by one subagent
- Across groups, dependencies are expressed as ordering layers (run dependent groups after their predecessors complete)

If two tasks must edit the same file, sequence them in the same group.

### 4. Dispatch Parallel Subagents

For each task group in the current dependency layer, dispatch a `devcore:programmer` subagent in parallel via the Task tool.

**Each subagent's prompt must include:**
- The specific tasks from the plan it owns
- The plan path and relevant context paths (`.claude/context/`, spec, plan)
- File ownership boundaries (which files this subagent owns)
- Integration points with other groups (shared types, interfaces, APIs — exact contracts)
- Constraint: do not run tests or typechecks — other subagents may be mid-edit
- Instruction to return when its tasks are complete, surfacing any issues encountered

### 5. Coordinate

Wait for all subagents in the current layer to return.

- If any subagent reports a blocker, assess: resolve yourself, adjust the plan, or escalate to user
- After a layer completes, dispatch the next layer of dependent groups
- Surface progress to the user periodically

Stay in a coordination role — do not implement tasks yourself unless a subagent returns blocked work.

### 6. Phase Completion

When all tasks in the plan's current phase are complete, state: "Phase {N} implementation complete. Ready for code review or continue to next phase."

**Do not** automatically proceed to the next phase — allow the user to review first.

## Notes

- For large plans, expect to run `/rpi:implement` multiple times (once per phase). Don't run it yourself — just do the first sub-plan, and tell the user to clear chat and run `/rpi:implement` again.
- Keep the user informed of progress, especially for long-running implementations
- The priority is excellent code. Completion of all work should never come at the cost of cut corners.
- **File conflicts:** Structure task ownership so subagents don't edit the same files. If unavoidable, sequence those tasks into the same group.
