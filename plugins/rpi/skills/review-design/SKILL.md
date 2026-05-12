---
name: review-design
description: Validate technical designs against requirements for coverage, feasibility, and architectural soundness. Use after creating a design.
user-invocable: false
allowed-tools: Task, Read, Grep, Glob
---

# Review Design

**Input:** `$ARGUMENTS`

Parse input to extract design path and requirements path. Expected format: `{design-path} {requirements-path}` or just `{design-path}` (infer requirements from same topic directory).

## Phase 1: Requirements Coverage

Designs that skip requirements produce elegant architectures that solve the wrong problem.

Spawn a Task agent to verify the design addresses all requirements:

Task tool parameters:
  subagent_type: general-purpose
  model: sonnet
  description: Design-requirements coverage check
  prompt: |
    Check that the design covers all requirements.

    Input: $ARGUMENTS
    - Design: the design.md file
    - Requirements: the requirements.md file (same topic directory, or provided explicitly)

    ## Process

    1. Read requirements file — extract every user story and acceptance criterion
    2. Read design file
    3. Map each acceptance criterion to design coverage: covered, partial, or missing
    4. A criterion is "covered" if the design's architecture, components, data models, or error handling would enable an implementer to satisfy it without guessing

    ## Output

    If all covered: `PASS`

    If gaps exist:
    - Missing: [acceptance criterion not addressed by design]
    - Partial: [criterion partially covered — what's missing]

If coverage check fails, report issues and stop.

## Phase 2: Flow Simulation

**You (the main agent) do this phase directly — do not delegate.**

This is the highest-signal review activity. Most design gaps hide in the seams between components.

### Process

1. **Read the design and requirements.**

2. **Read critical related files** — just the ones defining runtime contracts the design depends on:
   - Data models (schemas, types) the design creates or reads
   - Services/endpoints the design extends
   - State machines or lifecycle code the design participates in

3. **Construct the step-by-step journey.** Write out the flow from trigger to final state — every user action, system reaction, state change. Include happy path and important alternate paths.

4. **At each step, check:**

   | Check | Question | Example gap |
   |-------|----------|-------------|
   | **Preconditions** | What must be true for this step? Is it guaranteed by the design? | "Design creates a record but doesn't specify what happens if the parent doesn't exist" |
   | **State consistency** | Does the system interpret state correctly at each point? | "Component A sets status to PENDING but Component B only handles ACTIVE and COMPLETE" |
   | **Failure** | What happens if this step fails? Is recovery defined? | "If the API call fails, the design doesn't say whether to retry or surface the error" |
   | **Handoff** | Does this step's output match the next step's expected input? | "Service returns a list but the consumer expects a single item" |

5. **Report findings.** For each gap: what step, what's missing, what would go wrong during implementation.

If no gaps: `PASS — flow simulation found no gaps.`

## Phase 3: Feasibility Review

A design can cover all requirements and flow correctly but still be unbuildable — incompatible with existing patterns, impossible data model, or components that can't actually connect.

Spawn a Task agent to check architectural feasibility:

Task tool parameters:
  subagent_type: general-purpose
  model: sonnet
  description: Design feasibility review
  prompt: |
    Review the design for architectural feasibility.

    Design path: [from $ARGUMENTS]

    ## Process

    1. Read the design file
    2. Read related files listed in the design
    3. Read CLAUDE.md and .claude/rules/*.md for project patterns
    4. Check:
       - **Pattern compatibility**: Does the design follow or reasonably extend existing patterns? Flag contradictions with established conventions.
       - **Component boundaries**: Are responsibilities clear? Would two teams implementing different components know exactly where one ends and the other begins?
       - **Data model soundness**: Are schemas consistent with existing models? Are relationships, constraints, and validation rules well-defined?
       - **Integration feasibility**: Can the proposed components actually connect as described? Are there missing adapters, transformations, or protocol mismatches?

    ## Critical Rules

    - If the design is sound, report PASS.
    - Do NOT fabricate concerns or suggest alternatives that aren't clearly better.
    - Do NOT flag: subjective architecture preferences, speculative scaling concerns, things the planner will naturally resolve.
    - Threshold: Would an implementer discover that the design can't work as described?

    ## Output

    If no issues: `PASS — design is feasible and compatible with existing patterns.`

    If issues exist:
    - **{issue}** — {what's wrong or incompatible} → {what would break during implementation}

## Phase 4: Aggregate

Multiple phases catching the same gap is signal — those are the issues most likely to cause implementation failure.

Collect results from all phases. Drop PASS results.

If all phases pass: report `PASS` to the user.

If issues found:
- Deduplicate (flow simulation and feasibility may flag the same gap)
- Group by severity: issues found by multiple phases are highest signal
- Present each issue with: which phase found it, the gap, and the implementation risk
- Keep the report concise
