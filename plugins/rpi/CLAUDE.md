# RPI Plugin

Feature development workflow. Full pipeline: requirements, design, plan, implement, validate, test.

## Usage

**Full pipeline**: `/rpi:rpi <topic>`
**Individual phases** (standalone): `/rpi:problem`, `/rpi:requirements`, `/rpi:design`, `/rpi:plan`, `/rpi:implement`, `/rpi:validate`

The standalone commands work independently for partial workflows. `/rpi:rpi` orchestrates the full pipeline by dispatching to specialized subagents via the Task tool.

## Architecture

### Full Pipeline (`/rpi:rpi`)

```
Phase 1a: Requirements
  Main session dispatches Task tool → rpi:requirements-writer
  requirements-writer: investigate → propose → converse with user → save → validate
  Optional: fetch 3rd-party library docs, create context documents
  Output: .claude/specs/{topic}/requirements.md

Phase 1b: Design
  Main session dispatches Task tool → rpi:design-lead
  design-lead: reads requirements → investigates → proposes → converse → save → validate
  Output: .claude/specs/{topic}/design.md

Phase 2: Planning
  Main session dispatches Task tool → rpi:planning-lead
  planning-lead works autonomously with Plan subagents
  Creates implementation plan + test plan, runs advisor review
  Output: .claude/plans/{topic}.plan.md, {topic}.tests.plan.md

Phase 2.5: Validation Planning
  Main session dispatches Task tool → rpi:validation-lead
  Inventories existing infrastructure, builds reusable tools
  Writes validation plan with per-phase exit criteria
  Output: .claude/plans/{topic}.validation.plan.md, scripts/commands

Phase 3: Implementation (per phase)
  Main session partitions tasks into disjoint groups
  Dispatches parallel devcore:programmer subagents (one per group)
  Each subagent owns its files, completes its tasks, returns

  Phase Review:
    Main session dispatches parallel rpi:reviewer subagents (read-only)
    Reviewers validate findings with their own subagents and return reports
    Main session presents consolidated findings to user
    User approves fixes → main session dispatches devcore:programmer subagents to apply

  Phase Validation:
    Main session re-invokes rpi:validation-lead with "validate phase N"
    validation-lead runs proof scripts, returns pass/fail with evidence
    Failures → main session dispatches programmer subagent to fix → re-validate

Phase 4: Testing
  Main session dispatches devcore:programmer subagent to implement test plan
  Runs full test suite, fixes failures
  Re-invokes rpi:validation-lead for full cross-phase validation as final smoke test
```

### Agent Roster

All rpi agents are opus and dispatched via the Task tool. Cheaper models run as subagents within them.

| Agent | Role | Model | Edits? |
|-------|------|-------|--------|
| `rpi:requirements-writer` | Collaborative requirements definition with user | opus | Yes (requirements, context) |
| `rpi:design-lead` | Technical architecture design from requirements | opus | Yes (design, context) |
| `rpi:planning-lead` | Creates implementation + test plans | opus | Yes (plans) |
| `devcore:programmer` | Implementation | opus | Yes |
| `rpi:reviewer` | Code review + quality audit, returns fix list | opus | No (read-only) |
| `rpi:validation-lead` | Proof-of-life checks, reusable infrastructure | opus | Yes (scripts, commands, infrastructure) |

### Standalone Commands

| Command | Purpose | When to use |
|---------|---------|-------------|
| `/rpi:problem` | Explore and frame the problem space (optional) | Complex or ambiguous problem domains |
| `/rpi:requirements` | Define requirements through conversation | Need requirements without full pipeline |
| `/rpi:design` | Create technical design from requirements | Have requirements, want architecture decisions |
| `/rpi:plan` | Create implementation plan from design | Have design, want to plan without full pipeline |
| `/rpi:implement` | Execute plan with parallel subagents | Have a plan, want to implement without review/test phases |
| `/rpi:validate` | Run validation for a topic or phase | Need to verify implementation against plan |
| `/rpi:cleanup` | Clean up old spec/plan files | Housekeeping |

Standalone commands end with "clear chat and run the next command."

### Validation Skills

| Skill | Triggered by | Purpose |
|-------|-------------|---------|
| `review-requirements` | Model (after requirements edits) | Validates requirements quality and completeness |
| `review-design` | Model (after design edits) | Validates design against requirements |
| `review-plan` | Model (after plan edits) | Validates plan covers design |

The Stop hook in `hooks/` blocks session end if specs or plans were edited without running validation.

## Artifacts

```
.claude/
├── specs/{topic}/
│   ├── problem.md                           # Problem exploration (optional)
│   ├── requirements.md                       # EARS requirements
│   └── design.md                             # Technical design
├── plans/{topic}.plan.md                     # Implementation plan
├── plans/{topic}.tests.plan.md               # Test plan
├── plans/{topic}.validation.plan.md          # Validation plan
├── plans/{topic}-{phase}.plan.md             # Sub-plans (large features)
├── pipeline/{topic}.state.md                 # Decision journal
├── context/{topic}-{domain}.context.md       # Codebase context
├── context/{topic}-{library}.docs.md         # Library docs
├── scripts/                                  # Reusable validation scripts
└── validation/{topic}/                       # Topic-specific validation
```

## Key Design Decisions

- **Pipeline agents are opus, their internal subagents are sonnet/haiku.** Pipeline agents make judgment calls; subagents handle bounded, repetitive work.
- **Requirements and design are separate phases.** Requirements capture non-technical behavior (EARS format); design translates them into technical architecture. Keeping them separate prevents implementation details from contaminating behavioral intent.
- **Reviewers are read-only.** They investigate and return fix lists; the main session dispatches implementers to apply fixes.
- **Review happens per phase,** not just at the end. Catches issues before they compound in later phases.
- **Test plan is separate.** Written during planning but implemented after all code passes review. Tests reference actual implementation, not just the plan.
- **Validation creates lasting infrastructure, not throwaway scripts.** The validation-lead prioritizes reusable project tools (commands, shared scripts, debug endpoints) that future features benefit from. Topic-specific scripts supplement but don't replace shared infrastructure.
- **Design-lead fetches library docs.** If the feature uses unfamiliar third-party libraries, docs are gathered upfront and shared through the pipeline.
