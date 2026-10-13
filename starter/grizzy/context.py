"""Context selection under a token budget."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """Rough estimate (~4 characters per token). Fine for the task if documented."""
    return max(1, len(text) // 4)


@dataclass
class ContextBundle:
    files: dict[str, str] = field(default_factory=dict)  # res:// path -> text put into the prompt
    notes: list[str] = field(default_factory=list)  # why each file was chosen / what was cut

    @property
    def tokens(self) -> int:
        return sum(estimate_tokens(t) for t in self.files.values())

    def manifest(self) -> dict:
        """What goes to runs/<id>/context.json."""
        return {"tokens": self.tokens,
                "files": {p: estimate_tokens(t) for p, t in self.files.items()},
                "notes": self.notes}


def select_context(index: dict, project: Path, request: str, budget_tokens: int) -> ContextBundle:
    """Pick the files (or parts of files) of `project` the model needs for this request.

    TODO(candidate): implement a SIMPLE strategy and describe it in README, e.g.
      1) find entities mentioned in the request (keywords -> scripts / scenes / nodes);
      2) add their neighbours from index["edges"] (uses_script, instances, overrides,
         signal_handler, uses_autoload);
      3) stop at the budget; if something does not fit, shorten it (signatures instead of bodies,
         only the relevant nodes of a scene).
    The budget counts only project files in the prompt, not the instructions.
    """
    raise NotImplementedError("select_context")
