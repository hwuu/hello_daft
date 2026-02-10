"""Script executor: load user scripts, call run(), manage task lifecycle."""

import importlib.util
import threading
import uuid
from datetime import datetime, timezone
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRunner:
    def __init__(self):
        self._tasks: dict[str, dict] = {}
        self._lock = threading.Lock()

    def submit(self, script: str, input_path: str, output_path: str, params: dict) -> dict:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        task = {
            "id": task_id,
            "script": script,
            "input": input_path,
            "output": output_path,
            "params": params,
            "status": TaskStatus.RUNNING,
            "created_at": now,
            "completed_at": None,
            "result": None,
            "error": None,
        }
        with self._lock:
            self._tasks[task_id] = task

        thread = threading.Thread(target=self._execute, args=(task_id,), daemon=True)
        thread.start()
        return {"id": task_id, "status": task["status"], "created_at": now}

    def get(self, task_id: str) -> dict | None:
        with self._lock:
            task = self._tasks.get(task_id)
        if task is None:
            return None
        return {k: v for k, v in task.items() if k != "script"}

    def list_all(self) -> list[dict]:
        with self._lock:
            tasks = list(self._tasks.values())
        return [
            {"id": t["id"], "status": t["status"], "created_at": t["created_at"]}
            for t in tasks
        ]

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            if task["status"] == TaskStatus.RUNNING:
                task["status"] = TaskStatus.FAILED
                task["error"] = "cancelled"
                task["completed_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def _execute(self, task_id: str):
        with self._lock:
            task = self._tasks[task_id]
            script = task["script"]
            input_path = task["input"]
            output_path = task["output"]
            params = task["params"]

        try:
            run_fn = _load_run_function(script)
            result = run_fn(input_path, output_path, params)
            with self._lock:
                if task["status"] == TaskStatus.RUNNING:
                    task["status"] = TaskStatus.COMPLETED
                    task["result"] = result
                    task["completed_at"] = datetime.now(timezone.utc).isoformat()
        except Exception as e:
            with self._lock:
                if task["status"] == TaskStatus.RUNNING:
                    task["status"] = TaskStatus.FAILED
                    task["error"] = str(e)
                    task["completed_at"] = datetime.now(timezone.utc).isoformat()


def _load_run_function(script_path: str):
    spec = importlib.util.spec_from_file_location("user_script", script_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Script not found: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "run"):
        raise AttributeError(f"Script {script_path} must define a run() function")
    return module.run
