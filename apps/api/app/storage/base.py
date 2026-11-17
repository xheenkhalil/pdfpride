from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path

class StorageDriver(ABC):
    """Abstract interface for all persistent document storage operations."""

    @abstractmethod
    def put_file(self, file_path_or_bytes: Path | bytes, storage_key: str, content_type: str = "application/octet-stream") -> str:
        """Stores a file in the storage backend under the given storage key."""
        pass

    @abstractmethod
    def get_file_path(self, storage_key: str) -> Path:
        """Returns a local accessible Path to the stored file."""
        pass

    @abstractmethod
    def delete_file(self, storage_key: str) -> bool:
        """Removes a file from the storage backend."""
        pass

    @abstractmethod
    def generate_download_url(self, storage_key: str, expires_in_seconds: int = 3600) -> str:
        """Generates a secure temporary download URL."""
        pass
