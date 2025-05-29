"""Example-based prompt optimizer."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, cast

import dspy

from ..base import PromptOptimizer
from ..strategies import ExampleBasedConfig, OptimizationStrategy
from .generator import ExampleGenerator

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


# Removed hardcoded examples - all examples are now generated dynamically


def _load_examples_from_file(path: Path) -> list[dspy.Example]:
    """Load examples from a JSON file."""

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, IOError) as exc:
        raise RuntimeError(f"Unexpected error reading {path}: {exc}") from exc

    try:
        raw_data: object = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw_data, list):
        raise ValueError("Examples file must contain a list of objects")

    # raw_data is confirmed to be a list, but we need to validate it's the right type
    raw_examples: list[dict[str, object]] = cast(list[dict[str, object]], raw_data)

    examples: list[dspy.Example] = [
        dspy.Example(
            prompt=str(item.get("prompt", "")),
            analysis=str(item.get("analysis", "")),
            improved_prompt=str(item.get("improved_prompt", "")),
        )
        for item in raw_examples
    ]
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


@dataclass(init=False)
class ExampleBasedOptimizer(PromptOptimizer, OptimizationStrategy):
    """Optimizer that uses examples to improve prompts."""

    examples: list[dspy.Example] | None = None
    examples_file: Path | None = None
    example_generator_model: str | None = None
    example_generator_api_key: str | None = None
    example_generator_max_tokens: int | None = None
    num_examples: int = 3
    _examples: list[dspy.Example] = field(init=False)

    def __init__(self, config: ExampleBasedConfig) -> None:
        """Initialize the optimizer using ``config``."""
        super().__init__(
            model=config.model,
            api_key=config.api_key,
            max_tokens=config.max_tokens,
            verbose=config.verbose,
        )
        self.examples = config.examples
        self.examples_file = config.examples_file
        self.example_generator_model = config.example_generator_model
        self.example_generator_api_key = config.example_generator_api_key
        self.example_generator_max_tokens = config.example_generator_max_tokens
        self.num_examples = config.num_examples
        self._examples = self._initialize_examples()

    def _initialize_examples(self) -> list[dspy.Example]:
        """Initialize examples from config or generate them."""
        if self.examples is not None:
            return self.examples

        if self.examples_file is not None:
            return _load_examples_from_file(self.examples_file)

        return self._generate_examples()

    def _generate_examples(self) -> list[dspy.Example]:
        """Generate examples using the example generator."""
        example_max_tokens = self.example_generator_max_tokens or self.max_tokens

        if self.verbose:
            LOGGER.info(
                "Generating examples with example_generator_max_tokens=%s",
                example_max_tokens,
            )

        generator = ExampleGenerator(
            model=self.example_generator_model or "claude-3-5-haiku-latest",
            api_key=self.example_generator_api_key or self.api_key,
            num_examples=self.num_examples,
            max_tokens=example_max_tokens,
            verbose=self.verbose,
        )
        return generator.generate_examples()

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using example-based optimization.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        if self.verbose:
            LOGGER.info("Using example-based optimization approach")

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
            LOGGER.info("Analysis: %s", refinement_payload.analysis)

        return refinement_payload.improved_prompt
