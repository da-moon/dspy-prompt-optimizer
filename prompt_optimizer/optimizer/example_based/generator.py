"""Example generator for DSPy prompts - localized for example-based optimization."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import dspy


@dataclass
class ExampleGenerator:
    """Generate and persist :class:`dspy.Example` objects for example-based optimization."""

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

    def generate_examples(self) -> list[dspy.Example]:
        """Generate prompt improvement examples using the LLM."""

        # Define a signature for generating prompt optimization examples
        class ExampleGeneratorSignature(dspy.Signature):
            """Generate examples of prompt optimization."""

            task_description = dspy.InputField(
                desc="Description of the task for generating examples"
            )
            num_examples = dspy.InputField(desc="Number of examples to generate")
            examples = dspy.OutputField(
                desc="List of prompt optimization examples in JSON format with fields: prompt, analysis, improved_prompt"
            )

        # Create the example generation module
        example_generator = dspy.ChainOfThought(ExampleGeneratorSignature)

        # Generate examples
        task_desc = (
            "Generate diverse examples of prompt optimization showing how to improve "
            "vague, unclear, or poorly structured prompts. Each example should demonstrate "
            "common prompt improvement techniques like adding specificity, context, "
            "constraints, output format requirements, or role clarification."
        )

        if self.verbose:
            print(
                f"Generating {self.num_examples} examples using model {self.model}..."
            )

        # Call with dynamic arguments - type checkers don't understand dspy signatures  
        result = example_generator(  # type: ignore[call-arg]
            task_description=task_desc,  # pyright: ignore[reportCallIssue]
            num_examples=str(self.num_examples)  # pyright: ignore[reportCallIssue]
        )

        # Parse the generated examples
        try:
            import re

            # Extract JSON from the response (handle markdown code blocks)
            examples_text = str(getattr(result, "examples", ""))  # pyright: ignore[reportUnknownArgumentType]
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", examples_text)
            json_str: str
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = examples_text

            examples_data: list[dict[str, str]] = json.loads(json_str)

            # Convert to dspy.Example objects
            examples: list[dspy.Example] = []
            for ex_data in examples_data:
                examples.append(
                    dspy.Example(
                        prompt=str(ex_data.get("prompt", "")),
                        analysis=str(ex_data.get("analysis", "")),
                        improved_prompt=str(ex_data.get("improved_prompt", "")),
                    )
                )

            if self.verbose:
                print(f"Successfully generated {len(examples)} examples")

            return examples

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            if self.verbose:
                print(f"Failed to parse generated examples: {e}")
                print(f"Raw response: {getattr(result, 'examples', 'No examples attribute')}")  # pyright: ignore[reportUnknownArgumentType]

            # Re-raise the error instead of falling back to hardcoded examples
            raise RuntimeError(f"Failed to generate examples: {e}") from e

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

    def write_examples(self, path: Path) -> None:
        """Generate and write examples to a file."""
        examples = self.generate_examples()
        self.save_examples(examples, path)