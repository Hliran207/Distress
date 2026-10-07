FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install huggingface_hub

ARG HF_REPO_ID=Hliran2/distilbert-distress-detector
ARG HF_REVISION
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('${HF_REPO_ID}', revision='${HF_REVISION}')"

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install ".[ml,mongo,api]"

RUN python -c "import nltk; [nltk.download(r) for r in ('stopwords', 'wordnet', 'omw-1.4', 'punkt_tab', 'averaged_perceptron_tagger_eng')]"

COPY services/api/ ./services/api/

ENV HF_HUB_OFFLINE=1
EXPOSE 8000
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]