from pydantic import AwareDatetime, BaseModel, Field

from distress_core.contracts.prediction import PredictionResult
from distress_core.contracts.records import TelegramMessageRecord


class PredictRequest(BaseModel):
    """Body of POST /predict."""

    text: str = Field(min_length=1, max_length=5000)


class MessageOut(BaseModel):
    """A stored message as the API returns it, decoupled from the MongoDB document."""

    id: str
    sender_name: str | None
    text: str
    sent_at: AwareDatetime
    prediction: PredictionResult

    @classmethod
    def from_record(cls, record: TelegramMessageRecord) -> "MessageOut":
        return cls(
            id=record.id,
            sender_name=record.sender_name,
            text=record.text,
            sent_at=record.sent_at,
            prediction=record.prediction,
        )
