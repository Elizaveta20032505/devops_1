"""Обучение модели (пункт 3): самый простой классификатор, сохранение в experiments/."""
from __future__ import annotations

import configparser
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    cfg = configparser.ConfigParser()
    cfg.read(_root() / "config.ini", encoding="utf-8")
    d = _root() / cfg["PATHS"]["processed_dir"]

    X_train = pd.read_csv(d / "Train_X.csv")
    y_train = pd.read_csv(d / "Train_y.csv")["target"]

    model = LogisticRegression(max_iter=5000).fit(X_train, y_train)

    path = _root() / cfg["PATHS"]["model_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    print("Готово:", path)


if __name__ == "__main__":
    main()
