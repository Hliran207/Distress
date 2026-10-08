import logging
from datetime import datetime, timezone

from confluent_kafka import Consumer, Producer

from distress_core.cascade import Cascade
from distress_core.contracts.messages import IncomingMessage
from distress_core.contracts.records import TelegramMessageRecord
from distress_core.messaging.base import BaseKafkaConsumer
from distress_core.storage.repository import MessageRepository

log = logging.getLogger(__name__)


class InferenceConsumer(BaseKafkaConsumer):
    """Scores each incoming Telegram message with the cascade and stores the result."""

    def __init__(
        self,
        consumer: Consumer,
        dlq_producer: Producer,
        topic: str,
        dlq_topic: str,
        *,
        cascade: Cascade,
        repository: MessageRepository,
        model_revision: str,
    ) -> None:
        super().__init__(consumer, dlq_producer, topic, dlq_topic)
        self._cascade = cascade
        self._repository = repository
        self._model_revision = model_revision

    def handle(self, value: bytes) -> None:
        message = IncomingMessage.model_validate_json(value)
        prediction = self._cascade.predict(message.message_id, message.text)
        record = TelegramMessageRecord.from_message(
            message,
            prediction=prediction,
            scored_at=datetime.now(timezone.utc),
            model_revision=self._model_revision,
        )
        if self._repository.insert(record):
            log.info(
                "Stored %s: distress=%s, decided_by=%s, reasons=%s",
                message.message_id,
                prediction.is_distress,
                prediction.decided_by.value,
                prediction.escalation_reasons,
            )
        else:
            log.info("Duplicate %s, already stored", message.message_id)
