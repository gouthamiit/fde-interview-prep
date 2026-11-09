"""PostToolUse hook: lint and type-check after every file edit.

Runs `ruff check app tests` and `mypy app` from the project root. If either
fails, its output goes to stderr and we exit 2, so Claude Code feeds the
errors straight back to the agent to fix.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
CHECKS = [
    ["ruff", "check", "app", "tests"],
    ["mypy", "app"],
]


def python_executable() -> str:
    """Prefer the project's venv, where ruff and mypy are installed."""
    venv_python = PROJECT_DIR / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.exists() else sys.executable


def main() -> int:
    sys.stdin.read()  # the tool-call JSON; not needed, every edit triggers the same checks
    failures = []
    for check in CHECKS:
        result = subprocess.run(
            [python_executable(), "-m", *check],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append(f"$ {' '.join(check)}\n{result.stdout}{result.stderr}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
