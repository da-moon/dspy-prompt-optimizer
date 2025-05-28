from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest import MonkeyPatch

import pytest

import prompt_optimizer.optimizer.base as base_module
import prompt_optimizer.optimizer.example_based.generator as example_generator_module
import prompt_optimizer.optimizer.example_based.optimizer as example_based_optimizer_module
import prompt_optimizer.optimizer.metric_based as metric_based_module
import prompt_optimizer.optimizer.self_refinement as self_refinement_module
from prompt_optimizer.optimizer import (
    ExampleBasedOptimizer,
    MetricBasedOptimizer,
    SelfRefinementOptimizer,
    optimize_prompt,
)


@pytest.fixture
def mock_dspy(monkeypatch: "MonkeyPatch") -> None:
    class FakePredict:
        def __init__(self, signature: object) -> None:
            self.signature = signature

        def __call__(self, **kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(improved_prompt="improved", analysis="analysis")

    class FakeChainOfThought(FakePredict):
        def __init__(self, signature: object) -> None:
            super().__init__(signature)
            self.call_count = 0

        def __call__(self, **kwargs: object) -> SimpleNamespace:
            self.call_count += 1
            # First call (evaluation of original) gets score 5, subsequent calls get score 15
            # This ensures the generated prompt is "better" than the original
            score = "5" if self.call_count == 1 else "15"
            return SimpleNamespace(
                improved_prompt="improved",
                analysis="analysis",
                total_score=score,
                feedback="feedback",
                clarity_score="10",
                specificity_score="10",
                actionability_score="10",
            )

    def mock_input_field(*_args: object, **_kwargs: object) -> None:
        return None

    def mock_output_field(*_args: object, **_kwargs: object) -> None:
        return None

    def mock_example(*_args: object, **kwargs: object) -> SimpleNamespace:
        # Return a SimpleNamespace with the provided keyword arguments
        return SimpleNamespace(**kwargs)

    def mock_configure(**_kwargs: object) -> None:
        return None

    def mock_lm(*_args: object, **_kwargs: object) -> None:
        return None

    fake_dspy = SimpleNamespace(
        Signature=object,
        InputField=mock_input_field,
        OutputField=mock_output_field,
        Predict=FakePredict,
        ChainOfThought=FakeChainOfThought,
        Example=mock_example,
        configure=mock_configure,
        LM=mock_lm,
    )

    # Mock dspy in each individual module
    monkeypatch.setattr(base_module, "dspy", fake_dspy)
    monkeypatch.setattr(self_refinement_module, "dspy", fake_dspy)
    monkeypatch.setattr(example_based_optimizer_module, "dspy", fake_dspy)
    monkeypatch.setattr(example_generator_module, "dspy", fake_dspy)
    monkeypatch.setattr(metric_based_module, "dspy", fake_dspy)

    class FakeExampleGenerator:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

        def generate_examples(self) -> list[SimpleNamespace]:
            return [fake_dspy.Example(prompt="p", analysis="a", improved_prompt="i")]

    monkeypatch.setattr(
        example_generator_module, "ExampleGenerator", FakeExampleGenerator
    )
    monkeypatch.setattr(
        example_based_optimizer_module, "ExampleGenerator", FakeExampleGenerator
    )


def test_self_refinement_optimizer(mock_dspy: None) -> None:
    opt = SelfRefinementOptimizer(model="m", api_key="k", max_tokens=64000)
    result = opt.optimize("prompt")
    assert result == "improved"


def test_example_based_optimizer(mock_dspy: None) -> None:
    opt = ExampleBasedOptimizer(model="m", api_key="k", max_tokens=64000)
    result = opt.optimize("prompt")
    assert result == "improved"


def test_example_based_optimizer_dspy_compatibility(mock_dspy: None) -> None:
    """Test that example-based optimizer doesn't use non-existent DSPy methods."""
    opt = ExampleBasedOptimizer(model="m", api_key="k", max_tokens=64000)

    # This should not raise AttributeError about 'update_demos'
    # If the old code with update_demos was still there, this would fail
    result = opt.optimize("test prompt")
    assert result == "improved"

    # The real test is that the above doesn't throw an AttributeError
    # If the old update_demos code was still present, we'd get:
    # AttributeError: 'ChainOfThought' object has no attribute 'update_demos'


def test_metric_based_optimizer(mock_dspy: None) -> None:
    opt = MetricBasedOptimizer(model="m", api_key="k", max_tokens=64000)
    result = opt.optimize("prompt")
    assert result == "improved"


def test_metric_based_optimizer_with_custom_iterations(mock_dspy: None) -> None:
    opt = MetricBasedOptimizer(
        model="m", api_key="k", max_iterations=5, max_tokens=64000
    )
    assert opt.max_iterations == 5
    result = opt.optimize("prompt")
    assert result == "improved"


def test_optimize_prompt_function(mock_dspy: None) -> None:
    """Test the convenience function for each optimization type."""
    # Test self-refinement (default)
    result = optimize_prompt(
        prompt_text="test prompt", model="model", api_key="api_key"
    )
    assert result == "improved"

    # Test example-based
    result = optimize_prompt(
        prompt_text="test prompt",
        model="model",
        api_key="api_key",
        optimization_type="example",
    )
    assert result == "improved"

    # Test metric-based
    result = optimize_prompt(
        prompt_text="test prompt",
        model="model",
        api_key="api_key",
        optimization_type="metric",
    )
    assert result == "improved"

    # Test metric-based with custom max_iterations
    result = optimize_prompt(
        prompt_text="test prompt",
        model="model",
        api_key="api_key",
        optimization_type="metric",
        max_iterations=5,
    )
    assert result == "improved"

    # Test invalid optimization type
    with pytest.raises(ValueError, match="Unknown optimization type"):
        _ = optimize_prompt(
            prompt_text="test prompt",
            model="model",
            api_key="api_key",
            optimization_type="invalid",
        )
