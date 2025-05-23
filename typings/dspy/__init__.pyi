from typing import Any

class LM:
    def __init__(self, model: str, provider: str, api_key: str) -> None: ...

class Signature:
    pass

class InputField:
    def __init__(self, desc: str) -> None: ...

class OutputField:
    def __init__(self, desc: str) -> None: ...

class Predict:
    def __init__(self, signature: type[Signature]) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> object: ...

class ChainOfThought(Predict):
    def update_demos(self, demos: list[Example]) -> None: ...

class Example:
    def __init__(self, **kwargs: Any) -> None: ...

class Settings:
    def configure(self, *, lm: LM) -> None: ...

settings: Settings
