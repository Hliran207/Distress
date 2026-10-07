from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _EnvSettings(BaseSettings):
    """Shared behavior: read from environment variables and .env, ignore unrelated keys."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)


class CascadeSettings(_EnvSettings):
    """Configuration needed to build a Cascade."""

    hf_repo_id: str = "Hliran2/distilbert-distress-detector"
    hf_revision: str

    fast_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    bert_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    uncertainty_enabled: bool = True
    uncertainty_low: float = Field(default=0.25, ge=0.0, le=1.0)
    uncertainty_high: float = Field(default=0.75, ge=0.0, le=1.0)

    negation_enabled: bool = True

    audit_rate: float = Field(default=0.0, ge=0.0, le=1.0)


class MongoSettings(_EnvSettings):
    """Where scored messages are stored."""

    mongo_uri: str
    mongo_db: str = "reddit_distress_db"
    mongo_collection: str = "telegram_posts"
