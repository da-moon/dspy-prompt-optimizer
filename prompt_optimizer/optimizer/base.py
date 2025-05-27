"""
Base class for prompt optimization strategies.
"""

import logging
from dataclasses import dataclass, field

import dspy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
        """Set up DSPy with the Anthropic model."""
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
            logger.info(
                f"DSPy configured with model: {self.model} "
                f"(max_tokens={self.max_tokens})"
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
