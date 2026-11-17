import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class FileResponse(BaseModel):
    id: str
    original_name: str
    storage_key: str
    mime_type: str
    extension: str
    size_bytes: int
    checksum_sha256: str
    page_count: Optional[int] = None
    status: str
    created_at: Optional[datetime] = None
    download_url: Optional[str] = None

    class Config:
        from_attributes = True
