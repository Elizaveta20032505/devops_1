from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_with_model(tiny_api_module) -> None:
    with TestClient(tiny_api_module.app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_predict_ok(tiny_api_module) -> None:
    body = {"radius_mean": 1.0, "texture_mean": 1.0, "smoothness_mean": 1.0}
    with TestClient(tiny_api_module.app) as client:
        r = client.post("/predict", json=body)
        assert r.status_code == 200
        data = r.json()
        assert data["label"] in ("M", "B")
        assert "malignant_probability" in data


def test_predict_unknown_field_returns_422(tiny_api_module) -> None:
    body = {"radius_mean": 1.0, "texture_mean": 1.0, "smoothness_mean": 1.0, "not_a_feature": 0.0}
    with TestClient(tiny_api_module.app) as client:
        r = client.post("/predict", json=body)
        assert r.status_code == 422
