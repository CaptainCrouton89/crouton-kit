---
paths:
  - ".claude/rules/**/*.md"
---

# Writing Rules

Rules are constraints Claude follows automatically when working with matching files.

## Structure

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "**/*.test.ts"
---

# Topic Name

Declarative constraints here.
```

## Path Patterns

- `**/*.ts` - all TypeScript files
- `src/**/*` - everything under src/
- `{src,lib}/**/*.ts` - multiple directories
- Omit `paths` for rules that apply everywhere

## Rules

1. **One topic per file** - testing.md, security.md, not everything.md
2. **Declarative** - state what should/shouldn't be done
3. **Specific** - "use 2-space indent" not "format properly"
4. **Use paths sparingly** - only when rules truly are file-specific
5. **Organize with subdirectories** - group related rules
6. **Skip the obvious** - don't restate best practices Claude already knows (security basics, error handling, testing patterns). Only specify what's unique to your project.
