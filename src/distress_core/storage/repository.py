from pydantic import BaseModel, ConfigDict
from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from distress_core.contracts.prediction import DecidedBy
from distress_core.contracts.records import TelegramMessageRecord
from distress_core.settings import MongoSettings


class Stats(BaseModel):
    """Counts over all stored messages."""

    model_config = ConfigDict(frozen=True)

    total: int
    distress: int
    escalated: int


class MessageRepository:
    """Stores scored Telegram messages in MongoDB. The only code that talks to the database."""

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    @classmethod
    def connect(cls, settings: MongoSettings) -> "MessageRepository":
        client = MongoClient(settings.mongo_uri, tz_aware=True)
        return cls(client[settings.mongo_db][settings.mongo_collection])

    def insert(self, record: TelegramMessageRecord) -> bool:
        """Store a record. Return False if a record with the same id already exists."""
        try:
            self._collection.insert_one(record.model_dump(by_alias=True))
        except DuplicateKeyError:
            return False
        return True

    def get(self, message_id: str) -> TelegramMessageRecord | None:
        doc = self._collection.find_one({"_id": message_id})
        return None if doc is None else TelegramMessageRecord.model_validate(doc)

    def list_messages(
        self, *, limit: int, offset: int, is_distress: bool | None = None
    ) -> list[TelegramMessageRecord]:
        """Newest first. Optionally only distress / only non-distress."""
        query = {} if is_distress is None else {"prediction.is_distress": is_distress}
        cursor = (
            self._collection.find(query)
            .sort([("sent_at", DESCENDING), ("_id", DESCENDING)])
            .skip(offset)
            .limit(limit)
        )
        return [TelegramMessageRecord.model_validate(doc) for doc in cursor]

    def stats(self) -> Stats:
        return Stats(
            total=self._collection.count_documents({}),
            distress=self._collection.count_documents({"prediction.is_distress": True}),
            escalated=self._collection.count_documents(
                {"prediction.decided_by": DecidedBy.DISTILBERT.value}
            ),
        )

    def ping(self) -> bool:
        """True if MongoDB answers. Used by /health."""
        self._collection.database.client.admin.command("ping")
        return True
