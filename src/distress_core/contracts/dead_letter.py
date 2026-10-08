from pydantic import AwareDatetime, BaseModel, ConfigDict


class DeadLetter(BaseModel):
    """A message the inference service could not handle, as published to the DLQ topic."""

    model_config = ConfigDict(frozen=True)

    original_value: str
    error_type: str
    error_message: str
    source_topic: str
    source_partition: int
    source_offset: int
    source_key: str | None
    failed_at: AwareDatetime
