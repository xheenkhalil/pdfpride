import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class JobCreateRequest(BaseModel):
    operation: str = Field(..., description="Operation identifier (e.g., pdf_merge, pdf_compress)")
    input_file_ids: List[str] = Field(..., description="List of file IDs or storage keys to process")
    options: Dict[str, Any] = Field(default_factory=dict, description="Options dictionary for the operation")

class OutputFileInfo(BaseModel):
    original_name: str
    storage_key: str
    size_bytes: int
    checksum_sha256: str
    download_url: str

class JobResponse(BaseModel):
    id: str
    operation: str
    status: str
    progress: int
    stage_message: str
    options: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    output_files: List[OutputFileInfo] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
