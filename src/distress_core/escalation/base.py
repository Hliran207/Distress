from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field


class TriggerContext(BaseModel):
    """Everything a trigger may need to decide about one message."""

    model_config = ConfigDict(frozen=True)

    message_id: str
    raw_text: str
    p_fast: float = Field(ge=0.0, le=1.0)


class EscalationTrigger(ABC):
    """One rule for deciding whether a message needs DistilBERT (Strategy pattern)."""

    name: str

    @abstractmethod
    def should_escalate(self, ctx: TriggerContext) -> bool:
        """Return True if this message should be escalated to DistilBERT."""
