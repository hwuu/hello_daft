"""Executor HTTP API: storage + task routes."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .runner import TaskRunner
from .storage import Storage

_storage: Storage | None = None
_runner: TaskRunner | None = None


def create_app(storage_path: str = "./lance_storage") -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        global _storage, _runner
        _storage = Storage(storage_path)
        _runner = TaskRunner()
        yield

    app = FastAPI(title="Executor", lifespan=lifespan)

    # --- Datasets ---

    @app.get("/api/v1/datasets")
    def list_datasets():
        return _storage.list_datasets()

    @app.get("/api/v1/datasets/{dataset_id}")
    def get_dataset(dataset_id: str):
        result = _storage.get_dataset(dataset_id)
        if result is None:
            raise HTTPException(404, {"code": "DATASET_NOT_FOUND", "message": f"Dataset '{dataset_id}' not found"})
        return result

    @app.delete("/api/v1/datasets/{dataset_id}")
    def delete_dataset(dataset_id: str):
        if not _storage.delete_dataset(dataset_id):
            raise HTTPException(404, {"code": "DATASET_NOT_FOUND", "message": f"Dataset '{dataset_id}' not found"})
        return {"status": "deleted"}

    # --- Models ---

    @app.get("/api/v1/models")
    def list_models():
        return _storage.list_models()

    @app.get("/api/v1/models/{model_id}")
    def get_model(model_id: str):
        result = _storage.get_model(model_id)
        if result is None:
            raise HTTPException(404, {"code": "MODEL_NOT_FOUND", "message": f"Model '{model_id}' not found"})
        return result

    @app.delete("/api/v1/models/{model_id}")
    def delete_model(model_id: str):
        if not _storage.delete_model(model_id):
            raise HTTPException(404, {"code": "MODEL_NOT_FOUND", "message": f"Model '{model_id}' not found"})
        return {"status": "deleted"}

    # --- Tasks ---

    class TaskRequest(BaseModel):
        script: str
        input: str
        output: str
        params: dict = {}

    @app.post("/api/v1/tasks", status_code=201)
    def submit_task(req: TaskRequest):
        return _runner.submit(req.script, req.input, req.output, req.params)

    @app.get("/api/v1/tasks")
    def list_tasks():
        return _runner.list_all()

    @app.get("/api/v1/tasks/{task_id}")
    def get_task(task_id: str):
        result = _runner.get(task_id)
        if result is None:
            raise HTTPException(404, {"code": "TASK_NOT_FOUND", "message": f"Task '{task_id}' not found"})
        return result

    @app.post("/api/v1/tasks/{task_id}/cancel")
    def cancel_task(task_id: str):
        if not _runner.cancel(task_id):
            raise HTTPException(404, {"code": "TASK_NOT_FOUND", "message": f"Task '{task_id}' not found or not running"})
        return {"status": "cancelled"}

    return app


app = create_app()
