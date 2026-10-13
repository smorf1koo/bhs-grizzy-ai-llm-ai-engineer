"""Edit format returned by the model and its application to a project copy.

Provided ready-made: search/replace blocks plus whole new files. Put EDIT_FORMAT into the system
prompt. You may switch to another format (full files, unified diff) if you explain why in README.
"""
from __future__ import annotations

import re
from pathlib import Path

EDIT_FORMAT = """Answer ONLY with edit blocks, no explanations outside them.
To change an existing file:
FILE: scripts/player.gd
<<<<<<< SEARCH
exact lines copied from the current file
=======
new lines
>>>>>>> REPLACE
To create a new file:
FILE: scripts/new_file.gd
<<<<<<< NEW
full file content
>>>>>>> NEW
Paths are relative to the project root. SEARCH text must match the file exactly once.
GDScript uses tabs for indentation."""

BLOCK = re.compile(
    r"^FILE:\s*(?P<path>\S+)\s*\n"
    r"(?:<<<<<<< SEARCH\n(?P<search>.*?)\n?=======\n(?P<replace>.*?)\n?>>>>>>> REPLACE"
    r"|<<<<<<< NEW\n(?P<new>.*?)\n?>>>>>>> NEW)",
    re.S | re.M,
)


class EditError(Exception):
    """The model answer cannot be parsed or applied. Treat it like a validation error (retry)."""


def parse_edits(answer: str) -> list[dict]:
    """Extract edits: {"path", "search", "replace"} or {"path", "content"} for new files."""
    edits: list[dict] = []
    for m in BLOCK.finditer(answer):
        path = m.group("path").removeprefix("res://")
        if m.group("new") is not None:
            edits.append({"path": path, "content": m.group("new") + "\n"})
        else:
            edits.append({"path": path, "search": m.group("search"), "replace": m.group("replace")})
    if not edits:
        raise EditError("No edit blocks found. Use the FILE / SEARCH / REPLACE format exactly.")
    return edits


def _safe_path(root: Path, rel: str) -> Path:
    if rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel) or ".." in Path(rel).parts:
        raise EditError(f"{rel}: path outside the project is not allowed")
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()):
        raise EditError(f"{rel}: path outside the project is not allowed")
    return path


def apply_edits(project_copy: Path, edits: list[dict]) -> list[str]:
    """Apply edits inside project_copy, return changed res:// paths.

    Nothing from the answer is executed. Raises EditError with a message that can be sent back
    to the model (file name and the SEARCH text that did not match).
    """
    changed: list[str] = []
    for edit in edits:
        path = _safe_path(project_copy, edit["path"])
        if "content" in edit:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(edit["content"], encoding="utf-8")
        else:
            if not path.is_file():
                raise EditError(f"{edit['path']}: file does not exist (use a NEW block to create it)")
            text = path.read_text(encoding="utf-8")
            count = text.count(edit["search"])
            if count != 1:
                raise EditError(f"{edit['path']}: SEARCH text found {count} times, "
                                f"must be exactly once:\n{edit['search']}")
            path.write_text(text.replace(edit["search"], edit["replace"]), encoding="utf-8")
        res = "res://" + edit["path"]
        if res not in changed:
            changed.append(res)
    return changed
