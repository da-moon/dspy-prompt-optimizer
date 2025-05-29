"""Example generator for DSPy prompts - localized for example-based optimization."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, cast

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
        example_generator = self._build_generation_module()
        task_desc = self._create_task_description()
        self._log_generation_start()
        examples_text = self._generate_examples_text(example_generator, task_desc)
        return self._parse_response(examples_text)

    def _log_generation_start(self) -> None:
        """Log the start of example generation."""
        if self.verbose:
            print(
                f"Generating {self.num_examples} examples using model {self.model}..."
            )

    def _generate_examples_text(self, example_generator: dspy.ChainOfThought, task_desc: str) -> str:
        """Generate examples text using the LLM."""
        result_callable = getattr(example_generator, "__call__")
        result = result_callable(
            task_description=task_desc, num_examples=str(self.num_examples)
        )
        return str(getattr(result, "examples", ""))

    def _build_generation_module(self) -> dspy.ChainOfThought:
        """Create the dspy module used for example generation."""

        class ExampleGeneratorSignature(dspy.Signature):
            """Signature defining the example generation interface."""

            task_description = dspy.InputField(
                desc="Description of the task for generating examples"
            )
            num_examples = dspy.InputField(desc="Number of examples to generate")
            examples = dspy.OutputField(
                desc=(
                    "List of prompt optimization examples in JSON format with "
                    "fields: prompt, analysis, improved_prompt"
                )
            )

        return dspy.ChainOfThought(ExampleGeneratorSignature)

    def _create_task_description(self) -> str:
        """Return the text description for the generation task."""
        return (
            "Generate diverse examples of prompt optimization showing how to "
            "improve vague, unclear, or poorly structured prompts. Each example "
            "should demonstrate common prompt improvement techniques like adding "
            "specificity, context, constraints, output format requirements, or "
            "role clarification."
        )

    def _parse_response(self, text: str) -> list[dspy.Example]:
        """Parse `text` from the model into DSPy examples."""
        if not text:
            raise ValueError("Response text must be a non-empty string")
        try:
            json_str = self._extract_json_from_text(text)
            examples_data: list[dict[str, str]] = json.loads(json_str)
            examples = self._convert_to_examples(examples_data)
            self._log_success(examples)
            return examples
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            self._log_error(exc, text)
            raise RuntimeError(f"Failed to generate examples: {exc}") from exc

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON string from text, handling markdown code blocks."""
        json_match = re.search(r"```(?:json)?\s*([^`]*?)\s*```", text)
        return json_match[1] if json_match else text

    def _convert_to_examples(self, examples_data: list[dict[str, str]]) -> list[dspy.Example]:
        """Convert raw data to DSPy examples."""
        return [
            dspy.Example(
                prompt=str(ex_data.get("prompt", "")),
                analysis=str(ex_data.get("analysis", "")),
                improved_prompt=str(ex_data.get("improved_prompt", "")),
            )
            for ex_data in examples_data
        ]

    def _log_success(self, examples: list[dspy.Example]) -> None:
        """Log successful example generation."""
        if self.verbose:
            print(f"Successfully generated {len(examples)} examples")

    def _log_error(self, exc: Exception, text: str) -> None:
        """Log error during example parsing."""
        if self.verbose:
            print(f"Failed to parse generated examples: {exc}")
            print(f"Raw response: {text}")

    def load_examples(self, path: Path) -> list[dspy.Example]:
        """Load examples from ``path``."""
        raw_obj = self._load_json_file(path)
        self._validate_json_structure(raw_obj, path)
        raw_items = cast(list[dict[str, object]], raw_obj)
        return self._create_examples_from_items(raw_items)

    def _load_json_file(self, path: Path) -> object:
        """Load and parse JSON file."""
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    def _validate_json_structure(self, raw_obj: object, _path: Path) -> None:
        """Validate that JSON contains a list."""
        if not isinstance(raw_obj, list):
            raise ValueError(f"Invalid JSON format: expected list, got {type(raw_obj)}")

    def _create_examples_from_items(
        self, raw_items: list[dict[str, object]]
    ) -> list[dspy.Example]:
        """Create DSPy examples from raw JSON items."""
        return [
            dspy.Example(**{str(k): str(v) for k, v in item.items()})
            for item in raw_items
        ]

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
