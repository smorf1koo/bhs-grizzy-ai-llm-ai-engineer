"""Helpers for isolated runs: clean copy of the project and unified diff. Provided ready-made."""
from __future__ import annotations

import difflib
import shutil
from pathlib import Path

TEXT_SUFFIXES = {".gd", ".tscn", ".tres", ".godot", ".cfg"}


def make_clean_copy(project: Path, dest: Path) -> Path:
    """Copy the project to dest (removing dest first). The original is never modified."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(project, dest, ignore=shutil.ignore_patterns(".godot"))
    return dest


def unified_diff(original: Path, modified: Path) -> str:
    """Unified diff of all text files between two project trees (added/removed files included)."""
    def files(root: Path) -> set[str]:
        return {p.relative_to(root).as_posix() for p in root.rglob("*")
                if p.is_file() and p.suffix in TEXT_SUFFIXES and ".godot" not in p.parts}

    chunks: list[str] = []
    for rel in sorted(files(original) | files(modified)):
        a, b = original / rel, modified / rel
        a_lines = a.read_text(encoding="utf-8").splitlines(keepends=True) if a.exists() else []
        b_lines = b.read_text(encoding="utf-8").splitlines(keepends=True) if b.exists() else []
        if a_lines != b_lines:
            chunks.extend(difflib.unified_diff(a_lines, b_lines, f"a/{rel}", f"b/{rel}"))
    return "".join(chunks)
