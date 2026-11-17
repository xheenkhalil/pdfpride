import uuid
import hashlib
from pathlib import Path
from fastapi import APIRouter, UploadFile, File as FastAPIFile, HTTPException, Depends
from fastapi.responses import FileResponse as FastAPIFileResponse
from apps.api.app.schemas.file import FileResponse
from apps.api.app.storage import get_storage_driver

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload/direct", response_model=FileResponse)
async def upload_file_direct(file: UploadFile = FastAPIFile(...)):
    """
    Direct file upload endpoint with SHA-256 calculation and storage persistence.
    """
    file_id = str(uuid.uuid4())
    original_name = file.filename or "uploaded_document"
    extension = Path(original_name).suffix.lower()

    content = await file.read()
    size_bytes = len(content)

    if size_bytes == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Compute SHA-256 checksum
    hasher = hashlib.sha256()
    hasher.update(content)
    checksum = hasher.hexdigest()

    storage = get_storage_driver()
    storage_key = f"uploads/{file_id}/{original_name}"
    storage.put_file(content, storage_key, content_type=file.content_type or "application/octet-stream")

    return FileResponse(
        id=file_id,
        original_name=original_name,
        storage_key=storage_key,
        mime_type=file.content_type or "application/octet-stream",
        extension=extension,
        size_bytes=size_bytes,
        checksum_sha256=checksum,
        status="active",
        download_url=storage.generate_download_url(storage_key)
    )

@router.get("/download/{storage_key:path}")
async def download_file(storage_key: str):
    """
    Stream a stored file directly to the client.
    """
    storage = get_storage_driver()
    try:
        file_path = storage.get_file_path(storage_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Requested file was not found on server.")

    return FastAPIFileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream"
    )
