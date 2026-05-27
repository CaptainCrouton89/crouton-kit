#!/usr/bin/env python3
import json
import os
import re
import sys


def check_openai_models(content: str) -> list[str]:
    """Check for outdated OpenAI model usage."""
    issues = []

    # Latest models (Feb 2026): gpt-5.2, gpt-5.2-pro, gpt-5.2-codex
    # Still supported: gpt-5.1, gpt-5
    # Retiring Feb 13 2026: gpt-4o, gpt-4.1, gpt-4.1-mini, o4-mini
    openai_patterns = [
        (r'gpt-3\.5', 'Use gpt-5.2 or gpt-5.2-codex instead of GPT-3.5'),
        (r'gpt-4(?![.o\d])', 'Use gpt-5.2 instead of GPT-4 base'),
        (r'gpt-4-turbo', 'Use gpt-5.2 instead of GPT-4 Turbo'),
        (r'gpt-4o', 'Use gpt-5.2 instead of GPT-4o (retiring Feb 2026)'),
        (r'gpt-4\.[01]', 'Use gpt-5.2 instead of GPT-4.x variants (retiring Feb 2026)'),
        (r'gpt-4\.5-preview', 'Use gpt-5.2 instead of GPT-4.5 preview (deprecated)'),
        (r'o4-mini', 'Use gpt-5.2 instead of o4-mini (retiring Feb 2026)'),
    ]

    for pattern, message in openai_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(message)

    return issues

def check_anthropic_models(content: str) -> list[str]:
    """Check for outdated Anthropic model usage."""
    issues = []

    # Latest models (Feb 2026): claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5
    # Claude 4.0 and earlier are deprecated
    anthropic_patterns = [
        (r'claude-3-5-sonnet|claude-3\.5-sonnet', 'Use claude-sonnet-4-5 instead of Claude 3.5 Sonnet'),
        (r'claude-3-7-sonnet|claude-3\.7-sonnet', 'Use claude-sonnet-4-5 instead of Claude 3.7 Sonnet'),
        (r'claude-3-opus', 'Use claude-opus-4-5 instead of Claude 3 Opus'),
        (r'claude-3-haiku', 'Use claude-haiku-4-5 instead of Claude 3 Haiku'),
        (r'claude-4-sonnet(?!-4-5)', 'Use claude-sonnet-4-5 instead of Claude 4.0 Sonnet'),
        (r'claude-4-opus(?!-4-5)', 'Use claude-opus-4-5 instead of Claude 4.0 Opus'),
        (r'claude-4-haiku(?!-4-5)', 'Use claude-haiku-4-5 instead of Claude 4.0 Haiku'),
    ]

    for pattern, message in anthropic_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(message)

    return issues

def check_backwards_compat_patterns(content: str, file_path: str) -> list[str]:
    """Check for backwards compatibility and legacy patterns - warnings."""
    issues = []

    warning_patterns = [
        (r'\blegacy\b', "WARNING: Legacy code pattern detected. Backwards compatibility shouldn't be added unless the user explicitly asked for it."),
        (r'backward[s]?\s+compatib', "WARNING: Backwards compatibility pattern detected. Don't preserve old behavior unless the user explicitly asked for it."),
        (r'\bdeprecated\b', "WARNING: Deprecated pattern detected. Prefer deleting deprecated code over keeping it around."),
        (r'\bcompat(?:ibility)?\s*(?:mode|layer|shim)\b', "WARNING: Compatibility layer detected. Avoid shims unless the user explicitly asked for one."),
    ]

    for pattern, message in warning_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(message)

    return issues


def check_fallback_patterns(content: str, file_path: str) -> list[str]:
    """Check for fallback patterns in code files only - these are warnings."""
    issues = []

    # Only check code files (not markdown, yaml, json, etc.)
    code_extensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.hpp']
    if not any(file_path.endswith(ext) for ext in code_extensions):
        return issues

    warning_patterns = [
        (r'\|\|\s*[\'"][^\'"]*[\'"]', 'WARNING: Default value fallbacks (|| "default") detected. Consider using explicit error handling instead.'),
        (r'\?\?\s*[\'"][^\'"]*[\'"]', 'WARNING: Nullish coalescing with defaults (?? "default") detected. Consider replacing with explicit validation.'),
        (r'try\s*\{[^}]*\}\s*catch\s*\([^)]*\)\s*\{[^}]*\}', 'WARNING: Empty or generic catch blocks may hide errors. Ensure proper error handling and re-throwing.'),
    ]

    for pattern, message in warning_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(message)

    return issues

def strip_strings_and_comments(content: str) -> str:
    """Blank out string literals and comments so type checks don't false-positive
    on 'any' appearing inside them.

    Replaces string/comment characters with spaces while preserving newlines and
    overall length, so reported line numbers stay accurate. Handles single/double
    quoted strings (with escapes), template literals (keeping ${...} interpolations
    as live code so 'as any' inside them is still caught), line comments, and block
    comments. This is a lexer-style pass rather than a full AST parse because the
    hook only sees edit fragments, which often won't parse as complete source.
    """
    result = list(content)
    n = len(content)
    i = 0
    # Context stack. While inside a "${...}" interpolation we push "interp" for the
    # opening brace and for every nested "{", popping on each "}", so the matching
    # close returns us to the template.
    stack: list[str] = []

    def top() -> str | None:
        return stack[-1] if stack else None

    def blank(idx: int) -> None:
        if content[idx] != "\n":
            result[idx] = " "

    while i < n:
        c = content[i]
        nxt = content[i + 1] if i + 1 < n else ""
        ctx = top()

        if ctx in ("single", "double"):
            if c == "\\":
                blank(i)
                if i + 1 < n:
                    blank(i + 1)
                i += 2
                continue
            if (ctx == "single" and c == "'") or (ctx == "double" and c == '"'):
                stack.pop()
            blank(i)
            i += 1
            continue

        if ctx == "template":
            if c == "\\":
                blank(i)
                if i + 1 < n:
                    blank(i + 1)
                i += 2
                continue
            if c == "`":
                stack.pop()
                blank(i)
                i += 1
                continue
            if c == "$" and nxt == "{":
                stack.append("interp")
                blank(i)
                blank(i + 1)
                i += 2
                continue
            blank(i)
            i += 1
            continue

        if ctx == "line_comment":
            if c == "\n":
                stack.pop()
            else:
                blank(i)
            i += 1
            continue

        if ctx == "block_comment":
            if c == "*" and nxt == "/":
                stack.pop()
                blank(i)
                blank(i + 1)
                i += 2
                continue
            blank(i)
            i += 1
            continue

        # NORMAL code, or inside a "${...}" interpolation (also live code).
        if c == "/" and nxt == "/":
            stack.append("line_comment")
            blank(i)
            blank(i + 1)
            i += 2
            continue
        if c == "/" and nxt == "*":
            stack.append("block_comment")
            blank(i)
            blank(i + 1)
            i += 2
            continue
        if c == "'":
            stack.append("single")
            blank(i)
            i += 1
            continue
        if c == '"':
            stack.append("double")
            blank(i)
            i += 1
            continue
        if c == "`":
            stack.append("template")
            blank(i)
            i += 1
            continue
        if ctx == "interp" and c == "{":
            stack.append("interp")
            i += 1
            continue
        if ctx == "interp" and c == "}":
            stack.pop()
            i += 1
            continue
        i += 1

    return "".join(result)

def check_any_type_usage(content: str, file_path: str) -> list[str]:
    """Check for 'any' type usage in TypeScript/JavaScript."""
    if not file_path.endswith(('.ts', '.tsx')):
        return []
    issues = []

    # More sophisticated pattern to catch 'any' as a type
    any_type_patterns = [
        (r':\s*any\b', "WARNING: 'any' type detected. Consider defining proper types instead. Look up existing type definitions or create new ones in appropriate locations."),
        (r'<any>', "WARNING: 'any' generic type detected. Consider using specific types instead."),
        (r'Array<any>', "WARNING: 'Array<any>' detected. Consider using 'Array<SpecificType>' instead."),
        (r'Promise<any>', "WARNING: 'Promise<any>' detected. Consider using 'Promise<SpecificType>' instead."),
        (r'\bas\s+any\b', "WARNING: Type assertion 'as any' detected. Consider using proper type assertions or fix the underlying type issue."),
        (r'Record<[^,>]+,\s*any>', "WARNING: 'Record<string, any>' pattern detected. Consider defining proper value types if possible."),
    ]

    # Blank out strings and comments so 'any' inside them isn't flagged, while
    # keeping line numbers intact for reporting.
    cleaned = strip_strings_and_comments(content)
    lines = cleaned.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern, message in any_type_patterns:
            if re.search(pattern, line):
                issues.append(f"{message} (Line {line_num})")
                break  # Only report one issue per line

    return issues

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    hook_event = input_data.get("hook_event_name", "PreToolUse")

    # Only check Write and Edit operations
    if tool_name not in ["Write", "Edit", "MultiEdit"]:
        sys.exit(0)

    # Get file path early for exclusion checks
    file_path = tool_input.get("file_path", "")

    # Skip temp directories
    if any(d in file_path for d in ['/tmp/', '/private/tmp/', '/var/tmp/', '/temp/', '.tmp/']):
        sys.exit(0)

    # Don't check the hook file itself (contains model name patterns as strings)
    if "code-quality-checker.py" in file_path:
        sys.exit(0)

    # Get file content
    content = ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        # Check all edits
        edits = tool_input.get("edits", [])
        content = "\n".join([edit.get("new_string", "") for edit in edits])

    if not content:
        sys.exit(0)

    # Collect blocking issues (model-related)
    blocking_issues = []
    blocking_issues.extend(check_openai_models(content))
    blocking_issues.extend(check_anthropic_models(content))

    # Collect warning issues
    warning_issues = []
    warning_issues.extend(check_backwards_compat_patterns(content, file_path))
    warning_issues.extend(check_fallback_patterns(content, file_path))
    warning_issues.extend(check_any_type_usage(content, file_path))

    # Handle blocking issues (models)
    if blocking_issues:
        error_message = f"Code quality issues detected in {file_path}:\n\n"
        for i, issue in enumerate(blocking_issues, 1):
            error_message += f"{i}. {issue}\n"

        error_message += "\nPlease address these issues and try again."

        # Use JSON output to provide structured feedback
        output = {
            "decision": "block",
            "reason": error_message
        }
        print(json.dumps(output))
        sys.exit(0)

    # Handle warnings (show but don't block)
    if warning_issues:
        warning_message = f"Code quality issues detected in {file_path}:\n\n"
        for i, issue in enumerate(warning_issues, 1):
            warning_message += f"{i}. {issue}\n"

        warning_message = f"""<system-reminder>

{warning_message}

It is strongly advised to address these issues and try again.
</system-reminder>"""

        # Use JSON output to show warnings without blocking
        output = {
            "hookSpecificOutput": {
                "hookEventName": hook_event,
                "additionalContext": warning_message
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # If no issues, allow the operation to proceed
    sys.exit(0)

if __name__ == "__main__":
    main()
