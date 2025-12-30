#!/usr/bin/env python3
"""Hookify PreToolUse hook."""

import sys
import os
import json

# Add plugin core to path
plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, plugin_root)

from core.rules import load_rules, evaluate_rules


def main():
    try:
        input_data = json.load(sys.stdin)
        input_data['hook_event_name'] = 'PreToolUse'

        tool_name = input_data.get('tool_name', '')

        # Map tool to event type
        if tool_name == 'Bash':
            event = 'bash'
        elif tool_name in ['Edit', 'Write', 'MultiEdit']:
            event = 'file'
        else:
            event = 'all'

        rules = load_rules(event=event)
        # Also get 'all' rules
        all_rules = load_rules(event='all')
        rules.extend([r for r in all_rules if r not in rules])

        # PreToolUse only handles blocks (warnings handled by PostToolUse)
        result = evaluate_rules(rules, input_data, only_blocks=True)

        if result:
            # Block: deny operation
            print(json.dumps(result), file=sys.stderr)
            sys.exit(2)
        sys.exit(0)
    except Exception as e:
        print(f"Hookify error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
