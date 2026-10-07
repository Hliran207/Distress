from distress_core.cascade import Cascade
from distress_core.escalation.audit import AuditTrigger
from distress_core.escalation.base import EscalationTrigger
from distress_core.escalation.negation import NegationTrigger
from distress_core.escalation.uncertainty import UncertaintyTrigger
from distress_core.models.bert import BertModel
from distress_core.models.fast import FastModel
from distress_core.settings import CascadeSettings


def build_triggers(settings: CascadeSettings) -> list[EscalationTrigger]:
    """The enabled triggers, in a fixed order."""
    triggers: list[EscalationTrigger] = []
    if settings.uncertainty_enabled:
        triggers.append(
            UncertaintyTrigger(settings.uncertainty_low, settings.uncertainty_high)
        )
    if settings.negation_enabled:
        triggers.append(NegationTrigger())
    if settings.audit_rate > 0:
        triggers.append(AuditTrigger(settings.audit_rate))
    return triggers


def build_cascade(settings: CascadeSettings) -> Cascade:
    """Load both models from the HF Hub and assemble the cascade. Called once, at startup."""
    return Cascade(
        fast=FastModel.from_hub(settings.hf_repo_id, settings.hf_revision),
        bert=BertModel.from_hub(settings.hf_repo_id, settings.hf_revision),
        triggers=build_triggers(settings),
        fast_threshold=settings.fast_threshold,
        bert_threshold=settings.bert_threshold,
    )
