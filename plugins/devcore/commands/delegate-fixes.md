---
description: Delegate fixes to agents based on complexity
argument-hint: [additional instructions]
---

Delegate fixes for issues identified in this conversation.

**First**: If no issues were identified, inform the user and stop.

## Process

### 1. Categorize by Complexity

- **Obvious**: One clear fix. Single file or mechanical change across files.
- **Likely**: Tradeoffs exist but one approach recommended. Straightforward once decided.
- **Complex**: Tradeoffs AND complicated solution. Design decisions or architectural impact.

### 2. Propose Plan

Present:
- Obvious issues → delegate immediately after approval
- Likely issues → recommend approach, note alternatives
- Complex issues → need discussion first

Wait for approval before proceeding.

### 3. Execute

After approval, use TodoWrite to track, then:

**Obvious**: Delegate to `devcore:junior-engineer` in parallel. Multiple agents for 10+ repetitive changes. Run in background.

**Likely**: Once approach confirmed, delegate to `junior-engineer` or `programmer` based on scope.

**Complex**: Discuss with user. Offer `senior-advisor` agents to analyze from different perspectives. When agreed, use Plan agent if needed, then delegate implementation.

## Guidelines

- Provide clear instructions: code snippets, pseudocode, or file references to patterns
- Prefer agent orchestration over implementing yourself (saves context)
- For <3 changes, implement directly instead
- Task not complete until every issue addressed or explicitly skipped

$ARGUMENTS
