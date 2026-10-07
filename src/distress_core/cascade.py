from distress_core.contracts.prediction import DecidedBy, PredictionResult
from distress_core.escalation.base import EscalationTrigger, TriggerContext
from distress_core.models.base import DistressModel


class Cascade:
    """Scores a text with the fast model, and escalates to DistilBERT when any trigger fires."""

    def __init__(
        self,
        fast: DistressModel,
        bert: DistressModel,
        triggers: list[EscalationTrigger],
        fast_threshold: float,
        bert_threshold: float,
    ) -> None:
        for threshold in (fast_threshold, bert_threshold):
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"Thresholds must be in [0, 1], got {threshold}")
        self._fast = fast
        self._bert = bert
        self._triggers = tuple(triggers)
        self._fast_threshold = fast_threshold
        self._bert_threshold = bert_threshold

    def predict(self, message_id: str, text: str) -> PredictionResult:
        p_fast = self._fast.predict_one(text)
        ctx = TriggerContext(message_id=message_id, raw_text=text, p_fast=p_fast)
        reasons = tuple(t.name for t in self._triggers if t.should_escalate(ctx))

        if not reasons:
            return PredictionResult(
                is_distress=p_fast >= self._fast_threshold,
                p_distress=p_fast,
                decided_by=DecidedBy.TFIDF,
                escalation_reasons=(),
                p_fast=p_fast,
            )

        p_bert = self._bert.predict_one(text)
        return PredictionResult(
            is_distress=p_bert >= self._bert_threshold,
            p_distress=p_bert,
            decided_by=DecidedBy.DISTILBERT,
            escalation_reasons=reasons,
            p_fast=p_fast,
            p_bert=p_bert,
        )
