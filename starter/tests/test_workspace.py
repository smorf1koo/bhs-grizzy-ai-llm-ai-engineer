from pathlib import Path

from grizzy.context import estimate_tokens
from grizzy.workspace import make_clean_copy, unified_diff


def test_copy_and_diff(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "scripts").mkdir(parents=True)
    (src / "scripts" / "a.gd").write_text("extends Node\n", encoding="utf-8")
    copy = make_clean_copy(src, tmp_path / "copy")
    (copy / "scripts" / "a.gd").write_text("extends Node2D\n", encoding="utf-8")
    diff = unified_diff(src, copy)
    assert "-extends Node\n" in diff and "+extends Node2D\n" in diff
    assert (src / "scripts" / "a.gd").read_text(encoding="utf-8") == "extends Node\n"


def test_estimate_tokens() -> None:
    assert estimate_tokens("x" * 400) == 100


# TODO(candidate): add tests for your context selection and validation parsing
