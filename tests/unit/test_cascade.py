import pytest

from distress_core.cascade import Cascade
from distress_core.contracts.prediction import DecidedBy
from distress_core.escalation.negation import NegationTrigger
from distress_core.escalation.uncertainty import UncertaintyTrigger

TRIGGERS = [UncertaintyTrigger(0.25, 0.75), NegationTrigger()]


def test_confident_fast_model_decides_alone(fixed_model):
    bert = fixed_model(0.99)
    cascade = Cascade(fixed_model(0.05), bert, TRIGGERS, 0.5, 0.5)

    result = cascade.predict("tg:1:1", "Great game today")

    assert result.decided_by == DecidedBy.TFIDF
    assert result.is_distress is False
    assert result.escalation_reasons == ()
    assert result.p_bert is None
    assert bert.calls == 0


def test_escalation_lets_distilbert_decide_and_records_reasons(fixed_model):
    cascade = Cascade(fixed_model(0.37), fixed_model(0.96), TRIGGERS, 0.5, 0.5)

    result = cascade.predict("tg:1:1", "I am not okay")

    assert result.decided_by == DecidedBy.DISTILBERT
    assert result.is_distress is True
    assert result.p_distress == 0.96
    assert result.p_fast == 0.37
    assert result.escalation_reasons == ("uncertainty", "negation")


def test_distilbert_failure_propagates(fixed_model, broken_model):
    cascade = Cascade(fixed_model(0.37), broken_model, TRIGGERS, 0.5, 0.5)

    with pytest.raises(RuntimeError):
        cascade.predict("tg:1:1", "I am not okay")


def test_invalid_threshold_is_rejected(fixed_model):
    with pytest.raises(ValueError):
        Cascade(fixed_model(0.5), fixed_model(0.5), TRIGGERS, 1.5, 0.5)
