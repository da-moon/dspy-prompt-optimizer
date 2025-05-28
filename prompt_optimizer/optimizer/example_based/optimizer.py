"""Example-based prompt optimizer."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, cast, Any

import dspy

from .generator import ExampleGenerator
from ..base import PromptOptimizer

logger: Final[logging.Logger] = logging.getLogger(__name__)


# Removed hardcoded examples - all examples are now generated dynamically


def _load_examples_from_file(path: Path) -> list[dspy.Example]:
    """Load examples from a JSON file."""

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected error reading {path}: {exc}") from exc

    try:
        raw_data: object = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw_data, list):
        raise ValueError("Examples file must contain a list of objects")

    # raw_data is confirmed to be a list, but we need to validate it's the right type  
    raw_examples: list[Any] = raw_data  # pyright: ignore[reportUnknownVariableType]

    examples: list[dspy.Example] = []
    for item in raw_examples:
        if not isinstance(item, dict):
            raise ValueError("Each example entry must be an object")
        entry: dict[str, Any] = cast(dict[str, Any], item)
        examples.append(
            dspy.Example(
                prompt=str(entry.get("prompt", "")),
                analysis=str(entry.get("analysis", "")),
                improved_prompt=str(entry.get("improved_prompt", "")),
            )
        )

    return examples


def _format_examples(examples: list[dspy.Example]) -> str:
    """Return a formatted string representing prompt transformation examples."""

    return "\n\n".join(
        [
            f"Original: {ex.prompt}\n"
            + f"Analysis: {ex.analysis}\n"
            + f"Improved: {ex.improved_prompt}"
            for ex in examples
        ]
    )


@dataclass
class ExampleBasedOptimizer(PromptOptimizer):
    """Optimizer that uses examples to improve prompts."""

    examples: list[dspy.Example] | None = None
    examples_file: Path | None = None
    example_generator_model: str | None = None
    example_generator_api_key: str | None = None
    example_generator_max_tokens: int | None = None
    num_examples: int = 3
    _examples: list[dspy.Example] = field(init=False)

    def __post_init__(self) -> None:  # noqa: D401
        """Initialize optimizer and prepare examples."""
        super().__post_init__()

        if self.examples is not None:
            self._examples = self.examples
        elif self.examples_file is not None:
            self._examples = _load_examples_from_file(self.examples_file)
        else:
            generator = ExampleGenerator(
                model=self.example_generator_model or "claude-3-5-haiku-latest",
                api_key=self.example_generator_api_key or self.api_key,
                num_examples=self.num_examples,
                max_tokens=self.example_generator_max_tokens or self.max_tokens,
                verbose=self.verbose,
            )
            self._examples = generator.generate_examples()

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using example-based optimization.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info("Using example-based optimization approach")

        # Define a signature for prompt refinement with examples
        class ExamplePromptRefiner(dspy.Signature):
            """Refine a prompt based on examples of good prompts."""

            prompt = dspy.InputField(desc="The original prompt that needs refinement")
            examples = dspy.InputField(
                desc="Examples of good prompt transformations to learn from"
            )
            analysis = dspy.OutputField(
                desc="Analysis of the prompt's strengths and weaknesses"
            )
            improved_prompt = dspy.OutputField(
                desc="A refined version of the prompt that addresses the weaknesses"
            )

        # Format examples as context text
        examples_text = _format_examples(self._examples)
        # Create a module that uses the signature with examples
        refiner: dspy.ChainOfThought = dspy.ChainOfThought(ExamplePromptRefiner)

        # Apply the module with examples as context to refine the prompt
        refinement_payload = refiner(prompt=prompt_text, examples=examples_text)

        if self.verbose:
            logger.info(f"Analysis: {refinement_payload.analysis}")

        return refinement_payload.improved_prompt