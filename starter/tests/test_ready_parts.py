"""Tests for the ready-made parts: index, edit format, replay provider."""
from dataclasses import replace
from pathlib import Path

import pytest

from grizzy.config import Config
from grizzy.edits import EditError, apply_edits, parse_edits
from grizzy.index import build_index
from grizzy.llm import LLMError, chat

ROOT = Path(__file__).resolve().parents[1]
PROJECT = next(p for p in (ROOT / "project", ROOT.parent / "project") if p.is_dir())


def test_index_links() -> None:
    index = build_index(PROJECT)
    assert index["autoloads"] == {"GameState": "res://scripts/game_state.gd"}
    assert index["scripts"]["res://scripts/enemy.gd"]["class_name"] == "Enemy"
    level_2 = index["scenes"]["res://scenes/levels/level_2.tscn"]
    speeds = [n["props"]["speed"] for n in level_2["nodes"] if n["path"].startswith("Enemies/")]
    assert speeds == ["80.0", "90.0", "100.0", "80.0"]
    edges = {(a, kind, b) for a, kind, b, _ in index["edges"]}
    assert ("res://scenes/levels/level_2.tscn", "overrides", "res://scenes/enemy.tscn") in edges
    assert ("res://scenes/levels/level_1.tscn", "signal_handler", "res://scripts/level.gd") in edges
    assert ("res://scripts/enemy.gd", "uses_autoload", "res://scripts/game_state.gd") in edges


ANSWER = """Some text before.
FILE: scripts/a.gd
<<<<<<< SEARCH
var speed = 1
=======
var speed = 2
>>>>>>> REPLACE
FILE: scripts/b.gd
<<<<<<< NEW
extends Node
>>>>>>> NEW
"""


def test_parse_and_apply(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "a.gd").write_text("extends Node\nvar speed = 1\n", encoding="utf-8")
    changed = apply_edits(tmp_path, parse_edits(ANSWER))
    assert changed == ["res://scripts/a.gd", "res://scripts/b.gd"]
    assert (tmp_path / "scripts" / "a.gd").read_text(encoding="utf-8") == "extends Node\nvar speed = 2\n"
    assert (tmp_path / "scripts" / "b.gd").read_text(encoding="utf-8") == "extends Node\n"


def test_edit_errors(tmp_path: Path) -> None:
    with pytest.raises(EditError):
        parse_edits("no blocks here")
    with pytest.raises(EditError):
        apply_edits(tmp_path, [{"path": "../evil.gd", "content": "x"}])
    (tmp_path / "a.gd").write_text("x\n", encoding="utf-8")
    with pytest.raises(EditError):
        apply_edits(tmp_path, [{"path": "a.gd", "search": "y", "replace": "z"}])


def test_replay(tmp_path: Path) -> None:
    (tmp_path / "R03").mkdir()
    (tmp_path / "R03" / "attempt_1.txt").write_text(ANSWER, encoding="utf-8")
    cfg = replace(Config.from_env(), provider="replay", replay_dir=str(tmp_path))
    assert chat(cfg, [], key="R03/attempt_1") == ANSWER
    with pytest.raises(LLMError):
        chat(cfg, [], key="R03/attempt_2")
