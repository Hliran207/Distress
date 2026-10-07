from abc import ABC, abstractmethod


class DistressModel(ABC):
    """A model that scores texts for distress.

    Callers always pass raw text; each model prepares its own input.
    Returns probabilities only: thresholds belong to the cascade.
    """

    @abstractmethod
    def predict_proba(self, texts: list[str]) -> list[float]:
        """Return p(distress) for each text, in the same order."""

    def predict_one(self, text: str) -> float:
        """Score a single text."""
        return self.predict_proba([text])[0]
