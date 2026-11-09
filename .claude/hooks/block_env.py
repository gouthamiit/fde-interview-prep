"""PreToolUse hook: stop Claude Code from reading .env files.

Claude Code pipes the tool call to this script as JSON on stdin. If the Read
targets a path containing ".env" (but not ".env.example"), we print a reason
to stderr and exit 2, which blocks the call and shows the reason to Claude.
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if ".env" in file_path and ".env.example" not in file_path:
        reason = f"Blocked: reading '{file_path}' is not allowed (it may hold secrets)."
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
