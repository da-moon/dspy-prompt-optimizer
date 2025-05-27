"""Minimal runtime stub for the DSPy library used in tests."""

class Signature:
    """Base class for DSPy signatures."""

    pass


def InputField(*, desc: str) -> None:
    """Placeholder for InputField."""
    return None


def OutputField(*, desc: str) -> None:
    """Placeholder for OutputField."""
    return None


class Predict:
    """Placeholder for Predict."""

    def __init__(self, signature: type) -> None:
        self.signature = signature

    def __call__(self, **_kwargs: object) -> None:
        return None


class ChainOfThought(Predict):
    """Placeholder for ChainOfThought."""

    pass


class Example:
    """Placeholder for Example."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass


class LM:
    """Placeholder for LM."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass


def configure(*, lm: LM) -> None:
    """Placeholder configure function."""
    return None
