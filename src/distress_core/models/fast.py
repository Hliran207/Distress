import joblib
from huggingface_hub import hf_hub_download

from distress_core.models.base import DistressModel
from distress_core.preprocessing.preprocess import preprocess

FILENAME = "tfidf_logreg.pkl"
DISTRESS_LABEL = 1


class FastModel(DistressModel):
    """TF-IDF + logistic regression.

    Runs preprocess() on the raw text, exactly as in training.
    """

    def __init__(self, pipeline) -> None:
        self._pipeline = pipeline
        self._distress_index = list(pipeline.classes_).index(DISTRESS_LABEL)

    @classmethod
    def from_hub(cls, repo_id: str, revision: str) -> "FastModel":
        path = hf_hub_download(repo_id=repo_id, filename=FILENAME, revision=revision)
        return cls(joblib.load(path))

    def predict_proba(self, texts: list[str]) -> list[float]:
        cleaned = [preprocess(text) for text in texts]
        probabilities = self._pipeline.predict_proba(cleaned)
        return probabilities[:, self._distress_index].tolist()
