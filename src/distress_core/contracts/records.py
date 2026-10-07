from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from distress_core.contracts.messages import IncomingMessage
from distress_core.contracts.prediction import PredictionResult


class TelegramMessageRecord(BaseModel):
    """A scored Telegram message, as stored in MongoDB."""

    model_config = ConfigDict(frozen=True, validate_by_name=True)

    id: str = Field(alias="_id")
    chat_id: int
    telegram_message_id: int
    sender_id: int
    sender_name: str | None = None
    text: str
    sent_at: AwareDatetime
    scored_at: AwareDatetime
    model_revision: str
    prediction: PredictionResult

    @classmethod
    def from_message(
        cls,
        message: IncomingMessage,
        *,
        prediction: PredictionResult,
        scored_at: AwareDatetime,
        model_revision: str,
    ) -> "TelegramMessageRecord":
        """Build the stored record from an incoming message and its prediction."""
        return cls(
            id=message.message_id,
            chat_id=message.chat_id,
            telegram_message_id=message.telegram_message_id,
            sender_id=message.sender_id,
            sender_name=message.sender_name,
            text=message.text,
            sent_at=message.sent_at,
            scored_at=scored_at,
            model_revision=model_revision,
            prediction=prediction,
        )
