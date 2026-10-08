import logging

from distress_core.factory import build_cascade
from distress_core.messaging.base import create_consumer, create_producer
from distress_core.settings import CascadeSettings, KafkaSettings, MongoSettings
from distress_core.storage.repository import MessageRepository

from .consumer import InferenceConsumer

GROUP_ID = "inference"


def main() -> None:
    cascade_settings = CascadeSettings()
    kafka = KafkaSettings()

    consumer = InferenceConsumer(
        create_consumer(kafka, GROUP_ID),
        create_producer(kafka),
        kafka.kafka_topic,
        kafka.kafka_dlq_topic,
        cascade=build_cascade(cascade_settings),
        repository=MessageRepository.connect(MongoSettings()),
        model_revision=cascade_settings.hf_revision,
    )
    consumer.run()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
