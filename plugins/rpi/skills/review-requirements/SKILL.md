---
name: review-requirements
description: Validate requirements documents for EARS compliance, completeness, and consistency. Use after creating requirements.
user-invocable: false
allowed-tools: Task, Read, Grep, Glob
---

# Review Requirements

**Input:** `$ARGUMENTS`

Parse input to extract the requirements file path.

## Phase 1: Structural Validation

Spawn a Task agent to check requirements quality:

Task tool parameters:
  subagent_type: general-purpose
  model: sonnet
  description: Structural requirements validation
  prompt: |
    Validate the requirements at: $ARGUMENTS

    ## Process

    1. Read the requirements file
    2. Read CLAUDE.md, .claude/rules/*.md for project context
    3. Validate against criteria below

    **Threshold: Only flag issues that would block design or cause genuine confusion.**

    ### Criteria
    - **EARS Compliance**: Every acceptance criterion uses an EARS pattern (WHEN/SHALL, WHILE/SHALL, IF/THEN SHALL, WHERE/SHALL). Flag criteria that don't follow the pattern.
    - **Glossary Consistency**: Terms defined in the glossary are used consistently. Terms used in criteria are defined in the glossary.
    - **Non-Technical**: Requirements describe observable behavior, not implementation. Flag technical prescriptions (specific technologies, schemas, code patterns).
    - **Completeness**: Has introduction, glossary (3-10 terms), and 3-7 user stories. Each user story has acceptance criteria.
    - **Testability**: Each acceptance criterion is verifiable—an observer could determine pass/fail. Flag vague criteria ("system should be fast", "user-friendly").
    - **Error Coverage**: Requirements address key failure scenarios, especially at system boundaries.

    ## Output

    If no issues: `PASS`

    If issues exist, list each with category and explanation. Keep it terse.

If structural validation fails, report issues and stop.

## Phase 2: Consistency Review

Spawn a Task agent to check internal consistency:

Task tool parameters:
  subagent_type: general-purpose
  model: sonnet
  description: Requirements consistency review
  prompt: |
    Check the requirements at: $ARGUMENTS for internal consistency.

    ## Process

    1. Read the requirements file
    2. Check for:
       - Contradictions between acceptance criteria (one says X, another implies not-X)
       - Overlapping requirements that could conflict during implementation
       - Missing dependencies (requirement A assumes something that no other requirement establishes)
       - Scope gaps (scenarios a user would expect that no requirement covers)

    ## Critical Rules

    - If requirements are consistent and complete, report PASS. Finding nothing is valid.
    - Do NOT fabricate concerns. Only flag issues where you can explain what would go wrong.
    - Do NOT flag: subjective preferences, alternative phrasings, speculative future requirements.
    - Threshold: Would a designer or implementer be confused, build the wrong thing, or miss a scenario?

    ## Output

    If no issues: `PASS — requirements are internally consistent.`

    If issues exist:
    - **{issue}** — {what's inconsistent or missing} → {what could go wrong}

## Phase 3: Aggregate

Collect results from all phases. Drop PASS results.

If all phases pass: report `PASS` to the user.

If issues found:
- Deduplicate
- Group by severity
- Present each issue with: which phase found it, the gap, and the risk
- Keep the report concise
