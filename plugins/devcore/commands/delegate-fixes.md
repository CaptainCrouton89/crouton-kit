---
description: Delegate fixes to lots of agents
argument-hint: <additional instructions>
---

We've identified issues—let's fix them.

**First, check if there are any issues to fix.** If no issues were identified in the prior conversation or input, inform the user and stop.

Follow these steps precisely.

1. **Categorize each issue** by complexity:

   - **Obvious**: There is one clear best way to fix it. Affects a single file, or the same mechanical change across multiple files. Can be multi-line.
   - **Likely**: There are tradeoffs, but one approach is recommended. The solution itself is straightforward once the approach is chosen.
   - **Complex**: There are tradeoffs AND the solution is complicated. Requires design decisions or affects architecture.

2. **Propose your plan.** Briefly explain:
   - Which issues are obvious (will delegate immediately after approval)
   - Which issues are likely (propose the recommended approach and alternatives)
   - Which issues are complex (need discussion before proceeding)

3. **After the plan is approved**, use TodoWrite to track progress, then proceed:

   - **Obvious issues**: Delegate to haiku agents in parallel. Use as many as needed—including multiple agents for the same task if it involves 10+ well-defined, repetitive changes. Run these in the background and don't check in on them until ALL other tasks are done, or requested.

   - **Likely issues**: Once the approach is confirmed, delegate to haiku or sonnet agents depending on implementation complexity.

   - **Complex issues**: Cooperate with the user to arrive at a solution. Offer to have opus agents weigh in by analyzing from different perspectives (potentially one opus agent per perspective, for particularly complex problems). When agreed upon, offer to use a plan agent to make a plan (for complex fixes), and then delegate to haiku or sonnet agents to implement.

**Further clarification from user**:
$ARGUMENTS

**Reminders**:
- Give clear instructions to delegated agents, providing either code snippets or pseudocode, or file references to existing patterns; unclear instructions result in more harm than good.
- Orchestration of agents is generally preferable to implementing things yourself since it saves context. However, if there are only a few changes, you may make these changes yourself instead.
- This task is not finished until every issue has either been addressed or explicitly noted to be ignored. Prefer sending agents to the background and ignoring them so you can move on to the next issues.
