from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


def build_message_id(chat_id: int, telegram_message_id: int) -> str:
    """The stable id of a Telegram message. we create it to avoid collisions in Kafka."""
    return f"tg:{chat_id}:{telegram_message_id}"


class IncomingMessage(BaseModel):
    """A Telegram text message, as published by the bot to Kafka."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = 1
    message_id: str = Field(pattern=r"^tg:-?\d+:\d+$")
    chat_id: int
    telegram_message_id: int
    sender_id: int
    sender_name: str | None = None
    text: str = Field(min_length=1)
    sent_at: AwareDatetime
