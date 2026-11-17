from apps.api.app.storage.base import StorageDriver
from apps.api.app.storage.local import LocalStorageDriver
from apps.api.app.core.config import settings

_driver_instance: StorageDriver | None = None

def get_storage_driver() -> StorageDriver:
    global _driver_instance
    if _driver_instance is None:
        if settings.STORAGE_DRIVER == "local":
            _driver_instance = LocalStorageDriver()
        else:
            # Fallback to local driver if S3 is not configured
            _driver_instance = LocalStorageDriver()
    return _driver_instance

__all__ = ["StorageDriver", "LocalStorageDriver", "get_storage_driver"]
