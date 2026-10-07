from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DecidedBy(str, Enum):
    """Which model made the final decision for a message."""

    TFIDF = "tfidf"
    DISTILBERT = "distilbert"


class PredictionResult(BaseModel):
    """The cascade's output for one message.

    Holds no message identity: the stored record holds the identity
    and contains this result (composition).
    """

    model_config = ConfigDict(frozen=True)

    is_distress: bool
    p_distress: float = Field(ge=0.0, le=1.0)
    decided_by: DecidedBy
    escalation_reasons: tuple[str, ...]
    p_fast: float = Field(ge=0.0, le=1.0)
    p_bert: float | None = Field(default=None, ge=0.0, le=1.0)
