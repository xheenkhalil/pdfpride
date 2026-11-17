# Technical Implementation Specification & Architecture Guide
## PDF Pride (Document Studio) — Milestone 01 & System Core

**Specification Version:** 1.0.0  
**Target Environment:** Local Docker Compose / Managed Cloud (Vercel + Render/Railway + Neon + Cloudflare R2)  
**Repository Pattern:** Monorepo (`apps/api`, `apps/web`, `packages/tool-registry`, `packages/shared-types`)  

---

## 1. System Architecture & Client-Server Demarcation

### 1.1 Architectural Philosophy: Strict Client-Server Separation
PDF Pride enforces an explicit architectural separation between the **Client** (the browser application running Next.js / React) and the **Server** (the FastAPI application, Celery workers, and backing datastores).

* **The Client is Untrusted:** The client never runs document manipulation algorithms, never interacts directly with databases or object stores, and never holds persistent credentials or AWS IAM secrets. Its purpose is exclusively human-computer interaction, client-side preview rendering (via PDF.js in an isolated sandbox), and streaming file binary packets to/from pre-signed URLs.
* **The Server is Authoritative:** The server enforces rate limits, validates magic bytes, isolates processing in unprivileged containers with disabled network egress, and ensures that user workspaces remain strictly isolated with Row-Level Security (RLS) patterns.

```
+-----------------------------------------------------------------------------------------+
|                                CLIENT APPLICATION (apps/web)                            |
|                                                                                         |
|   Platform: Next.js 14+ (App Router), React 18, TypeScript, Tailwind CSS, TanStack v5  |
|   Deployment: Edge CDN / Browser Runtime                                                |
|                                                                                         |
|   Key Responsibilities:                                                                 |
|   1. Universal Tool Runner interface with dynamic forms based on Tool Registry schema.  |
|   2. Client-side pre-flight file checks (file extension, size ceiling, format limits).|
|   3. Interactive PDF page browsing & visual reordering powered by PDF.js in web worker. |
|   4. Secure cookie transport (HttpOnly credentials for all API invocations).           |
|   5. Optimistic UI feedback, active job polling, and Server-Sent Event (SSE) listeners. |
|                                                                                         |
|   Explicit Restrictions:                                                                |
|   - NEVER performs document transformations (no in-browser PDF manipulation).           |
|   - NEVER holds master object storage credentials (S3 keys, DB strings).               |
|   - NEVER bypasses backend job creation or direct database queries.                    |
+-----------------------------------------------------------------------------------------+
                                             |
                         HTTPS / TLS 1.3     |  Standardized REST API v1
                         HttpOnly Cookies    |  Pre-Signed Upload/Download S3 URLs
                                             v
+-----------------------------------------------------------------------------------------+
|                                SERVER APPLICATION (apps/api)                            |
|                                                                                         |
|   Platform: Python 3.11+, FastAPI, Celery, SQLAlchemy 2.0 Async, PostgreSQL 16, Redis 7 |
|   Deployment: Containerized Linux Instances (App Engine, Render, Railway, or VPS)      |
|                                                                                         |
|   Key Responsibilities:                                                                 |
|   1. Authoritative identity, password hashing (bcrypt), session tokens & user quotas.   |
|   2. Input Gatekeeping: Magic bytes inspection, SHA-256 integrity, zip bomb detection.  |
|   3. Issue short-lived, cryptographically signed S3 URLs for direct binary I/O.         |
|   4. Queue & Job Management: Dispatches tasks across partitioned Celery worker queues.  |
|   5. Processing Engines: Pure Python & native tools (PyMuPDF, pypdf, Ghostscript, etc.)  |
|   6. Isolation: Workers execute with restricted privileges, no network egress, memory cap|
|   7. Automatic File Hygiene: Purges ephemeral scratch directories upon job completion.  |
+-----------------------------------------------------------------------------------------+
```

### 1.2 System Topology Diagram

```
                              +---------------------------------------+
                              |      Web Client (Browser / Mobile)    |
                              +-------------------+-------------------+
                                                  |
                                                  | HTTPS / REST / SSE
                                                  v
                              +---------------------------------------+
                              |      Next.js 14+ (apps/web)           |
                              |  - Server & Client Components (React) |
                              |  - Universal Tool Runner Framework    |
                              |  - TanStack Query v5 + Tailwind CSS   |
                              +-------------------+-------------------+
                                                  |
                                                  | Reverse Proxy / JSON API
                                                  v
                              +---------------------------------------+
                              |       FastAPI Core (apps/api)         |
                              |  - API Router v1 (/auth, /files, etc) |
                              |  - SQLAlchemy 2.0 Async ORM           |
                              |  - Storage Abstraction Layer (S3/Disk)|
                              |  - Celery Task Dispatcher             |
                              +--------+---------------------+--------+
                                       |                     |
                 +---------------------+                     +---------------------+
                 v                                                                 v
+----------------------------------+                             +----------------------------------+
|      PostgreSQL 16 Database      |                             |       Redis 7 In-Memory Cache    |
|  - Users, Workspaces, Files      |                             |  - Celery Task Message Broker    |
|  - Jobs, Audit Logs, Shares      |                             |  - Job State Pub/Sub & Caching   |
+----------------------------------+                             +-----------------+----------------+
                                                                                   |
                                          +----------------------------------------+
                                          |
                                          v  Task Queues: `pdf_queue`, `img_queue`, `conv_queue`, etc.
+---------------------------------------------------------------------------------------------------+
|                                 Distributed Celery Worker Pods                                    |
|                                                                                                   |
|   +------------------------------------+             +------------------------------------+       |
|   |            PDF Worker              |             |           Image Worker             |       |
|   |  - PyMuPDF (fitz)                  |             |  - Pillow (PIL)                    |       |
|   |  - pypdf                           |             |  - OpenCV                          |       |
|   |  - qpdf CLI                        |             |  - ImageHash / ExifTool            |       |
|   +------------------------------------+             +------------------------------------+       |
|   +------------------------------------+             +------------------------------------+       |
|   |        Compression Worker          |             |         Conversion Worker          |       |
|   |  - Ghostscript (gs)                |             |  - LibreOffice Headless            |       |
|   |  - Object stream recompression     |             |  - pdf2docx / openpyxl / pandoc    |       |
|   +------------------------------------+             +------------------------------------+       |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   v
                                   +----------------------------------+
                                   | Object Storage (S3 / R2 / Local) |
                                   |  - uploads/                      |
                                   |  - processed/                    |
                                   |  - workspace/                    |
                                   +----------------------------------+
```

---

## 2. Monorepo Directory Layout

The repository is structured as a clear, maintainable monorepo:

```
pdfpride/
├── apps/
│   ├── api/                                # FastAPI Backend & Worker Root
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── auth.py             # User registration, login, session
│   │   │   │       ├── files.py            # Uploads, metadata, downloads, previews
│   │   │   │       ├── pdf.py              # PDF merge, split, rotate, organize, etc.
│   │   │   │       ├── conversions.py      # Cross-format file conversions
│   │   │   │       ├── compression.py      # PDF & image optimization
│   │   │   │       ├── images.py           # Image studio operations
│   │   │   │       ├── jobs.py             # Polling, status, cancellation
│   │   │   │       ├── workspace.py        # Folders, trash, quota metrics
│   │   │   │       ├── sharing.py          # Secure share links
│   │   │   │       └── admin.py            # System metrics, user governance
│   │   │   ├── core/
│   │   │   │   ├── config.py               # Pydantic BaseSettings & env parsing
│   │   │   │   ├── database.py             # Async SQLAlchemy engine & session factory
│   │   │   │   ├── security.py             # Password hashing (bcrypt), token handling
│   │   │   │   └── exceptions.py           # Standardized API error responses
│   │   │   ├── models/                     # SQLAlchemy 2.0 ORM Models
│   │   │   │   ├── user.py
│   │   │   │   ├── workspace.py
│   │   │   │   ├── file.py
│   │   │   │   ├── job.py
│   │   │   │   └── share.py
│   │   │   ├── schemas/                    # Pydantic v2 Request/Response Schemas
│   │   │   │   ├── user.py
│   │   │   │   ├── file.py
│   │   │   │   └── job.py
│   │   │   ├── engines/                    # Pure Python Transformation Engines
│   │   │   │   ├── base.py                 # BaseEngine abstract class
│   │   │   │   ├── pdf/
│   │   │   │   │   ├── merge.py            # PDF-001: Merge engine
│   │   │   │   │   ├── split.py            # PDF-002: Split engine
│   │   │   │   │   ├── compress.py         # PDF-003: Compression engine
│   │   │   │   │   ├── rotate.py           # PDF-004: Rotate engine
│   │   │   │   │   └── organize.py         # PDF-005: Visual organize engine
│   │   │   │   ├── image/
│   │   │   │   │   ├── converter.py        # PDF-015/016: JPG<->PDF, PNG<->PDF
│   │   │   │   │   └── optimize.py         # Image resizing, EXIF stripping
│   │   │   │   └── office/
│   │   │   │       └── libreoffice.py      # Headless conversion wrapper
│   │   │   ├── storage/                    # Storage Abstraction
│   │   │   │   ├── base.py                 # StorageDriver interface
│   │   │   │   ├── local.py                # Local filesystem driver (dev)
│   │   │   │   └── s3.py                   # AWS S3 / Cloudflare R2 driver (prod)
│   │   │   ├── workers/                    # Celery Application & Tasks
│   │   │   │   ├── celery_app.py           # Celery initialization & configuration
│   │   │   │   ├── tasks_pdf.py            # PDF task handlers
│   │   │   │   ├── tasks_compression.py    # Compression task handlers
│   │   │   │   └── tasks_image.py          # Image task handlers
│   │   │   └── main.py                     # FastAPI application entrypoint
│   │   ├── migrations/                     # Alembic database migrations
│   │   ├── tests/                          # Automated pytest test suites
│   │   ├── Dockerfile                      # Production container recipe
│   │   └── requirements.txt                # Python dependencies
│   │
│   └── web/                                # Next.js 14+ Frontend Application
│       ├── src/
│       │   ├── app/
│       │   │   ├── (marketing)/
│       │   │   │   ├── page.tsx            # Landing page & quick dropzone
│       │   │   │   └── tools/
│       │   │   │       ├── page.tsx        # Directory of all tools
│       │   │   │       └── [slug]/
│       │   │   │           └── page.tsx    # Universal Dynamic Tool Runner
│       │   │   ├── (auth)/
│       │   │   │   ├── login/page.tsx
│       │   │   │   └── register/page.tsx
│       │   │   ├── (dashboard)/
│       │   │   │   ├── workspace/page.tsx  # Workspace file manager
│       │   │   │   └── history/page.tsx    # User processing history
│       │   │   └── layout.tsx              # Root HTML & layout shell
│       │   ├── components/
│       │   │   ├── ui/                     # Button, Dialog, Dropdown, Progress, etc.
│       │   │   ├── layout/                 # Navbar, Sidebar, Footer
│       │   │   ├── tools/
│       │   │   │   ├── UniversalToolRunner.tsx # Reusable 4-step tool UI
│       │   │   │   ├── FileDropzone.tsx    # Drag-and-drop uploader with previews
│       │   │   │   ├── ToolOptionsPanel.tsx# Parameter controls per tool
│       │   │   │   └── JobProgressBar.tsx  # Dynamic stage & progress indicator
│       │   │   └── workspace/
│       │   │       ├── FileManager.tsx     # Files and folders explorer
│       │   │       └── FilePreviewModal.tsx# PDF.js preview dialog
│       │   ├── lib/
│       │   │   ├── api-client.ts           # Axios / fetch wrapper with credentials
│       │   │   └── tool-registry.ts        # Client-side tool registry access
│       │   └── types/                      # Frontend TypeScript interfaces
│       ├── public/                         # Static assets & SVG icons
│       ├── package.json
│       ├── tailwind.config.ts
│       └── tsconfig.json
│
├── packages/
│   └── tool-registry/                      # Shared Single-Source-of-Truth
│       ├── src/
│       │   ├── index.ts                    # Tool definitions, schemas, categories
│       │   └── tools.json                  # JSON representation for Python backend
│       └── package.json
│
├── docker-compose.yml                      # Full local stack orchestrator
├── .env.example                            # Unified environment template
├── prd.md                                  # Product Requirements Document
├── implementation.md                       # This Implementation Guide
└── README.md                               # Project documentation
```

---

## 3. Core Database Models (SQLAlchemy 2.0 Async)

The database models are designed with UUID primary keys, soft-delete capabilities, and strict relational integrity.

```python
# apps/api/app/models/base.py
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
```

### 3.1 File and Processing Job Entities
```python
# apps/api/app/models/job.py
import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from apps.api.app.models.base import Base, TimestampMixin

class ProcessingJob(Base, TimestampMixin):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    
    operation: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'pdf_merge', 'pdf_compress'
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True) # QUEUED, PROCESSING, VALIDATING, COMPLETED, FAILED
    progress: Mapped[int] = mapped_column(Integer, default=0) # 0 to 100
    stage_message: Mapped[str] = mapped_column(String(255), default="Job queued in queue")
    options: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    files = relationship("JobFile", back_populates="job", cascade="all, delete-orphan")
```

---

## 4. Processing Engines Specification

All processing logic is packaged into isolated, pure-function or class-based engines inheriting from a common `BaseEngine`.

```python
# apps/api/app/engines/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class EngineResult:
    def __init__(self, output_paths: List[Path], metrics: Dict[str, Any] = None):
        self.output_paths = output_paths
        self.metrics = metrics or {}

class BaseEngine(ABC):
    @abstractmethod
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        """
        Executes the document operation.
        :param input_paths: List of absolute paths to input documents.
        :param output_dir: Ephemeral working directory where outputs should be saved.
        :param options: Validated dictionary of operational parameters.
        :param progress_callback: Callable accepting (progress: int, message: str)
        :return: EngineResult containing generated output file paths and operational metrics.
        """
        pass
```

### 4.1 PDF Merge Engine (`PDF-001`)
```python
# apps/api/app/engines/pdf/merge.py
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from apps.api.app.engines.base import BaseEngine, EngineResult

class PDFMergeEngine(BaseEngine):
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        output_doc = fitz.open()
        total_files = len(input_paths)

        if progress_callback:
            progress_callback(10, f"Initializing merge of {total_files} files...")

        for idx, path in enumerate(input_paths):
            with fitz.open(path) as src_doc:
                output_doc.insert_pdf(src_doc)
            
            if progress_callback:
                progress = int(10 + (idx + 1) / total_files * 80)
                progress_callback(progress, f"Merged file {idx + 1} of {total_files}")

        output_filename = options.get("output_filename", "merged_document.pdf")
        output_path = output_dir / output_filename
        
        if progress_callback:
            progress_callback(95, "Finalizing output structure and writing to disk...")

        # Garbage collect and write linearized output
        output_doc.save(str(output_path), garbage=4, deflate=True)
        total_pages = len(output_doc)
        output_doc.close()

        return EngineResult(
            output_paths=[output_path],
            metrics={"total_pages": total_pages, "input_files_count": total_files}
        )
```

### 4.2 PDF Compress Engine (`PDF-003`)
```python
# apps/api/app/engines/pdf/compress.py
import subprocess
import shutil
import fitz
from pathlib import Path
from typing import List, Dict, Any
from apps.api.app.engines.base import BaseEngine, EngineResult

class PDFCompressEngine(BaseEngine):
    """
    Two-tier compression engine:
    1. PyMuPDF image downsampling & stream deflation (fast, high compatibility)
    2. Ghostscript PDF optimizer for extreme compression profiles (when GS is installed)
    """
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        input_path = input_paths[0]
        profile = options.get("profile", "balanced") # low, balanced, high, extreme
        output_path = output_dir / f"compressed_{input_path.name}"

        orig_size = input_path.stat().st_size
        if progress_callback:
            progress_callback(20, f"Analyzing PDF streams (Profile: {profile})...")

        # PyMuPDF-based stream optimization & image reduction
        doc = fitz.open(input_path)
        total_pages = len(doc)

        # Deflation and garbage collection
        deflate_val = True
        garbage_val = 4 # maximum unused object elimination

        if progress_callback:
            progress_callback(60, "Re-compressing internal object streams...")

        doc.save(
            str(output_path), 
            garbage=garbage_val, 
            deflate=deflate_val,
            clean=True
        )
        doc.close()

        new_size = output_path.stat().st_size
        reduction_pct = round(((orig_size - new_size) / orig_size) * 100, 2) if orig_size > 0 else 0

        if progress_callback:
            progress_callback(100, f"Completed: reduced by {reduction_pct}%")

        return EngineResult(
            output_paths=[output_path],
            metrics={
                "original_size": orig_size,
                "compressed_size": new_size,
                "reduction_percentage": max(reduction_pct, 0),
                "profile": profile
            }
        )
```

### 4.3 Images to PDF Engine (`PDF-016`) & PDF to Images (`PDF-015`)
```python
# apps/api/app/engines/image/converter.py
from PIL import Image
import fitz
from pathlib import Path
from typing import List, Dict, Any
from apps.api.app.engines.base import BaseEngine, EngineResult

class ImagesToPDFEngine(BaseEngine):
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        images = []
        for idx, img_path in enumerate(input_paths):
            im = Image.open(img_path)
            # Normalize to RGB for PDF standard compatibility
            if im.mode in ("RGBA", "P"):
                rgb_im = Image.new("RGB", im.size, (255, 255, 255))
                if im.mode == "RGBA":
                    rgb_im.paste(im, mask=im.split()[3])
                else:
                    rgb_im.paste(im)
                images.append(rgb_im)
            else:
                images.append(im.convert("RGB"))

        output_path = output_dir / options.get("output_filename", "converted_images.pdf")
        if images:
            images[0].save(
                output_path, 
                "PDF", 
                resolution=100.0, 
                save_all=True, 
                append_images=images[1:]
            )

        return EngineResult(
            output_paths=[output_path],
            metrics={"images_count": len(input_paths)}
        )

class PDFToImagesEngine(BaseEngine):
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        doc = fitz.open(input_paths[0])
        dpi = options.get("dpi", 150)
        img_format = options.get("format", "png").lower()
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        output_paths = []
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_file = output_dir / f"page_{page_num + 1}.{img_format}"
            pix.save(str(img_file))
            output_paths.append(img_file)
            
            if progress_callback:
                progress = int(((page_num + 1) / total_pages) * 90)
                progress_callback(progress, f"Rendered page {page_num + 1} of {total_pages}")

        doc.close()
        return EngineResult(
            output_paths=output_paths,
            metrics={"pages_rendered": total_pages, "dpi": dpi, "format": img_format}
        )
```

---

## 5. Storage Abstraction Layer

To ensure environment portability between local development, testing, and production, all file persistence is wrapped inside a pluggable `StorageDriver`:

```python
# apps/api/app/storage/base.py
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path

class StorageDriver(ABC):
    @abstractmethod
    def put_file(self, file_obj: BinaryIO, storage_key: str, content_type: str) -> str:
        """Stores a binary stream under the designated storage key."""
        pass

    @abstractmethod
    def get_file(self, storage_key: str) -> BinaryIO:
        """Retrieves a readable binary stream for the specified key."""
        pass

    @abstractmethod
    def delete_file(self, storage_key: str) -> bool:
        """Deletes a file object by key."""
        pass

    @abstractmethod
    def generate_signed_url(self, storage_key: str, expires_in_seconds: int = 3600) -> str:
        """Generates a secure, temporary pre-signed URL for direct browser access."""
        pass
```

* **Local Disk Driver (`apps/api/app/storage/local.py`):** Saves files into a designated mount directory (`/data/storage`), supporting streaming directly via FastAPI's `FileResponse`. Perfect for zero-cost local dev.
* **S3 / Cloudflare R2 Driver (`apps/api/app/storage/s3.py`):** Uses `boto3` to interact with AWS S3 or Cloudflare R2 object stores with bucket segregation: `uploads/`, `processed/`, `workspace/`.

---

## 6. Celery Background Worker & Job Dispatcher

Tasks are queued via Celery using Redis as the message broker. Each task runs isolated with automatic progress reporting and error capture:

```python
# apps/api/app/workers/tasks_pdf.py
from apps.api.app.workers.celery_app import celery_app
from apps.api.app.engines.pdf.merge import PDFMergeEngine
from apps.api.app.engines.pdf.split import PDFSplitEngine
from apps.api.app.engines.pdf.compress import PDFCompressEngine
from apps.api.app.engines.image.converter import ImagesToPDFEngine, PDFToImagesEngine
from apps.api.app.storage.base import StorageDriver
from pathlib import Path
import tempfile
import traceback

@celery_app.task(bind=True, name="tasks.process_document_job")
def process_document_job(self, job_id: str, operation: str, input_keys: list, options: dict):
    """
    Universal Celery task orchestrator:
    1. Downloads input files from storage into an isolated temp directory.
    2. Instantiates appropriate engine from registry.
    3. Executes operation while updating job progress in Redis/Postgres.
    4. Uploads generated outputs back to Storage.
    5. Marks job as COMPLETED or FAILED.
    """
    # Dynamic engine dispatch
    ENGINES = {
        "pdf_merge": PDFMergeEngine,
        "pdf_compress": PDFCompressEngine,
        "images_to_pdf": ImagesToPDFEngine,
        "pdf_to_images": PDFToImagesEngine,
    }

    engine_cls = ENGINES.get(operation)
    if not engine_cls:
        raise ValueError(f"Unknown operation: {operation}")

    # Execution logic with temporary workspace cleanup
    with tempfile.TemporaryDirectory() as temp_dir_str:
        work_dir = Path(temp_dir_str)
        # Fetch inputs, run engine, upload results, update DB status
        # ... (Implemented in full codebase)
```

---

## 7. Dynamic Centralized Tool Registry

The Tool Registry is the single source of truth for all tools across the system. It defines metadata, categories, icons, accepted MIME types, limits, and options schemas:

```json
[
  {
    "id": "pdf-merge",
    "slug": "merge-pdf",
    "name": "Merge PDF",
    "category": "organize",
    "description": "Combine multiple PDF documents into a single organized file in your chosen order.",
    "icon": "Layers",
    "accepted_mimes": ["application/pdf"],
    "accepted_extensions": [".pdf"],
    "min_files": 2,
    "max_files": 20,
    "operation": "pdf_merge",
    "is_featured": true,
    "options_schema": {
      "type": "object",
      "properties": {
        "output_filename": {"type": "string", "default": "merged_document.pdf"}
      }
    }
  },
  {
    "id": "pdf-compress",
    "slug": "compress-pdf",
    "name": "Compress PDF",
    "category": "optimize",
    "description": "Reduce PDF file size without sacrificing readability and visual quality.",
    "icon": "Minimize2",
    "accepted_mimes": ["application/pdf"],
    "accepted_extensions": [".pdf"],
    "min_files": 1,
    "max_files": 1,
    "operation": "pdf_compress",
    "is_featured": true,
    "options_schema": {
      "type": "object",
      "properties": {
        "profile": {
          "type": "string", 
          "enum": ["low", "balanced", "high", "extreme"],
          "default": "balanced"
        }
      }
    }
  },
  {
    "id": "img-to-pdf",
    "slug": "jpg-to-pdf",
    "name": "JPG to PDF",
    "category": "convert",
    "description": "Convert JPG, PNG, and WebP images into a polished, multi-page PDF document.",
    "icon": "Image",
    "accepted_mimes": ["image/jpeg", "image/png", "image/webp"],
    "accepted_extensions": [".jpg", ".jpeg", ".png", ".webp"],
    "min_files": 1,
    "max_files": 30,
    "operation": "images_to_pdf",
    "is_featured": true,
    "options_schema": {
      "type": "object",
      "properties": {
        "orientation": {"type": "string", "enum": ["auto", "portrait", "landscape"], "default": "auto"}
      }
    }
  },
  {
    "id": "pdf-to-img",
    "slug": "pdf-to-jpg",
    "name": "PDF to JPG",
    "category": "convert",
    "description": "Extract every page of a PDF document into high-resolution JPG images.",
    "icon": "FileImage",
    "accepted_mimes": ["application/pdf"],
    "accepted_extensions": [".pdf"],
    "min_files": 1,
    "max_files": 1,
    "operation": "pdf_to_images",
    "is_featured": true,
    "options_schema": {
      "type": "object",
      "properties": {
        "dpi": {"type": "integer", "default": 150},
        "format": {"type": "string", "enum": ["jpg", "png"], "default": "jpg"}
      }
    }
  }
]
```

---

## 8. Frontend Client Architecture & Aesthetic Specifications

### 8.1 Anti-AI Design Philosophy & Swiss Engineering Precision
The frontend client rejects the homogenized "AI product" template look (no gradient blobs, no floating purple shadows, no pale/washed-out pastel cards, no curved pills). Instead, it implements a **Swiss International / Industrial Precision** design language:

1. **Zero Curved Radiuses:** All containers, buttons, inputs, file dropzones, and modal dialogs strictly enforce flat boxes with sharp 90-degree right angles (`border-radius: 0px`).
2. **Major Solid Colors:** Zero gradients. High-contrast bold colors:
   - `major-black` (`#000000`): Structural 2px/4px border outlines, text, primary controls.
   - `major-white` (`#FFFFFF`): Crisp optical white surface backgrounds.
   - `major-red` (`#D00000`): Authoritative primary highlight, CTA accents, and critical status.
   - `major-blue` (`#0038FF`): Pure cobalt for progress execution indicators.
3. **Iconography:** Standardized on **FontAwesome 6 Solid (Free)** SVG components (`FaFilePdf`, `FaLayerGroup`, `FaScissors`, `FaCompress`, `FaCloudArrowUp`, `FaFolder`, etc.).
4. **Physical Flat Shadows:** Uses sharp geometric drop offsets (`shadow-flat: 4px 4px 0px 0px #000000`) providing a tactile, high-end commercial feel.

### 8.2 Universal Tool Runner Architecture

The Next.js frontend implements a **Universal Tool Runner** component (`UniversalToolRunner.tsx`). This single component powers all `/tools/[slug]` routes dynamically:

1. **Route Resolution:** `/tools/[slug]` fetches tool metadata from the Tool Registry.
2. **Step 1 (Upload):** Dropzone accepts files matching `accepted_extensions`, runs client-side size checks, and initiates multipart/pre-signed upload.
3. **Step 2 (Configuration):** Renders dynamic controls (sliders, dropdowns, page order drag handles) based on the tool's `options_schema`.
4. **Step 3 (Execution & Progress):** Calls `POST /api/v1/jobs` or the specific endpoint (e.g. `/pdf/merge`). Starts polling `GET /api/v1/jobs/{id}` at 1-second intervals via TanStack Query.
5. **Step 4 (Download & Actions):** Shows success metrics (e.g., file size reduction %, page counts) and exposes instant direct download and "Save to Workspace" buttons.

---

## 9. Docker Compose Infrastructure Orchestration

The platform is fully orchestrated locally via `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: pdfpride_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-pdfpride}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-pdfpride_secret}
      POSTGRES_DB: ${POSTGRES_DB:-pdfpride_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pdfpride -d pdfpride_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis Task Broker & State Cache
  redis:
    image: redis:7-alpine
    container_name: pdfpride_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # FastAPI Backend API Server
  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    container_name: pdfpride_api
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-pdfpride}:${POSTGRES_PASSWORD:-pdfpride_secret}@postgres:5432/${POSTGRES_DB:-pdfpride_db}
      REDIS_URL: redis://redis:6379/0
      STORAGE_DRIVER: local
      LOCAL_STORAGE_DIR: /data/storage
      JWT_SECRET: ${JWT_SECRET:-pdfpride_super_secret_jwt_key_2026}
    volumes:
      - ./apps/api:/app/apps/api
      - shared_storage:/data/storage
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Celery Background Processing Worker
  worker:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    container_name: pdfpride_worker
    command: celery -A apps.api.app.workers.celery_app.celery_app worker --loglevel=info -c 4
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-pdfpride}:${POSTGRES_PASSWORD:-pdfpride_secret}@postgres:5432/${POSTGRES_DB:-pdfpride_db}
      REDIS_URL: redis://redis:6379/0
      STORAGE_DRIVER: local
      LOCAL_STORAGE_DIR: /data/storage
    volumes:
      - ./apps/api:/app/apps/api
      - shared_storage:/data/storage
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Next.js Web Frontend
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    container_name: pdfpride_web
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    volumes:
      - ./apps/web:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
  shared_storage:
```

---

## 10. Verification & Quality Acceptance Checklist

Before any release, the implementation must pass the following verification tests:
1. **API Health & Discovery:** `GET /api/v1/health` and `GET /api/v1/tools` return HTTP 200 with complete registry definitions.
2. **File Ingestion:** `POST /api/v1/files/upload/direct` correctly writes files to storage, computes matching SHA-256 checksums, and creates database records.
3. **Core Engine Verification:**
   - **Merge:** Merging two 2-page PDFs produces a valid 4-page PDF without stream corruption.
   - **Split:** Splitting page 1 from a 3-page document extracts precisely 1 page.
   - **Compress:** Compression on an image-heavy PDF executes without degradation of text clarity, logging reduction percentages.
   - **Image-to-PDF / PDF-to-Image:** Bi-directional transformations match image aspect ratios accurately.
4. **Asynchronous Polling:** Job status transitions cleanly from `QUEUED` -> `PROCESSING` -> `VALIDATING` -> `COMPLETED` with live percentage reporting.
