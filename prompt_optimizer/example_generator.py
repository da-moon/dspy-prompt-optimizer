"""Example generator for DSPy prompts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import dspy


@dataclass
class ExampleGenerator:
    """Generate and persist :class:`dspy.Example` objects."""

    model: str
    api_key: str
    num_examples: int
    max_tokens: int
    verbose: bool = False
    lm: dspy.LM = field(init=False)

    def __post_init__(self) -> None:
        """Initialize :mod:`dspy` with an Anthropic language model."""
        if not self.model:
            raise ValueError("model cannot be empty")
        if not self.api_key:
            raise ValueError("api_key cannot be empty")
        if self.num_examples <= 0 or self.max_tokens <= 0:
            raise ValueError("num_examples and max_tokens must be positive")
        self.lm = dspy.LM(
            self.model,
            provider="anthropic",
            api_key=self.api_key,
            max_tokens=self.max_tokens,
        )
        dspy.configure(lm=self.lm)

    def generate_examples(self, prompt: str) -> list[dspy.Example]:
        """Return a list of simple prompt improvement examples."""
        if not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        return [
            dspy.Example(
                prompt=prompt,
                analysis=f"Example {i + 1}",
                improved_prompt=f"{prompt} improved {i + 1}",
            )
            for i in range(self.num_examples)
        ]

    def load_examples(self, path: Path) -> list[dspy.Example]:
        """Load examples from ``path``."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
        return [dspy.Example(**item) for item in data]

    def save_examples(self, examples: Iterable[dspy.Example], path: Path) -> None:
        """Save ``examples`` to ``path`` as JSON."""
        data = [ex.__dict__ for ex in examples]
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            _ = path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except PermissionError as exc:
            raise PermissionError(f"Cannot write to {path}: {exc}") from exc
