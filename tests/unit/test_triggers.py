import pytest

from distress_core.escalation.audit import AuditTrigger, _bucket
from distress_core.escalation.negation import NegationTrigger
from distress_core.escalation.uncertainty import UncertaintyTrigger


@pytest.mark.parametrize(
    ("p_fast", "expected"),
    [
        (0.25, True),
        (0.50, True),
        (0.75, True),
        (0.2499, False),
        (0.7501, False),
        (0.05, False),
        (0.98, False),
    ],
)
def test_uncertainty_fires_inside_band_inclusive(make_ctx, p_fast, expected):
    trigger = UncertaintyTrigger(low=0.25, high=0.75)

    assert trigger.should_escalate(make_ctx(p_fast=p_fast)) is expected


def test_uncertainty_rejects_inverted_band():
    with pytest.raises(ValueError):
        UncertaintyTrigger(low=0.75, high=0.25)


@pytest.mark.parametrize(
    "text",
    [
        "I am not okay",
        "no one cares",
        "I don't want this",
        "I dont care",
        "I can’t do this",
        "NEVER again",
        "Nothing matters",
    ],
)
def test_negation_fires_on_negations(make_ctx, text):
    assert NegationTrigger().should_escalate(make_ctx(text=text)) is True


@pytest.mark.parametrize(
    "text",
    [
        "I know",
        "a short note",
        "I noticed it",
        "I want help",
        "I went home",
        "an important point",
        "Nottingham is nice",
    ],
)
def test_negation_ignores_look_alike_words(make_ctx, text):
    assert NegationTrigger().should_escalate(make_ctx(text=text)) is False


def test_audit_bucket_is_stable_across_runs():
    assert _bucket("tg:1:2") == 2754


@pytest.mark.parametrize(("rate", "expected"), [(0.0, 0), (1.0, 100)])
def test_audit_rate_extremes(make_ctx, rate, expected):
    trigger = AuditTrigger(rate=rate)

    selected = sum(
        trigger.should_escalate(make_ctx(message_id=f"tg:1:{i}")) for i in range(100)
    )

    assert selected == expected
