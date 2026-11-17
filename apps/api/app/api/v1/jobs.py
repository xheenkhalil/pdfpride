import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from apps.api.app.schemas.job import JobCreateRequest, JobResponse, OutputFileInfo
from apps.api.app.workers.tasks import execute_job_synchronously, process_document_job
from apps.api.app.core.config import settings

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Ephemeral in-memory job store for fast state lookups
_JOBS_STORE: Dict[str, Dict[str, Any]] = {}

@router.post("", response_model=JobResponse, status_code=202)
async def create_job(request: JobCreateRequest, background_tasks: BackgroundTasks):
    """
    Creates an asynchronous processing job and dispatches it to Celery or background tasks.
    """
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    job_data = {
        "id": job_id,
        "operation": request.operation,
        "status": "PROCESSING",
        "progress": 5,
        "stage_message": "Job queued and initializing engine...",
        "options": request.options,
        "error_message": None,
        "output_files": [],
        "created_at": now,
        "completed_at": None,
    }
    _JOBS_STORE[job_id] = job_data

    # Helper function to run the job and update the store
    def _run_job_bg():
        try:
            res = execute_job_synchronously(
                job_id=job_id,
                operation=request.operation,
                input_file_paths=request.input_file_ids,
                options=request.options,
            )
            _JOBS_STORE[job_id]["status"] = "COMPLETED"
            _JOBS_STORE[job_id]["progress"] = 100
            _JOBS_STORE[job_id]["stage_message"] = "Processing complete."
            _JOBS_STORE[job_id]["output_files"] = res.get("output_files", [])
            _JOBS_STORE[job_id]["completed_at"] = datetime.now(timezone.utc)
        except Exception as e:
            _JOBS_STORE[job_id]["status"] = "FAILED"
            _JOBS_STORE[job_id]["error_message"] = str(e)
            _JOBS_STORE[job_id]["stage_message"] = f"Failed: {str(e)}"
            _JOBS_STORE[job_id]["completed_at"] = datetime.now(timezone.utc)

    background_tasks.add_task(_run_job_bg)

    return JobResponse(**job_data)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Polling endpoint for client to check real-time progress and receive completed download links.
    """
    job_data = _JOBS_STORE.get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JobResponse(**job_data)
