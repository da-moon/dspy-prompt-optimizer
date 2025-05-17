from types import SimpleNamespace
import pytest

import prompt_optimizer.optimizer as optimizer


@pytest.fixture
def mock_dspy(monkeypatch):
    class FakePredict:
        def __init__(self, signature):
            self.signature = signature

        def __call__(self, **kwargs):
            return SimpleNamespace(improved_prompt="improved", analysis="analysis")

    class FakeChainOfThought(FakePredict):
        def update_demos(self, demos):
            # No-op for demo update
            pass

        def __call__(self, **kwargs):
            return SimpleNamespace(
                improved_prompt="improved",
                analysis="analysis",
                total_score="10",
                feedback="feedback",
                clarity_score="10",
                specificity_score="10",
                actionability_score="10",
            )

    fake_dspy = SimpleNamespace(
        Signature=object,
        InputField=lambda *a, **kw: None,
        OutputField=lambda *a, **kw: None,
        Predict=FakePredict,
        ChainOfThought=FakeChainOfThought,
        Example=lambda *a, **kw: SimpleNamespace(),
        settings=SimpleNamespace(configure=lambda **kw: None),
        LM=lambda **kw: None,
    )

    monkeypatch.setattr(optimizer, "dspy", fake_dspy)


def test_self_refinement_optimizer(mock_dspy):
    opt = optimizer.SelfRefinementOptimizer(model="m", api_key="k")
    result = opt.optimize("prompt")
    assert result == "improved"


def test_example_based_optimizer(mock_dspy):
    opt = optimizer.ExampleBasedOptimizer(model="m", api_key="k")
    result = opt.optimize("prompt")
    assert result == "improved"


def test_metric_based_optimizer(mock_dspy):
    opt = optimizer.MetricBasedOptimizer(model="m", api_key="k")
    result = opt.optimize("prompt")
    assert result == "improved"
