"""Подготовка данных: читает CSV с Kaggle, делит на train/test, пишет в data/processed/."""
from __future__ import annotations

import configparser
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    cfg = configparser.ConfigParser()
    cfg.read(_root() / "config.ini", encoding="utf-8")
    raw = _root() / cfg["PATHS"]["raw_csv"]
    out_dir = _root() / cfg["PATHS"]["processed_dir"]

    if not raw.is_file():
        raise SystemExit(
            f"Нет файла: {raw}\n"
        )

    df = pd.read_csv(raw)
    df = df.drop(columns=[c for c in df.columns if str(c).startswith("Unnamed")], errors="ignore")
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    y = (df["diagnosis"] == "M").astype(int)
    X = df.drop(columns=["diagnosis"])

    rs = int(cfg["SPLIT"]["random_state"])
    ts = float(cfg["SPLIT"]["test_size"])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=ts, random_state=rs, stratify=y
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    X_train.to_csv(out_dir / "Train_X.csv", index=False)
    X_test.to_csv(out_dir / "Test_X.csv", index=False)
    y_train.to_csv(out_dir / "Train_y.csv", index=False, header=["target"])
    y_test.to_csv(out_dir / "Test_y.csv", index=False, header=["target"])
    print("Готово:", out_dir)


if __name__ == "__main__":
    main()
