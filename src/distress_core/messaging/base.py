import logging
import signal
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from confluent_kafka import Consumer, Message, Producer

from distress_core.contracts.dead_letter import DeadLetter
from distress_core.settings import KafkaSettings

log = logging.getLogger(__name__)


def create_consumer(settings: KafkaSettings, group_id: str) -> Consumer:
    """A consumer configured for manual commits. Never enable auto-commit here."""
    return Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap,
            "group.id": group_id,
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
        }
    )


def create_producer(settings: KafkaSettings) -> Producer:
    return Producer(
        {"bootstrap.servers": settings.kafka_bootstrap, "enable.idempotence": True}
    )


def send_confirmed(
    producer: Producer,
    topic: str,
    records: list[tuple[str | bytes | None, str]],
    timeout: float,
) -> bool:
    """Produce records and wait for Kafka to confirm them. True only if every one was confirmed."""
    errors = []
    for key, value in records:
        producer.produce(
            topic,
            key=key,
            value=value,
            on_delivery=lambda err, _: errors.append(err) if err else None,
        )
    not_delivered = producer.flush(timeout=timeout)
    if errors or not_delivered:
        log.error(
            "Kafka did not confirm records to %s: %s",
            topic,
            errors or f"{not_delivered} pending",
        )
        return False
    return True


class DeadLetterError(Exception):
    """The DLQ did not confirm a message. The offset must not be committed."""


class BaseKafkaConsumer(ABC):
    """Reads a topic and passes each message to `handle` (Template Method).

    The base class owns reliability: an offset is committed only after its message was
    handled or sent to the DLQ (at-least-once). Subclasses implement only `handle`.
    """

    def __init__(
        self, consumer: Consumer, dlq_producer: Producer, topic: str, dlq_topic: str
    ) -> None:
        self._consumer = consumer
        self._dlq_producer = dlq_producer
        self._topic = topic
        self._dlq_topic = dlq_topic
        self._running = True

    @abstractmethod
    def handle(self, value: bytes) -> None:
        """Process one message. Raise on failure: the base class sends it to the DLQ."""

    def run(self) -> None:
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)
        self._consumer.subscribe([self._topic])
        log.info("Consuming from %s", self._topic)
        try:
            while self._running:
                msg = self._consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    log.warning("Kafka error: %s", msg.error())
                    continue
                self._process(msg)
                self._consumer.commit(message=msg, asynchronous=False)
        finally:
            self._consumer.close()
            log.info("Consumer closed")

    def _process(self, msg: Message) -> None:
        try:
            self.handle(msg.value())
        except Exception as exc:
            log.exception(
                "Failed %s[%d]@%d, sending to DLQ",
                msg.topic(),
                msg.partition(),
                msg.offset(),
            )
            self._send_to_dlq(msg, exc)

    def _send_to_dlq(self, msg: Message, exc: Exception) -> None:
        key = msg.key()
        letter = DeadLetter(
            original_value=(msg.value() or b"").decode("utf-8", errors="replace"),
            error_type=type(exc).__name__,
            error_message=str(exc),
            source_topic=msg.topic(),
            source_partition=msg.partition(),
            source_offset=msg.offset(),
            source_key=key.decode("utf-8", errors="replace") if key else None,
            failed_at=datetime.now(timezone.utc),
        )
        if not send_confirmed(
            self._dlq_producer,
            self._dlq_topic,
            [(key, letter.model_dump_json())],
            timeout=10,
        ):
            raise DeadLetterError(
                f"DLQ did not confirm {msg.topic()}[{msg.partition()}]@{msg.offset()}"
            )

    def _stop(self, signum, frame) -> None:
        log.info("Shutdown requested, finishing the current message")
        self._running = False
