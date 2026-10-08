from datetime import datetime, timezone

from distress_core.contracts.messages import IncomingMessage, build_message_id


def to_incoming_message(update: dict) -> IncomingMessage | None:
    """Convert a Telegram update to an IncomingMessage, or None if there is nothing to score.

    Skipped: updates without a message, messages without a sender, non-text messages
    (photos, stickers) and commands such as /start.
    """
    message = update.get("message")
    if message is None:
        return None

    sender = message.get("from")
    text = message.get("text")
    if sender is None or not text or text.startswith("/"):
        return None

    chat_id = message["chat"]["id"]
    return IncomingMessage(
        message_id=build_message_id(chat_id, message["message_id"]),
        chat_id=chat_id,
        telegram_message_id=message["message_id"],
        sender_id=sender["id"],
        sender_name=_display_name(sender),
        text=text,
        sent_at=datetime.fromtimestamp(message["date"], tz=timezone.utc),
    )


def _display_name(sender: dict) -> str | None:
    """First name, plus last name when present. Telegram does not always provide both."""
    name = " ".join(
        part for part in (sender.get("first_name"), sender.get("last_name")) if part
    )
    return name or None
