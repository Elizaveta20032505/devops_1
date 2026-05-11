"""FastAPI: здоровье сервиса и предсказание модели."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, create_model

from src.inference import load_artifacts, predict_from_features, read_feature_names_for_openapi


def _predict_body_model() -> type[BaseModel]:
    names = read_feature_names_for_openapi()
    example = {n: 0.0 for n in names}
    return create_model(
        "PredictBody",
        __config__=ConfigDict(json_schema_extra={"example": example}, extra="forbid"),
        **{n: (float, Field(default=0.0, title=n.replace("_", " ")[:40])) for n in names},
    )


PredictBody = _predict_body_model()


@asynccontextmanager
async def _lifespan(app: FastAPI):
    try:
        app.state.model, app.state.feature_names = load_artifacts()
    except FileNotFoundError:
        app.state.model = None
        app.state.feature_names = []
    yield


app = FastAPI(title="breast-cancer-logreg", version="0.1", lifespan=_lifespan)


@app.get("/health")
def health() -> dict:
    ok = getattr(app.state, "model", None) is not None
    return {"status": "ok" if ok else "no_model"}


@app.post("/predict")
def predict(body: PredictBody) -> dict:
    if app.state.model is None:
        raise HTTPException(
            status_code=503,
            detail="Модель не найдена.",
        )
    try:
        payload = body.model_dump()
        return predict_from_features(payload, app.state.model, app.state.feature_names)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
