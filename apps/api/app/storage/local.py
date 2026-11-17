import shutil
from pathlib import Path
from apps.api.app.storage.base import StorageDriver
from apps.api.app.core.config import settings

class LocalStorageDriver(StorageDriver):
    """Local filesystem driver ideal for container volumes and local development."""

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = Path(base_dir or settings.LOCAL_STORAGE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, storage_key: str) -> Path:
        # Prevent directory traversal attacks
        cleaned_key = storage_key.lstrip("/\\")
        target_path = (self.base_dir / cleaned_key).resolve()
        if not str(target_path).startswith(str(self.base_dir)):
            raise ValueError(f"Path traversal detected: {storage_key}")
        return target_path

    def put_file(self, file_path_or_bytes: Path | bytes, storage_key: str, content_type: str = "application/octet-stream") -> str:
        target_path = self._resolve_path(storage_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(file_path_or_bytes, Path):
            shutil.copyfile(str(file_path_or_bytes), str(target_path))
        elif isinstance(file_path_or_bytes, bytes):
            with open(target_path, "wb") as f:
                f.write(file_path_or_bytes)
        else:
            raise TypeError("Unsupported file object type")

        return storage_key

    def get_file_path(self, storage_key: str) -> Path:
        target_path = self._resolve_path(storage_key)
        if not target_path.exists():
            raise FileNotFoundError(f"Storage key not found: {storage_key}")
        return target_path

    def delete_file(self, storage_key: str) -> bool:
        target_path = self._resolve_path(storage_key)
        if target_path.exists():
            target_path.unlink()
            return True
        return False

    def generate_download_url(self, storage_key: str, expires_in_seconds: int = 3600) -> str:
        # In local development, downloads route through the API endpoint
        return f"{settings.API_V1_STR}/files/download/{storage_key}"
