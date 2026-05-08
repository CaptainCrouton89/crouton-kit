---
name: prompting-effectively
description: Structure Claude prompts for clarity and better results using roles, explicit instructions, context, positive framing, and strategic organization. Use when crafting prompts for complex tasks, long documents, tool workflows, or code generation.
---

# Prompt Architecture

Effective prompts have structure. This skill covers the principles that make prompts clear, reliable, and maintainable — whether you're writing commands, agents, modes, skills, or API system prompts.

**MANDATORY:** Before authoring any prompt for internal Claude tools (skills, agents, modes, commands, subagent prompts), read [opus-4-7.md](opus-4-7.md) — the Opus 4.7-specific behavior reference. It covers model-specific tuning (effort, tool triggering, literal instruction following, subagent spawning, thinking, agentic patterns) that this architecture overview does not.

For detailed patterns and examples of the architecture principles below, see [reference.md](reference.md).

## The Two Zones

The most important architectural decision: what goes where.

**Behavior zone** (system prompt, agents, modes):
- Identity, personality, tone
- Constraints and hard rules
- Tool usage policies (→ [tool-design](../tool-design/SKILL.md) covers designing the tools themselves)
- Decision frameworks ("when X, do Y")
- Formatting preferences

**Task zone** (commands, skills, task prompts):
- Temporary role shifts and focus areas
- Step-by-step procedures or constraints for the task
- Context the agent needs to do this specific thing

**Knowledge zone** (skills, documents, user context, CLAUDE.md):
- Reference material and domain knowledge
- User-specific context and preferences
- Project information
- Data that changes between sessions

System prompt content gets treated as foundational identity. Task-zone content layers on top — it *redirects* the agent without replacing who it is. Knowledge gets treated as reference material. Mixing these up creates agents that treat their own rules as optional suggestions, or user-turn prompts that fight the system prompt for control of identity.

→ For the orthogonal API-level question — what goes in the `system` message vs the `user` message of a single API call — see [system-vs-user-prompt](../system-vs-user-prompt/SKILL.md).

## XML for Instruction Domains

Use XML tags to separate concern domains (identity, safety, tools, formatting). Rules:

- Section-level boundaries only — don't wrap every paragraph
- Two levels of nesting maximum for instructions (deeper is fine for examples)
- Over-tagging creates noise that dilutes the structural signal

Over-formatted system prompts bleed into over-formatted responses — use the lightest formatting that makes content clear.

## Tone Registers

The voice you use affects how the model interprets instructions — and the right voice depends on *where the prompt lives*.

**Third person → Identity (system prompts only):**
> "Claude cares about people's wellbeing."
> "The agent avoids over-formatting responses."

Establishes personality traits. The model internalizes these as "who I am." This framing belongs in system prompts, agents, and modes — not in commands or skills.

**"You are X" → Identity declaration (system prompts only):**
> "You are a senior security auditor who reviews code for vulnerabilities."

Defines the agent's core role. In a system prompt, this is foundational. In a user-turn prompt (command, skill, task), it conflicts with the identity already established — use "Act as X for this task" instead.

**"Act as X" → Temporary role (commands, skills, task prompts):**
> "Act as a security auditor for this review. Focus on auth flows and input validation."

Layers a role on top of the existing identity without overriding it. The agent applies this lens for the current task, then returns to its base behavior.

**Second person → Operations:**
> "When you encounter X, stop immediately."
> "You should use the minimum number of tools needed."

Direct instruction for procedures and workflows. Works in both zones.

**Imperative → Hard rules:**
> "NEVER reproduce song lyrics."
> "ALWAYS search before responding about current events."

Absolute rules that should not be overridden by context.

### The Escalation Ladder

1. **Suggestion**: "It's fine to..." / "Claude can..."
2. **Default**: "Claude does..." / "Claude avoids..."
3. **Instruction**: "You should..." / "Always prefer..."
4. **Hard rule**: "NEVER..." / "MUST..." / "CRITICAL:..."
5. **Repeated hard rule**: Same rule in multiple sections with different framing

Most guidance sits at levels 2–3. Reserve 4–5 for genuine non-negotiables. If everything is CRITICAL, nothing is.

## Subtract Before You Add

When the model produces bad output, scan the prompt for the instruction causing it and delete that instruction. The model has strong defaults — out-of-distribution behaviors (wrapping output in unusual tags, inventing structure, weird formatting) almost always trace back to a prompt that pushed the model there. The fix is subtraction, not addition.

**Worked example.** A tool description read:

> "Task instruction wrapped in `<fork-task>` verbatim."

The model wrapped its output in `<fork-task>` tags because the description told it to. The minimal fix is deletion:

> "The task this fork should execute."

What goes wrong if you skip the delete step:

- **Adding a prohibition while leaving the cause:** keep the "wrapped in `<fork-task>`" instruction, then bolt on *"DO NOT wrap in `<fork-task>` tags."* Now the prompt contradicts itself, and the prohibition primes attention toward the very tags you don't want.
- **Replacing with a positive description when none was needed:** "One self-contained instruction, e.g. 'Send a DM to Priya.'" Reads fine, but the field name and schema already convey this. You've spent tokens telling the model to write normally — which is what it would have done anyway.

**Order of preference:**

1. **Delete** the instruction causing the misbehavior. Often nothing needs to take its place — the field name, type, or surrounding context already conveys what's expected.
2. **Rephrase positively** when the field genuinely lacks a description. "DO NOT use ellipses" → "Use periods instead" — describe the target, not its inverse.
3. **Prohibit** only when you have observed the failure *without* any prompt pushing the model there. Rare. The bar is evidence, not preference.

**When negative framing earns its place:** the model has an observed prior toward the wrong behavior with no prompt cause. "Avoid Inter" works because Opus genuinely defaults to Inter. "Be conservative" in a code review actively suppresses findings (see opus-4-7.md). Otherwise: trust the default.

**Heuristic:** before adding *anything* in response to bad output, find the line in the prompt that caused it. If you find one, delete it and stop. Telling the model to "write normally" or "respond naturally" is a token-burning no-op — it would have done that already if you hadn't told it otherwise.

## Positive Framing

For instructions that survive the subtraction check — genuine deviations from default behavior — describe the target, not its inverse.

**Weak:** "Do not use ellipses."
**Strong:** "Use periods or commas to end clauses."

The model produces what you describe. "Don't do X" requires the model to represent X in order to avoid it, which can prime the failure mode rather than suppress it. "Do Y" steers directly. This holds across domains:

- Output style: "don't be verbose" → "keep responses to 2–3 sentences for simple questions"
- Tool use: "don't call this tool unnecessarily" → "call this tool when you see X, Y, or Z"
- Behavioral guidance: "don't be sycophantic" → "open with the answer, not a compliment"

Concrete positive instructions outperform abstract negative ones, especially in long prompts where any single rule's attention weight is diluted by surrounding context. If you find yourself writing a "don't," ask what the corresponding "do" is — that's usually the better instruction.

## Examples

**Rules:**
- Place examples adjacent to the rules they illustrate — never in a separate appendix
- Use good/bad pairs for nuanced behaviors
- Add rationale tags when the reasoning matters for generalization

```xml
<example>
  <user>What should I eat for lunch?</user>
  <good_response>A Mediterranean bowl with...</good_response>
</example>
```

```xml
<example>
  <user>Search for a recent article about fisheries.</user>
  <response>I found the article... [paraphrased summary]</response>
  <rationale>Paraphrases entirely in own words, conveying key facts
  while respecting copyright.</rationale>
</example>
```

The bad example is as important as the good one — it shows the specific failure mode you're preventing, which is often a plausible response that happens to be wrong.

## Strategic Repetition

Repetition is a deliberate design tool, not sloppiness. In long prompts, a rule stated once may get diluted by surrounding context.

**Repeat (2–3 locations, different framing):**
- Safety boundaries
- The 2–3 most important behavioral rules
- Cross-cutting constraints that apply across multiple contexts

**Don't repeat:**
- Personality traits (once is enough)
- Formatting preferences
- General tone guidance

**Heuristic:** If violating the rule would cause real harm or a terrible experience, repeat it. If it's stylistic, state it once.

→ For how repetition interacts with token budgets, placement effects, and caching in long prompts, see [context-management](../context-management/SKILL.md).

## Decision Frameworks

When the agent needs judgment calls, provide a framework — not an exhaustive rule list.

**Checklist pattern** — sequential with stop conditions:

```
## Step 0 — Does this need a visual at all?
Most requests are conversational. Check first.

## Step 1 — Is a specialized tool available?
Scan connected tools. Category match → use it. Stop.

## Step 2 — Did the person ask for a file?
"file," "download," "save" → create file. Stop.

## Step 3 — Default path
No matches → inline rendering.
```

**Trigger pattern** — concrete matching criteria:

```
**Always use this tool when you see:**
- Explicit references: "continue our conversation about..."
- Temporal references: "what did we talk about yesterday"
- Implicit signals:
  - Past tense verbs suggesting prior exchanges
  - Definite articles assuming shared knowledge
```

Both patterns beat "use the tool when appropriate" because they give the model concrete decision criteria.

## Procedures vs Constraints

Choose the right structure for the guidance you're giving. Neither is inherently better.

**Use procedures when** the order genuinely matters — steps that must happen in sequence, every time, or the outcome breaks. A deployment checklist, a multi-stage data pipeline, a protocol with dependencies between steps. If step 3 can't happen before step 2, that's a procedure.

```
1. Run the test suite
2. If tests pass, build the artifact
3. Deploy to staging
4. Run smoke tests against staging
5. If smoke tests pass, promote to production
```

This is correct as a procedure because each step depends on the previous one. Rewriting it as constraints ("ensure tests pass", "verify staging health") loses the ordering that makes it work.

**Use constraints when** the guidance is about *what matters*, not *what order to do it in*. Behavioral rules, quality standards, and goals where the agent should decide how to get there.

```
Plan before building. A missed dependency or wrong assumption
caught during planning costs nothing — caught during implementation
it means rework. Surface your plan to the user before writing code.
```

This is correct as a constraint because the agent should adapt *how* it plans to the specific task.

**The failure modes are opposite:**
- Procedures where constraints belong → brittle agents that follow the letter and miss the point
- Constraints where procedures belong → agents that skip critical steps or reorder dependencies

### When you're unsure

If it's not clear from the prompt whether something should be procedural or flexible, ask. "Should these steps happen in this exact order every time, or is the order flexible?" is a better question than guessing wrong.

### The middle ground: principles + examples

When the guidance is flexible but the application isn't obvious, state the reasoning and ground it with an example:

**Over-constrained:** "Always spawn exactly 3 explore agents before planning."
**Too vague:** "Explore proportional to codebase complexity."
**Sweet spot:** "Understand the scope of changes before committing to a plan — misunderstanding the codebase is the most expensive mistake. For example, if you're unsure how a subsystem works, spinning up 2–3 explore agents to map it out before writing a plan is usually worth the cost."

The sweet spot teaches the principle, explains why it matters, and shows what good judgment looks like — while leaving the agent free to adapt.

### Signs of wrong structure

**Procedure masquerading as constraints:**
- Steps that keep getting reordered or skipped, causing failures
- You keep adding "make sure X happened before Y" patches

**Constraints masquerading as procedure:**
- Fixed counts where the right number depends on the situation
- The prompt keeps growing as you patch failure modes with more rules
- The model follows instructions faithfully but produces worse outcomes than a looser prompt would

## Scoping & Progressive Disclosure

**Include:** Rules specific to your agent's domain, constraints on available tools, edge cases from testing, behavioral patterns users will encounter.

**Exclude:** Generic LLM knowledge, exhaustive third-party docs, frequently changing information (put in user context), rules for features the agent doesn't have.

**Progressive disclosure:** List resources with short descriptions upfront, load detail on demand:

```xml
<available_resources>
  <resource>
    <name>pdf-creation</name>
    <description>Use when creating PDF files</description>
    <location>/path/to/detailed-instructions</location>
  </resource>
</available_resources>
```

This is the pattern behind Claude Code skills — descriptions loaded upfront, full instructions loaded on demand.

## Common Mistakes

- **Over-formatting** — heavily formatted system prompts produce heavily formatted responses
- **Instruction-stuffing** — trying to anticipate every edge case with exact steps; teach principles and let the model decide how to apply them
- **Adding when you should delete** — bad output usually traces back to a prompt instruction pushing the model there. Find the cause and remove it before adding anything new. "Write normally" is not a fix; deleting the line that made it write abnormally is
- **Flat structure** — long prompts with no XML sections or headers; the model can't locate guidance
- **XML-everything** — wrapping every paragraph; structural noise dilutes the signal
- **Missing examples** — "be helpful but not too eager" means nothing without a demonstration
- **Repeating everything** — if 80% of rules are repeated, repetition stops being a signal
- **Behavioral rules in documents** — agent instructions in uploaded docs get treated as suggestions
- **Static knowledge in system prompts** — facts that change (pricing, team members) belong in retrievable documents

## Applying to Claude Code Components

| Component | Zone | Role framing | Key consideration |
|-----------|------|-------------|-------------------|
| Agents | Behavior | "You are X" — defines identity | 3rd person for traits, 2nd person for operations. |
| Modes | Behavior | "You are X" — defines identity | `append` keeps standard identity; `replace` for full custom persona. |
| Commands | Task | "Act as X" — temporary lens | Constraints or procedures depending on the task. Minimal tokens. |
| Skills | Knowledge | No role — reference material | Progressive disclosure. Overview in SKILL.md, depth in reference files. |
| CLAUDE.md | Knowledge | No role — project context | Guardrails and pointers. Constraints Claude would get wrong without. |
| Rules | Behavior | No role — constraints only | Declarative constraints scoped by file pattern. |

**Deeper guides for each component:**
- Agents → [multi-agent-orchestration](../multi-agent-orchestration/SKILL.md) for designing systems of cooperating agents
- Commands → [commands-authoring](../commands/SKILL.md)
- Skills → [skills-authoring](../skills/SKILL.md)
- CLAUDE.md → [claude-md-authoring](../claude-md/SKILL.md)
- Rules → [rules-authoring](../rules/SKILL.md)
- Hooks (lifecycle automation around prompts) → [hooks](../hooks/SKILL.md)

## Related Skills

Cross-cutting prompting topics with their own skills:

- [system-vs-user-prompt](../system-vs-user-prompt/SKILL.md) — placement of instructions in `system` vs `user` messages at the API level
- [tool-design](../tool-design/SKILL.md) — designing tool descriptions, parameter schemas, and error messages for function-calling agents
- [structured-output](../structured-output/SKILL.md) — reliable typed JSON via constrained decoding, JSON Schema, Zod, Pydantic
- [context-management](../context-management/SKILL.md) — token budgets, RAG, prompt caching, compression, multi-turn strategy
- [output-variety](../output-variety/SKILL.md) — defeating sameyness in repeated LLM calls (personality lines, names, commentary)
- [eval-and-quality-gates](../eval-and-quality-gates/SKILL.md) — measuring whether prompt changes actually help; LLM-as-judge, regression tests, guardrails
- [sounding-human](../sounding-human/SKILL.md) — removing AI-tells from generated text
