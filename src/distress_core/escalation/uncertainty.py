from distress_core.escalation.base import EscalationTrigger, TriggerContext


class UncertaintyTrigger(EscalationTrigger):
    """Escalates when the fast model's score falls inside [low, high]."""

    name = "uncertainty"

    def __init__(self, low: float, high: float) -> None:
        if not 0.0 <= low <= high <= 1.0:
            raise ValueError(
                f"Expected 0 <= low <= high <= 1, got low={low}, high={high}"
            )
        self._low = low
        self._high = high

    def should_escalate(self, ctx: TriggerContext) -> bool:
        return self._low <= ctx.p_fast <= self._high
