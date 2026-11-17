import tempfile
import uuid
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from apps.api.app.workers.celery_app import celery_app
from apps.api.app.engines import get_engine
from apps.api.app.storage import get_storage_driver

def _compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def execute_job_synchronously(
    job_id: str,
    operation: str,
    input_file_paths: List[str],
    options: Dict[str, Any],
    progress_callback=None
) -> Dict[str, Any]:
    """
    Core executor used both inside Celery tasks and direct synchronous fallback.
    """
    storage = get_storage_driver()
    engine = get_engine(operation)

    with tempfile.TemporaryDirectory() as temp_dir_str:
        work_dir = Path(temp_dir_str)
        local_inputs: List[Path] = []

        # Download or resolve input files into ephemeral scratch directory
        for idx, key_or_path in enumerate(input_file_paths):
            p = Path(key_or_path)
            if p.exists():
                local_inputs.append(p)
            else:
                stored_path = storage.get_file_path(key_or_path)
                local_inputs.append(stored_path)

        # Run engine
        result = engine.execute(
            input_paths=local_inputs,
            output_dir=work_dir,
            options=options,
            progress_callback=progress_callback
        )

        # Save generated output files to storage
        output_files_info = []
        for out_path in result.output_paths:
            out_checksum = _compute_sha256(out_path)
            storage_key = f"processed/{job_id}/{out_path.name}"
            storage.put_file(out_path, storage_key)

            output_files_info.append({
                "original_name": out_path.name,
                "storage_key": storage_key,
                "size_bytes": out_path.stat().st_size,
                "checksum_sha256": out_checksum,
                "download_url": storage.generate_download_url(storage_key)
            })

        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "progress": 100,
            "stage_message": "Operation completed successfully.",
            "metrics": result.metrics,
            "output_files": output_files_info,
        }

@celery_app.task(bind=True, name="tasks.process_document_job")
def process_document_job(self, job_id: str, operation: str, input_file_paths: list, options: dict):
    def update_celery_progress(prog: int, msg: str):
        self.update_state(
            state="PROCESSING",
            meta={"progress": prog, "stage_message": msg}
        )

    return execute_job_synchronously(
        job_id=job_id,
        operation=operation,
        input_file_paths=input_file_paths,
        options=options,
        progress_callback=update_celery_progress
    )
