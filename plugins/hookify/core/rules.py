#!/usr/bin/env python3
"""
Hookify rule loader and evaluator.

Loads rules from .claude/hookify.*.local.md in:
1. CWD and all parent directories (up to home)
2. ~/.claude/ (global rules)
"""

import os
import re
import glob
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


def run_command(cmd: str, timeout: int = 5) -> str:
    """Execute a shell command and return its output."""
    try:
        # Use login shell to source .zshenv/.bashrc for env vars
        result = subprocess.run(
            ['/bin/zsh', '-l', '-c', cmd],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            output = f"(error: {result.stderr.strip()})"
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timed out)"
    except Exception as e:
        return f"(error: {e})"


def interpolate_commands(message: str) -> str:
    """
    Replace !`command` patterns with command output.

    Example:
        !`linear issue list` -> (output of linear issue list)

    Skips patterns inside code blocks or when escaped.
    """
    # Skip if inside code block (``` ... ```)
    code_block_pattern = r'```[\s\S]*?```'
    code_blocks = [(m.start(), m.end()) for m in re.finditer(code_block_pattern, message)]

    # Skip inline code spans (`...`)
    inline_code_pattern = r'`[^`]+`'
    inline_codes = [(m.start(), m.end()) for m in re.finditer(inline_code_pattern, message)]

    def in_code(pos):
        for start, end in code_blocks + inline_codes:
            if start <= pos < end:
                return True
        return False

    pattern = r'!\`([^`]+)\`'

    def replacer(match):
        if in_code(match.start()):
            return match.group(0)  # Don't replace if in code block
        cmd = match.group(1)
        if cmd == 'command':  # Skip literal example placeholder
            return match.group(0)
        return run_command(cmd)

    return re.sub(pattern, replacer, message)


@dataclass
class Condition:
    """A single condition for matching."""
    field: str
    operator: str
    pattern: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        return cls(
            field=data.get('field', ''),
            operator=data.get('operator', 'regex_match'),
            pattern=data.get('pattern', '')
        )


@dataclass
class Rule:
    """A hookify rule."""
    name: str
    enabled: bool
    event: str
    pattern: Optional[str] = None
    conditions: List[Condition] = field(default_factory=list)
    action: str = "warn"
    message: str = ""

    @classmethod
    def from_dict(cls, frontmatter: Dict[str, Any], message: str) -> 'Rule':
        conditions = []

        if 'conditions' in frontmatter:
            cond_list = frontmatter['conditions']
            if isinstance(cond_list, list):
                conditions = [Condition.from_dict(c) for c in cond_list]

        simple_pattern = frontmatter.get('pattern')
        if simple_pattern and not conditions:
            event = frontmatter.get('event', 'all')
            if event == 'bash':
                cond_field = 'command'
            elif event == 'file':
                cond_field = 'new_text'
            elif event == 'prompt':
                cond_field = 'prompt'
            else:
                cond_field = 'content'

            conditions = [Condition(
                field=cond_field,
                operator='regex_match',
                pattern=simple_pattern
            )]

        return cls(
            name=frontmatter.get('name', 'unnamed'),
            enabled=frontmatter.get('enabled', True),
            event=frontmatter.get('event', 'all'),
            pattern=simple_pattern,
            conditions=conditions,
            action=frontmatter.get('action', 'warn'),
            message=message.strip()
        )


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and message body."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1]
    message = parts[2].strip()

    # Simple YAML parser
    frontmatter = {}
    lines = frontmatter_text.split('\n')

    current_key = None
    current_list = []
    current_dict = {}
    in_list = False
    in_dict_item = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())

        if indent == 0 and ':' in line and not stripped.startswith('-'):
            if in_list and current_key:
                if in_dict_item and current_dict:
                    current_list.append(current_dict)
                    current_dict = {}
                frontmatter[current_key] = current_list
                in_list = False
                in_dict_item = False
                current_list = []

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if not value:
                current_key = key
                in_list = True
                current_list = []
            else:
                value = value.strip('"').strip("'")
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                frontmatter[key] = value

        elif stripped.startswith('-') and in_list:
            if in_dict_item and current_dict:
                current_list.append(current_dict)
                current_dict = {}

            item_text = stripped[1:].strip()

            if ':' in item_text:
                in_dict_item = True
                k, v = item_text.split(':', 1)
                current_dict = {k.strip(): v.strip().strip('"').strip("'")}
            else:
                current_list.append(item_text.strip('"').strip("'"))
                in_dict_item = False

        elif indent > 2 and in_dict_item and ':' in line:
            k, v = stripped.split(':', 1)
            current_dict[k.strip()] = v.strip().strip('"').strip("'")

    if in_list and current_key:
        if in_dict_item and current_dict:
            current_list.append(current_dict)
        frontmatter[current_key] = current_list

    return frontmatter, message


def get_ancestor_dirs(start_dir: str) -> List[str]:
    """Get all ancestor directories from start_dir up to root."""
    dirs = []
    current = os.path.abspath(start_dir)
    home = os.path.expanduser('~')

    while True:
        dirs.append(current)
        parent = os.path.dirname(current)
        if parent == current:  # Reached root
            break
        # Stop at home directory (don't go above it)
        if current == home:
            break
        current = parent

    return dirs


def load_rules(event: Optional[str] = None) -> List[Rule]:
    """Load rules from .claude/ directories walking up from CWD, plus global ~/.claude/."""
    rules = []

    # Build search paths: walk up from CWD, then global
    search_paths = []

    # Add ancestor directories (CWD and parents)
    for ancestor in get_ancestor_dirs(os.getcwd()):
        search_paths.append(os.path.join(ancestor, '.claude', 'hookify.*.local.md'))

    # Add global ~/.claude/ (may already be included if we're under home)
    global_path = os.path.join(os.path.expanduser('~'), '.claude', 'hookify.*.local.md')
    if global_path not in search_paths:
        search_paths.append(global_path)

    seen_files = set()
    files = []
    for pattern in search_paths:
        for f in glob.glob(pattern):
            real_path = os.path.realpath(f)
            if real_path not in seen_files:
                seen_files.add(real_path)
                files.append(f)

    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            frontmatter, message = parse_frontmatter(content)
            if not frontmatter:
                continue

            rule = Rule.from_dict(frontmatter, message)

            if event and rule.event != 'all' and rule.event != event:
                continue

            if rule.enabled:
                rules.append(rule)
        except Exception:
            continue

    return rules


def evaluate_rules(rules: List[Rule], input_data: Dict[str, Any], only_warnings: bool = False, only_blocks: bool = False) -> Dict[str, Any]:
    """Evaluate rules against input data."""
    hook_event = input_data.get('hook_event_name', '')
    blocking_rules = []
    warning_rules = []

    for rule in rules:
        if rule_matches(rule, input_data):
            if rule.action == 'block':
                if not only_warnings:
                    blocking_rules.append(rule)
            else:
                if not only_blocks:
                    warning_rules.append(rule)

    if blocking_rules:
        messages = [f"**[{r.name}]**\n{interpolate_commands(r.message)}" for r in blocking_rules]
        combined = "\n\n".join(messages)

        if hook_event == 'Stop':
            return {"decision": "block", "reason": combined}
        elif hook_event in ['PreToolUse', 'PostToolUse']:
            return {
                "hookSpecificOutput": {
                    "hookEventName": hook_event,
                    "permissionDecision": "deny"
                },
                "systemMessage": combined
            }
        elif hook_event == 'UserPromptSubmit':
            return {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": combined
                }
            }
        else:
            return {"systemMessage": combined}

    if warning_rules:
        messages = [f"**[{r.name}]**\n{interpolate_commands(r.message)}" for r in warning_rules]
        combined = "\n\n".join(messages)

        if hook_event == 'UserPromptSubmit':
            return {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": combined
                }
            }
        # For warnings, return plain text (hook script will handle output)
        return {"_warning": True, "_message": combined}

    return {}


def rule_matches(rule: Rule, input_data: Dict[str, Any]) -> bool:
    """Check if rule matches input data."""
    if not rule.conditions:
        return False

    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    for condition in rule.conditions:
        value = extract_field(condition.field, tool_name, tool_input, input_data)
        if value is None:
            return False

        if not check_condition(condition, value):
            return False

    return True


def extract_field(field: str, tool_name: str, tool_input: Dict, input_data: Dict) -> Optional[str]:
    """Extract field value from input."""
    if field in tool_input:
        return str(tool_input[field])

    if field == 'prompt':
        return input_data.get('prompt', '')
    if field == 'reason':
        return input_data.get('reason', '')
    if field == 'command':
        return tool_input.get('command', '')
    if field == 'file_path':
        return tool_input.get('file_path', '')
    if field in ['new_text', 'new_string']:
        return tool_input.get('new_string', '') or tool_input.get('content', '')
    if field in ['old_text', 'old_string']:
        return tool_input.get('old_string', '')
    if field == 'content':
        return tool_input.get('content', '') or tool_input.get('new_string', '')

    return None


def check_condition(condition: Condition, value: str) -> bool:
    """Check if condition matches value."""
    pattern = condition.pattern
    op = condition.operator

    if op == 'regex_match':
        try:
            return bool(re.search(pattern, value, re.IGNORECASE))
        except re.error:
            return False
    elif op == 'contains':
        return pattern in value
    elif op == 'equals':
        return pattern == value
    elif op == 'not_contains':
        return pattern not in value
    elif op == 'starts_with':
        return value.startswith(pattern)
    elif op == 'ends_with':
        return value.endswith(pattern)

    return False
