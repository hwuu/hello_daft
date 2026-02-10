"""Lance storage operations: list, get, delete datasets and models."""

from pathlib import Path

import daft
import lancedb


class Storage:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.datasets_path = self.storage_path / "datasets"
        self.models_path = self.storage_path / "models"
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)

    def _list_tables(self, directory: Path) -> list[dict]:
        results = []
        for p in sorted(directory.glob("*.lance")):
            try:
                df = daft.read_lance(str(p))
                schema = {f.name: str(f.dtype) for f in df.schema()}
                num_rows = df.count_rows()
                results.append({
                    "id": p.stem,
                    "path": str(p),
                    "schema": schema,
                    "num_rows": num_rows,
                })
            except Exception:
                results.append({"id": p.stem, "path": str(p), "error": "unreadable"})
        return results

    def _get_table(self, directory: Path, table_id: str) -> dict | None:
        p = directory / f"{table_id}.lance"
        if not p.exists():
            return None
        df = daft.read_lance(str(p))
        schema = {f.name: str(f.dtype) for f in df.schema()}
        num_rows = df.count_rows()
        return {
            "id": table_id,
            "path": str(p),
            "schema": schema,
            "num_rows": num_rows,
        }

    def _delete_table(self, directory: Path, table_id: str) -> bool:
        p = directory / f"{table_id}.lance"
        if not p.exists():
            return False
        import shutil
        shutil.rmtree(p)
        return True

    # --- Datasets ---

    def list_datasets(self) -> list[dict]:
        return self._list_tables(self.datasets_path)

    def get_dataset(self, dataset_id: str) -> dict | None:
        return self._get_table(self.datasets_path, dataset_id)

    def delete_dataset(self, dataset_id: str) -> bool:
        return self._delete_table(self.datasets_path, dataset_id)

    # --- Models ---

    def list_models(self) -> list[dict]:
        return self._list_tables(self.models_path)

    def get_model(self, model_id: str) -> dict | None:
        return self._get_table(self.models_path, model_id)

    def delete_model(self, model_id: str) -> bool:
        return self._delete_table(self.models_path, model_id)
