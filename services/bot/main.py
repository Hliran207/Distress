import logging
import signal
import time

from pydantic import ValidationError

from distress_core.messaging.base import create_producer, send_confirmed
from distress_core.settings import KafkaSettings, TelegramSettings

from .convert import to_incoming_message
from .telegram import TelegramClient, TelegramError

log = logging.getLogger("bot")

RETRY_DELAY_SECONDS = 5


def run() -> None:
    kafka = KafkaSettings()
    telegram = TelegramClient(TelegramSettings())
    producer = create_producer(kafka)

    running = True

    def stop(signum, frame):
        nonlocal running
        log.info("Shutdown requested, finishing the current batch")
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    offset = None
    log.info("Bot started, producing to %s", kafka.kafka_topic)

    while running:
        try:
            updates = telegram.get_updates(offset)
        except TelegramError as exc:
            log.warning(
                "getUpdates failed: %s. Retrying in %ss", exc, RETRY_DELAY_SECONDS
            )
            time.sleep(RETRY_DELAY_SECONDS)
            continue
        if not updates:
            continue

        records = []
        for update in updates:
            try:
                message = to_incoming_message(update)
            except (KeyError, ValidationError) as exc:
                log.error(
                    "Skipping malformed update %s: %s", update.get("update_id"), exc
                )
                continue
            if message is not None:
                records.append((str(message.chat_id), message.model_dump_json()))

        if not send_confirmed(producer, kafka.kafka_topic, records, timeout=30):
            log.error("Not acknowledging; Telegram will resend")
            time.sleep(RETRY_DELAY_SECONDS)
            continue

        offset = updates[-1]["update_id"] + 1
        log.info(
            "Forwarded %d update(s); acknowledged up to %d", len(updates), offset - 1
        )

    log.info("Bot stopped")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    run()
