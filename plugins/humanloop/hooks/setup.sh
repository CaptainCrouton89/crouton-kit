#!/usr/bin/env bash
#
# SessionStart hook: installs `hl` (npm — @crouton-kit/humanloop) if missing.
# Always exits 0.
#

set -euo pipefail

messages=()

install_hl() {
    if command -v hl &>/dev/null; then
        return 0
    fi

    if command -v npm &>/dev/null; then
        npm install -g @crouton-kit/humanloop --silent 2>/dev/null && return 0
    fi
    if command -v pnpm &>/dev/null; then
        pnpm add -g @crouton-kit/humanloop --silent 2>/dev/null && return 0
    fi
    if command -v yarn &>/dev/null; then
        yarn global add @crouton-kit/humanloop --silent 2>/dev/null && return 0
    fi

    messages+=("hl not installed: no npm/pnpm/yarn found. Install manually: npm install -g @crouton-kit/humanloop")
    return 1
}

install_hl || true

if [[ ${#messages[@]} -gt 0 ]]; then
    joined=$(printf '%s. ' "${messages[@]}")
    printf '{"systemMessage": %s}\n' "$(printf '%s' "$joined" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')"
fi

exit 0
