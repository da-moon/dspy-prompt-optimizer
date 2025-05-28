"""Minimal type stubs for dspy library - precisely typed based on actual usage."""

from typing import Protocol, Type, runtime_checkable

from pydantic.fields import FieldInfo

# Protocol for DSPy result objects that have dynamic attributes
@runtime_checkable
class DSPyResult(Protocol):
    """Protocol for objects returned by DSPy predict/chain calls."""

    def __getattr__(self, name: str) -> str: ...

    # Explicit attributes that we know return strings
    @property
    def analysis(self) -> str: ...
    @property
    def improved_prompt(self) -> str: ...
    @property
    def total_score(self) -> str: ...
    @property
    def feedback(self) -> str: ...

# Only the field functions we use - being specific about our usage
def InputField(*, desc: str) -> FieldInfo: ...
def OutputField(*, desc: str) -> FieldInfo: ...

# Base Signature class
class SignatureMeta(type):
    """Metaclass for Signature to enable subclassing."""

    pass

class Signature(metaclass=SignatureMeta):
    """Base class for DSPy signatures."""

    pass

# Example class - only what we use, specific to our kwargs
class Example:
    def __init__(self, *, prompt: str, analysis: str, improved_prompt: str) -> None: ...
    @property
    def prompt(self) -> str: ...
    @property
    def analysis(self) -> str: ...
    @property
    def improved_prompt(self) -> str: ...

# LM class - only what we use
class LM:
    def __init__(
        self,
        model: str,
        provider: str,
        api_key: str,
        max_tokens: int = ...,
    ) -> None: ...

# Predict and ChainOfThought - based on our actual usage patterns
class Predict:
    def __init__(self, signature: Type[Signature]) -> None: ...
    def __call__(
        self, *, prompt: str = ..., original_prompt: str = ...
    ) -> DSPyResult: ...

class ChainOfThought:
    def __init__(self, signature: Type[Signature]) -> None: ...
    def __call__(
        self,
        *,
        prompt: str = ...,
        original_prompt: str = ...,
        examples: str = ...,
    ) -> DSPyResult: ...

# Module-level configure function - only what we use
def configure(*, lm: LM) -> None: ...
