import hashlib
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse

from distress_core.cascade import Cascade
from distress_core.contracts.prediction import PredictionResult
from distress_core.factory import build_cascade
from distress_core.settings import CascadeSettings, MongoSettings
from distress_core.storage.repository import MessageRepository, Stats

from .schemas import MessageOut, PredictRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cascade = build_cascade(CascadeSettings())
    app.state.repo = MessageRepository.connect(MongoSettings())
    yield


app = FastAPI(title="Distress Detector", lifespan=lifespan)


def get_cascade(request: Request) -> Cascade:
    return request.app.state.cascade


def get_repo(request: Request) -> MessageRepository:
    return request.app.state.repo


def api_message_id(text: str) -> str:
    """Same text, same id: keeps /predict deterministic if the audit trigger is enabled."""
    return "api:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@app.post("/predict", response_model=PredictionResult)
def predict(
    body: PredictRequest, cascade: Cascade = Depends(get_cascade)
) -> PredictionResult:
    return cascade.predict(api_message_id(body.text), body.text)


@app.get("/messages", response_model=list[MessageOut])
def list_messages(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    is_distress: bool | None = None,
    repo: MessageRepository = Depends(get_repo),
) -> list[MessageOut]:
    records = repo.list_messages(limit=limit, offset=offset, is_distress=is_distress)
    return [MessageOut.from_record(r) for r in records]


@app.get("/messages/{message_id}", response_model=MessageOut)
def get_message(
    message_id: str, repo: MessageRepository = Depends(get_repo)
) -> MessageOut:
    record = repo.get(message_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageOut.from_record(record)


@app.get("/stats", response_model=Stats)
def stats(repo: MessageRepository = Depends(get_repo)) -> Stats:
    return repo.stats()


@app.get("/health")
def health(repo: MessageRepository = Depends(get_repo)) -> dict[str, str]:
    repo.ping()
    return {"status": "ok"}


INDEX_HTML = Path(__file__).parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(INDEX_HTML)
