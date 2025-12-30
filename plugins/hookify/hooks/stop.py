#!/usr/bin/env python3
"""Hookify Stop hook."""

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
        input_data['hook_event_name'] = 'Stop'

        rules = load_rules(event='stop')
        all_rules = load_rules(event='all')
        rules.extend([r for r in all_rules if r not in rules])

        result = evaluate_rules(rules, input_data)

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"systemMessage": f"Hookify error: {e}"}))

    sys.exit(0)


if __name__ == '__main__':
    main()
