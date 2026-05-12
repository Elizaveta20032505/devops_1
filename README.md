# devops_1

## Назначение

Репозиторий: воспроизводимый пайплайн для датасета Breast Cancer Wisconsin — подготовка данных, обучение логистической регрессии (`scikit-learn`), выдача предсказаний через HTTP API (FastAPI), версионирование данных и стадий (DVC), контейнеризация (Docker), автоматическая сборка и публикация образа (Jenkins CI), выкладка и проверка работающего контейнера (Jenkins CD).

## Данные и обучение

- Конфигурация путей и гиперпараметров: `config.ini`.
- Стадии: `python -m src.prepare_data` → `data/processed/`; `python -m src.train` → `experiments/model.joblib`, `experiments/feature_names.json`.
- DVC: `dvc add data/raw/data.csv`, затем `dvc repro` по `dvc.yaml` / `dvc.lock`. В системе контроля версий: `dvc.yaml`, `dvc.lock`, `*.dvc`, метаданные `.dvc/`; кэш `.dvc/cache`.

## API и контейнер

- Запуск API локально: `uvicorn src.api:app --reload`.
- Зависимости разработки: `requirements.txt`; минимальный набор для образа: `requirements-docker.txt`.
- Сборка образа: `Dockerfile`. Запуск одного сервиса: `docker compose up --build` (см. `docker-compose.yml`: порт 8000, healthcheck на `/health`).

## Проверки 

- **pytest** (`tests/`, `pytest.ini`): проверки кода и API.
- **`scripts/run_scenarios.py` + `scenario.json`**: сценарные HTTP-запросы к уже запущенному инстансу API (ручной или CD-запуск контейнера).

## Метаданные дистрибутива

- `dev_sec_ops.yml` — сводные параметры для отчёта; обновление: `python scripts/update_dev_sec_ops.py`.

## Jenkins: CI

- В репозитории: корневой `Jenkinsfile`.
- Тип job: **Multibranch Pipeline** — сканирование веток и pull request GitHub; для каждой сущности создаётся отдельная линия сборок.
- Условие полного CI: PR в ветку `main` (`CHANGE_TARGET=main`). Стадии: `checkout` → **`pytest`** (venv `.ci-venv`, `pip install -r requirements.txt`) → `docker build` → `docker push`. Иначе выполняется только стадия `info`.
- Учётные данные Docker Hub: credential id `dockerhub-creds`; глобальная переменная `DOCKERHUB_USER` должна совпадать с владельцем репозитория образа на Hub.

## Jenkins: CD

- Файл: `CD/Jenkinsfile`. Job типа Pipeline, **Pipeline script from SCM**, поле **Script Path:** `CD/Jenkinsfile`, имя job по умолчанию: `devops1-model-cd` (должно совпадать с вызовом `build job` из корневого `Jenkinsfile` при успешном CI).
- Последовательность: `checkout scm` → `docker pull` (параметр `IMAGE_TAG`) → `docker run` (порт хоста 18080) → `python scripts/run_scenarios.py` с базой из переменной `SCENARIO_BASE_URL` → удаление контейнера в `post`.

