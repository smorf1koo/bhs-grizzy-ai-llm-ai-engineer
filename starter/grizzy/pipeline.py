"""One request end-to-end: index -> context -> generate -> apply -> validate -> (one retry)."""
from __future__ import annotations

import json
from pathlib import Path

from grizzy.config import Config
from grizzy.workspace import make_clean_copy, unified_diff


def run_request(cfg: Config, project: Path, request: str, run_dir: Path) -> dict:
    """Process one request on a clean copy of the project; never touch `project` itself.

    Artifacts to write into run_dir: context.json (manifest), attempt_<n>_prompt.txt,
    attempt_<n>_answer.txt, attempt_<n>_validation.txt, patch.diff, result.json.

    Ready-made parts: build_index (grizzy.index), EDIT_FORMAT / parse_edits / apply_edits
    (grizzy.edits), chat (grizzy.llm), make_clean_copy / unified_diff (grizzy.workspace).

    TODO(candidate): fill in the steps below.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace = make_clean_copy(project, run_dir / "workspace")
    # 1. index = build_index(workspace)
    # 2. bundle = select_context(index, workspace, request, cfg.budget_tokens); save bundle.manifest()
    # 3. messages = [system prompt with EDIT_FORMAT, user message with the context and the request]
    # 4. for attempt in range(1, cfg.max_attempts + 1):
    #        answer = chat(cfg, messages, key=f"{run_dir.name}/attempt_{attempt}")  # save prompt and answer
    #        try: changed = apply_edits(workspace, parse_edits(answer))
    #        except EditError as e: errors = [str(e)]
    #        else: errors = check_scripts(cfg.godot_bin, workspace, changed)
    #        if not errors: break
    #        messages += [assistant answer, user message with the error text]   # the retry
    #        (reset the workspace to a clean copy before re-applying, or apply on top - your choice)
    # 5. (run_dir / "patch.diff").write_text(unified_diff(project, workspace))
    raise NotImplementedError("run_request")


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
