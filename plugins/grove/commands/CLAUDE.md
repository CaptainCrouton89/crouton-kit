# CLAUDE.md

## Command roles

`/plant` and `/seed` are the composite commands — they orchestrate discovery, registration, and planting. The other commands (`/adopt`, `/register`, `/list`, `/doctor`, `/uproot`) are thin passthroughs to the `grove` CLI. Don't add synthesis logic to the thin ones.

`/list` and `/doctor` use `disable-model-invocation: true` — they produce no model output, just raw CLI output piped to the user.

## `/seed` flow

`/seed` runs **three parallel discovery agents** on a source project and outputs two files into `.claude/grove/`:

- `config.json` — port definitions, repo specs, copy/patch/install declarations. The CLI processes these declaratively during `grove plant`.
- `setup.sh` — optional script for custom logic that config can't express (DB creation, binary patching, etc.). Most projects don't need one.

After seeding, the user commits `.claude/grove/` and teammates run `/grove:plant` with no discovery step.

If `.claude/grove/config.json` already exists, `/seed` asks before overwriting.

## `/plant` flow — two paths

`/plant` checks for `.claude/grove/config.json` immediately after parsing arguments:

**Seeded path (config exists):**
1. Register via `grove register <source> --from-config` if not already registered
2. Run `grove plant` — the CLI handles everything declaratively:
   - Clones repos (if `repos` defined) or rsync copies
   - Copies files from source (`copyFromSource`)
   - Patches port references (`patchPortsIn`) — auto-derives replacements from port definitions
   - Installs dependencies (`install`)
   - Runs `setup.sh` last (if present) for custom logic
3. Lightweight verification and report

**Discovery path (no config):**
1. Run **three parallel discovery agents** (same agents as `/seed` Step 3)
2. `grove register` with explicit `--port` flags
3. `grove plant`
4. Manual post-plant patching: .env files, .claude/ directory, config files, dependency install, codegen
5. Full verification

The registration check (`grove list`) gates both paths — if already registered, skip to plant.

## `.claude/grove/` contract

Projects that have been seeded contain:

```
.claude/grove/
  config.json   — port definitions, repo specs, copy/patch/install declarations
  setup.sh      — optional script for custom logic (env-var driven, no args)
```

`config.json` schema:
```json
{
  "version": 1,
  "name": "<project-name>",
  "ports": {
    "<service>": { "base": <N>, "offset": <N> }
  },
  "excludes": ["node_modules", ".next", "dist", ...],
  "repos": {
    "<repo-dir>": { "branch": "main", "recurseSubmodules": false }
  },
  "copyFromSource": [
    { "from": "<path>", "to": "<path>", "patchPorts": false }
  ],
  "patchPortsIn": [".claude/**/*.md", "**/.env", "**/.env.*"],
  "install": [
    { "dir": "<subdir>", "cmds": ["pnpm install --frozen-lockfile"] }
  ]
}
```

Config-driven setup fields (all optional, processed in order by `grove plant`):
- `repos` — multi-repo clone definitions. Replaces rsync for projects with multiple git repos.
- `copyFromSource` — files/dirs to copy from source (untracked files like `.env`, `.yalc`, `dist/`). `patchPorts: true` applies port substitution after copy.
- `patchPortsIn` — glob patterns for automatic port substitution. Uses `(?<!\d)BASE(?!\d)` regex to replace base port numbers with computed ports. Skips `grove/config.json`.
- `install` — per-directory install commands.

`setup.sh` runs last. All context is passed via env vars: `GROVE_SLOT`, `GROVE_SOURCE`, `GROVE_TARGET`, `GROVE_INSTANCE_NAME`, `GROVE_PORT_<SERVICE>`, `GROVE_PORTS_JSON`.

## `grove register` flags

`--from-config` — reads port definitions, name, excludes, and setup script path from `.claude/grove/config.json`. Explicit CLI flags override config values.

`--update` — updates an existing registration rather than erroring. Used when re-seeding a project that was already registered.

## Port formula

```
actual_port = base + (slot × offset)
```

Use `offset: 1` for debug/CDP ports (9222, 9229) so slot 2 → 9223, slot 3 → 9224. Use `offset: 100` for everything else. Mixing offsets in a single project is intentional — don't normalize them.

## Most-missed post-plant step (discovery path only)

Step 10b (`.claude/` directory patching) is explicitly the most commonly missed in the discovery path. After planting, find-replace base port numbers across `.md`, `.sh`, `.json`, `.yaml` files in the target's `.claude/` directory. Stale ports here cause Claude sessions in the new instance to silently operate on the original instance's services. Seeded projects handle this via the `patchPortsIn` config field.

## `/adopt` slot detection

`/adopt` auto-detects the slot number from `PORT=` values in `.env` files in the target directory. Pass `--slot N` explicitly only when the .env file is absent or has a non-standard port variable name.

## Init script contract (discovery path)

Grove calls the init script as:
```
<script> <source> <target> <slot> <name>
```
If a project has `.claude/scripts/create-*-env.sh`, `/plant` passes it via `--init`. If the init script ran successfully, Step 10 (post-plant setup) skips steps the script already handled — check init output before patching .env files manually.

Seeded projects use `setup.sh` instead of the init script pattern.

## `/uproot` does not auto-clean

`grove uproot` removes the directory and registry entry but does **not** kill running processes or drop databases. After uprooting, read the cleanup hints in the command output and run them manually (kill by port, `psql` to drop slot DB).

## Keeping grove current

grove reports when it's behind: running any `grove` command may print a notice to **stderr** like `[grove] update available: X → Y` (throttled, so not on every run). When you see it, update grove before continuing — and use the package manager that installed it, **never a hardcoded `npm i -g`** (a wrong guess drops a conflicting parallel global install):

1. Inspect the install path: `readlink -f "$(command -v grove)"`.
2. Path contains `/pnpm/` → `pnpm add -g @crouton-kit/grove@latest`; `/.bun/` → `bun add -g @crouton-kit/grove@latest`; `.yarn`/`yarn/global` → `yarn global add @crouton-kit/grove@latest`; otherwise → `npm i -g @crouton-kit/grove@latest`.

The SessionStart hook only checks that grove exists — it deliberately does not update it, for the same reason (no assuming a package manager).
