"""MCP server "interview-guides": serves the study guides in resources/.

Run it (stdio transport, which is what Claude Code expects):
    python mcp/server.py

Note: this folder deliberately has no __init__.py. With one, it would shadow
the installed `mcp` package that FastMCP itself imports.
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"

mcp = FastMCP("interview-guides")


def guide_names() -> list[str]:
    """Names of every guide: the .md files in resources/, without the extension."""
    return sorted(path.stem for path in RESOURCES_DIR.glob("*.md"))


@mcp.tool
def list_guides() -> list[str]:
    """List the available interview guides, e.g. 'decomposition-guide'."""
    return guide_names()


@mcp.tool
def get_guide(name: str) -> str:
    """Return the full markdown of one guide. Use a name from list_guides()."""
    name = name.removesuffix(".md")
    # Only accept known names, so a caller can't read files outside resources/.
    if name not in guide_names():
        available = ", ".join(guide_names())
        raise ToolError(f"No guide named '{name}'. Available guides: {available}")
    return (RESOURCES_DIR / f"{name}.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
