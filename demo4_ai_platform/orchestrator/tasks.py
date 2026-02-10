"""Unified task management: ingestion / training / inference."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from threading import Lock

import httpx


class TaskType(str, Enum):
    INGESTION = "ingestion"
    TRAINING = "training"
    INFERENCE = "inference"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager:
    def __init__(self, executor_url: str):
        self.executor_url = executor_url.rstrip("/")
        self._tasks: dict[str, dict] = {}
        self._lock = Lock()

    def create(self, task_type: TaskType, payload: dict) -> dict:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        task = {
            "id": task_id,
            "type": task_type,
            "name": payload.get("name", ""),
            "status": TaskStatus.RUNNING,
            "created_at": now,
            "completed_at": None,
            "result": None,
            "error": None,
            **{k: v for k, v in payload.items() if k not in ("type", "name")},
        }

        with self._lock:
            self._tasks[task_id] = task

        if task_type in (TaskType.INGESTION, TaskType.TRAINING):
            self._submit_batch(task_id, payload)
        elif task_type == TaskType.INFERENCE:
            self._start_inference(task_id, payload)

        with self._lock:
            return self._public_view(self._tasks[task_id])

    def get(self, task_id: str) -> dict | None:
        with self._lock:
            task = self._tasks.get(task_id)
        if task is None:
            return None

        # For batch tasks, poll Executor for latest status
        if task["type"] in (TaskType.INGESTION, TaskType.TRAINING) and task["status"] == TaskStatus.RUNNING:
            executor_task_id = task.get("_executor_task_id")
            if executor_task_id:
                self._sync_batch_status(task_id, executor_task_id)

        with self._lock:
            return self._public_view(self._tasks[task_id])

    def list_all(self, task_type: TaskType | None = None) -> list[dict]:
        with self._lock:
            tasks = list(self._tasks.values())
        if task_type:
            tasks = [t for t in tasks if t["type"] == task_type]
        return [self._public_view(t) for t in tasks]

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None or task["status"] != TaskStatus.RUNNING:
                return False

        # Cancel on Executor if batch task
        executor_task_id = task.get("_executor_task_id")
        if executor_task_id:
            try:
                httpx.post(f"{self.executor_url}/api/v1/tasks/{executor_task_id}/cancel")
            except httpx.HTTPError:
                pass

        with self._lock:
            task["status"] = TaskStatus.FAILED
            task["error"] = "cancelled"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
        return True

    def _submit_batch(self, task_id: str, payload: dict):
        """Submit ingestion/training task to Executor."""
        try:
            resp = httpx.post(
                f"{self.executor_url}/api/v1/tasks",
                json={
                    "script": payload["script"],
                    "input": payload["input"],
                    "output": payload["output"],
                    "params": payload.get("params", {}),
                },
            )
            resp.raise_for_status()
            executor_task_id = resp.json()["id"]
            with self._lock:
                self._tasks[task_id]["_executor_task_id"] = executor_task_id
        except Exception as e:
            with self._lock:
                self._tasks[task_id]["status"] = TaskStatus.FAILED
                self._tasks[task_id]["error"] = str(e)
                self._tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

    def _sync_batch_status(self, task_id: str, executor_task_id: str):
        """Poll Executor for batch task status."""
        try:
            resp = httpx.get(f"{self.executor_url}/api/v1/tasks/{executor_task_id}")
            resp.raise_for_status()
            data = resp.json()
            with self._lock:
                task = self._tasks[task_id]
                if data["status"] == "completed":
                    task["status"] = TaskStatus.COMPLETED
                    task["result"] = data.get("result")
                    task["completed_at"] = data.get("completed_at")
                elif data["status"] == "failed":
                    task["status"] = TaskStatus.FAILED
                    task["error"] = data.get("error")
                    task["completed_at"] = data.get("completed_at")
        except httpx.HTTPError:
            pass

    def _start_inference(self, task_id: str, payload: dict):
        """Start inference service (placeholder — model loading happens here)."""
        # For Level 1, inference runs in-process.
        # Full implementation will load model from Lance and start a predict endpoint.
        port = payload.get("port", 8080)
        with self._lock:
            self._tasks[task_id]["endpoint"] = f"http://localhost:{port}"

    def _public_view(self, task: dict) -> dict:
        """Return task dict without internal fields."""
        return {k: v for k, v in task.items() if not k.startswith("_") and v is not None}
