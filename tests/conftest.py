import pytest

from distress_core.escalation.base import TriggerContext
from distress_core.models.base import DistressModel


class FixedModel(DistressModel):
    """Fake model: returns the same score for every text, and counts its calls."""

    def __init__(self, score: float) -> None:
        self.score = score
        self.calls = 0

    def predict_proba(self, texts: list[str]) -> list[float]:
        self.calls += 1
        return [self.score] * len(texts)


class BrokenModel(DistressModel):
    """Fake model: always fails."""

    def predict_proba(self, texts: list[str]) -> list[float]:
        raise RuntimeError("model is down")


@pytest.fixture
def fixed_model():
    """Factory: fixed_model(0.37) is a model that always returns 0.37."""
    return FixedModel


@pytest.fixture
def broken_model() -> BrokenModel:
    return BrokenModel()


@pytest.fixture
def make_ctx():
    """Factory: make_ctx(text=..., p_fast=...) builds a TriggerContext with defaults."""

    def _make(
        text: str = "x", p_fast: float = 0.5, message_id: str = "tg:1:1"
    ) -> TriggerContext:
        return TriggerContext(message_id=message_id, raw_text=text, p_fast=p_fast)

    return _make
