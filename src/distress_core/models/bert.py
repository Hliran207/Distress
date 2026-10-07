import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from distress_core.models.base import DistressModel

MAX_LENGTH = 256
DISTRESS_LABEL = "distress"


class BertModel(DistressModel):
    """Fine-tuned DistilBERT.

    Trained on raw text, so it does not call preprocess().
    """

    def __init__(self, tokenizer, model) -> None:
        self._tokenizer = tokenizer
        self._model = model
        self._model.eval()
        self._distress_index = model.config.label2id[DISTRESS_LABEL]

    @classmethod
    def from_hub(cls, repo_id: str, revision: str) -> "BertModel":
        tokenizer = AutoTokenizer.from_pretrained(repo_id, revision=revision)
        model = AutoModelForSequenceClassification.from_pretrained(
            repo_id, revision=revision
        )
        return cls(tokenizer, model)

    def predict_proba(self, texts: list[str]) -> list[float]:
        inputs = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )
        with torch.inference_mode():
            logits = self._model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)
        return probabilities[:, self._distress_index].tolist()
