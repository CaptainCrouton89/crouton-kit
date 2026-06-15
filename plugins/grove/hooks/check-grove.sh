#!/usr/bin/env bash
# SessionStart hook: make sure the grove CLI is available.
#
# This does NOT update grove. grove keeps itself current on its own: it prints a
# notice to stderr when a newer version has been published, and whoever updates
# uses the package manager that installed it. The hook must never assume npm —
# grove may have been installed with pnpm, yarn, or bun, and `npm i -g` would
# drop a conflicting parallel global install.
if ! command -v grove &>/dev/null; then
  echo "grove CLI not found. Install @crouton-kit/grove globally with this machine's package manager — e.g. 'npm i -g', 'pnpm add -g', 'bun add -g', or 'yarn global add' @crouton-kit/grove — then re-run." >&2
fi
exit 0
