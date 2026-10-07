import hashlib

from distress_core.escalation.base import EscalationTrigger, TriggerContext

_BUCKETS = 10_000


class AuditTrigger(EscalationTrigger):
    """Escalates a deterministic sample of messages, for monitoring.

    The same message id always gets the same decision, so a message
    redelivered by Kafka is handled exactly the same way.
    """

    name = "audit"

    def __init__(self, rate: float) -> None:
        if not 0.0 <= rate <= 1.0:
            raise ValueError(f"Expected 0 <= rate <= 1, got rate={rate}")
        self._threshold = round(rate * _BUCKETS)

    def should_escalate(self, ctx: TriggerContext) -> bool:
        return _bucket(ctx.message_id) < self._threshold


def _bucket(message_id: str) -> int:
    """Map a message id to a stable number in [0, _BUCKETS)."""
    digest = hashlib.sha256(message_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % _BUCKETS
