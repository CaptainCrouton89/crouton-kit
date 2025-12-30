#!/usr/bin/env python3
"""Hookify PostToolUse hook - handles warnings (shown after tool executes)."""

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
        input_data['hook_event_name'] = 'PostToolUse'

        tool_name = input_data.get('tool_name', '')

        if tool_name == 'Bash':
            event = 'bash'
        elif tool_name in ['Edit', 'Write', 'MultiEdit']:
            event = 'file'
        else:
            event = 'all'

        rules = load_rules(event=event)
        all_rules = load_rules(event='all')
        rules.extend([r for r in all_rules if r not in rules])

        # Only process warning rules
        result = evaluate_rules(rules, input_data, only_warnings=True)

        if result and result.get('_warning'):
            # Output plain text to stderr, exit 2 (shows to Claude for PostToolUse)
            print(result['_message'], file=sys.stderr)
            sys.exit(2)

        sys.exit(0)
    except Exception as e:
        print(f"Hookify error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
