"""Загрузка модели и предсказание."""
from __future__ import annotations

import configparser
import json
import os
from pathlib import Path

import joblib
import pandas as pd


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _model_dir() -> Path:
    override = os.environ.get("DEVOPS_MODEL_DIR")
    if override:
        return Path(override)
    cfg = configparser.ConfigParser()
    cfg.read(_root() / "config.ini", encoding="utf-8")
    return (_root() / cfg["PATHS"]["model_path"]).parent


_WDBC_KAGGLE_FEATURES: tuple[str, ...] = (
    "radius_mean",
    "texture_mean",
    "perimeter_mean",
    "area_mean",
    "smoothness_mean",
    "compactness_mean",
    "concavity_mean",
    "concave points_mean",
    "symmetry_mean",
    "fractal_dimension_mean",
    "radius_se",
    "texture_se",
    "perimeter_se",
    "area_se",
    "smoothness_se",
    "compactness_se",
    "concavity_se",
    "concave points_se",
    "symmetry_se",
    "fractal_dimension_se",
    "radius_worst",
    "texture_worst",
    "perimeter_worst",
    "area_worst",
    "smoothness_worst",
    "compactness_worst",
    "concavity_worst",
    "concave points_worst",
    "symmetry_worst",
    "fractal_dimension_worst",
)


def read_feature_names_for_openapi() -> list[str]:
    """Имена признаков для схемы Swagger (без загрузки весов модели)."""
    names_path = _model_dir() / "feature_names.json"
    if names_path.is_file():
        return json.loads(names_path.read_text(encoding="utf-8"))
    cfg = configparser.ConfigParser()
    cfg.read(_root() / "config.ini", encoding="utf-8")
    train_x = _root() / cfg["PATHS"]["processed_dir"] / "Train_X.csv"
    if train_x.is_file():
        return list(pd.read_csv(train_x, nrows=0).columns)
    return list(_WDBC_KAGGLE_FEATURES)


def load_artifacts() -> tuple[object, list[str]]:
    """Возвращает (модель, список имён признаков в нужном порядке)."""
    mdir = _model_dir()
    model_path = mdir / "model.joblib"
    names_path = mdir / "feature_names.json"
    if not model_path.is_file():
        raise FileNotFoundError(str(model_path))
    model = joblib.load(model_path)
    if names_path.is_file():
        feature_names: list[str] = json.loads(names_path.read_text(encoding="utf-8"))
    else:
        cfg = configparser.ConfigParser()
        cfg.read(_root() / "config.ini", encoding="utf-8")
        train_x = _root() / cfg["PATHS"]["processed_dir"] / "Train_X.csv"
        if not train_x.is_file():
            raise FileNotFoundError("Нет feature_names.json и нет Train_X.csv")
        feature_names = list(pd.read_csv(train_x, nrows=0).columns)
    return model, feature_names


def predict_from_features(features: dict[str, float], model: object, feature_names: list[str]) -> dict:
    missing = [n for n in feature_names if n not in features]
    if missing:
        raise ValueError(f"Не хватает полей ({len(missing)}): {missing[:8]}{'...' if len(missing) > 8 else ''}")
    X = pd.DataFrame([{n: float(features[n]) for n in feature_names}])
    pred = int(model.predict(X)[0])
    proba_m = None
    if hasattr(model, "predict_proba"):
        proba_m = float(model.predict_proba(X)[0, 1])
    return {
        "label": "M" if pred == 1 else "B",
        "malignant_probability": proba_m,
    }
