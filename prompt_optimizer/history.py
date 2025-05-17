from __future__ import annotations

"""History logging utilities for DSPy Prompt Optimizer."""

import json
from pathlib import Path
from typing import Any, List, Mapping

HISTORY_PATH = Path.home() / ".dspy_prompt_optimizer" / "history.log"


def record_history(data: Mapping[str, Any], log_file: Path = HISTORY_PATH) -> None:
    """Append a JSON entry to the history log."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        json.dump(dict(data), fh)
        fh.write("\n")


def load_history(
    limit: int | None = None, log_file: Path = HISTORY_PATH
) -> List[dict[str, Any]]:
    """Load history entries from the log.

    Parameters
    ----------
    limit:
        Maximum number of entries to return from the end of the file.
    log_file:
        Path to the history log file.
    """
    if not log_file.exists():
        return []

    with log_file.open("r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    if limit is not None:
        lines = lines[-limit:]

    entries: List[dict[str, Any]] = []
    for line in lines:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries
