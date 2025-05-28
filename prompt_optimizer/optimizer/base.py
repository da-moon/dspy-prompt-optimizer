"""
Base class for prompt optimization strategies.
"""

import logging
from dataclasses import dataclass, field
from typing import Final

import dspy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


@dataclass
class PromptOptimizer:
    """Base class for prompt optimization strategies."""

    model: str
    api_key: str
    verbose: bool = False
    max_iterations: int = field(default=3, kw_only=True)
    max_tokens: int = field(default=64000, kw_only=True)
    lm: dspy.LM = field(init=False)

    def __post_init__(self) -> None:
        """Initialize DSPy after dataclass initialization."""
        # Set up DSPy with Anthropic
        self._setup_dspy()

    def _setup_dspy(self) -> None:
        """Configure DSPy for use with the Anthropic model.

        This method instantiates :class:`dspy.LM` using ``self.model`` and
        ``self.api_key``. The resulting language model is stored on
        ``self.lm`` and registered as the default via :func:`dspy.configure`.
        When ``self.verbose`` is ``True`` a log message noting the chosen
        model and ``max_tokens`` is emitted.

        Args:
            None: All configuration values are read from the instance
                attributes.

        Raises:
            ValueError: If ``api_key`` is empty.
            RuntimeError: If the language model cannot be created or DSPy
                configuration fails.
        """
        # Configure the LM using Anthropic with custom max_tokens
        self.lm = dspy.LM(
            self.model,
            provider="anthropic",
            api_key=self.api_key,
            max_tokens=self.max_tokens,
        )

        # Set the LM as the default for DSPy
        dspy.configure(lm=self.lm)

        if self.verbose:
            LOGGER.info(
                "DSPy configured with model: %s (max_tokens=%s)",
                self.model,
                self.max_tokens,
            )

    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the given prompt.

        Args:
            prompt_text: The prompt text to optimize

        Returns:
            The optimized prompt text
        """
        raise NotImplementedError("Subclasses must implement the optimize method")
