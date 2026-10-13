"""Validation with the Godot binary."""
from __future__ import annotations

import subprocess
from pathlib import Path


def run_godot(godot_bin: str, args: list[str], timeout: float = 120.0) -> tuple[int, str]:
    """Run Godot, return (exit code, stdout+stderr). Provided ready-made."""
    proc = subprocess.run([godot_bin, *args], capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout + proc.stderr


def check_scripts(godot_bin: str, project_copy: Path, changed: list[str]) -> list[str]:
    """Return a list of human-readable errors (empty list = OK).

    TODO(candidate):
      - import the project once so class_name and autoloads resolve:
            run_godot(godot_bin, ["--headless", "--path", str(project_copy), "--import"])
      - for every changed .gd:
            run_godot(godot_bin, ["--headless", "--path", str(project_copy), "--check-only", "--script", "res://..."])
      - look at the output too, not only at the exit code (search for "SCRIPT ERROR", "Parse Error", "ERROR:").
    Changed .tscn files are not covered by --check-only; loading them headless is optional.
    """
    raise NotImplementedError("check_scripts")
