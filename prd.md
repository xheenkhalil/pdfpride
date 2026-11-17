# Product Requirements Document (PRD)
## PDF Pride (Document Studio)

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Target Platform:** Web (Desktop & Mobile Responsive SaaS)  
**Architecture Pattern:** Modular Monolith + Distributed Background Worker Pools  

---

## 1. Executive Summary & Product Vision

### 1.1 Product Identity
**PDF Pride** (internally designated **Document Studio**) is an enterprise-grade, cloud-hosted document processing and productivity platform. It provides a comprehensive, centralized suite of PDF manipulation tools, cross-format document converters, image utilities, visual editing and annotation capabilities, document intelligence/OCR, and secure persistent cloud workspace storage.

* **Core Value Proposition:** All your document tools in one unified, private, lightning-fast platform.
* **Target Audience:** Public users, students, academic researchers, legal and corporate professionals, SMEs, and enterprise organizations.
* **Service Model:** Freemium SaaS with guest access (temporary ephemeral processing), authenticated user tiers (cloud workspace and higher limits), and administrative governance.

### 1.2 Core Product Principles
1. **No Artificial Feature Claims:** If a feature (such as PDF to Excel) is exposed in the interface, it must produce authentic, structured, valid target files, never simple extension renames or corrupted mocks.
2. **Native & Open-Source Processing:** Rely on self-hosted, battle-tested open-source engines (PyMuPDF, pypdf, qpdf, Ghostscript, LibreOffice, Pillow, OpenCV, Tesseract/OCRmyPDF) to ensure user privacy, minimize variable API costs, and guarantee processing sovereignty.
3. **Strict Separation of Concerns:** Core document processing logic is decoupled into standalone engines (`engines/`), orchestrated via Celery background workers, and consumed through versioned REST APIs. The frontend acts as a unified presentation and interaction layer.
4. **Asynchronous by Default:** All heavy operations are job-based. Users are never held hostage to an open HTTP connection; jobs are assigned unique IDs, tracked through states, and persist even if the browser session disconnects.
5. **Zero Trust & Privacy by Design:** Uploaded user files are strictly private by default. Untrusted user documents are isolated, scrubbed, validated for malicious payloads (decompression bombs, malformed PostScript, embedded exploits), and automatically pruned via lifecycle policies.

---

## 2. User Personas & Access Governance

### 2.1 Persona Definitions
* **Guest User:** Unauthenticated visitor needing immediate, one-off file transformations (e.g., merge 2 receipts, compress a CV). Requires zero friction, no signup, with short retention of generated files.
* **Registered Free User:** Authenticated user who needs a persistent workspace, multi-file batch processing, history tracking, folder organization, and secure shareable links.
* **Power / Pro User (Future Commercial Tier):** High-volume user processing hundreds of pages, requiring heavy OCR, extreme compression, batch operations, and extended cloud storage.
* **Platform Administrator:** Internal team member monitoring platform health, queue latency, storage usage, error rates, managing user accounts, and toggling tools via the dynamic Tool Registry.

### 2.2 Access Control & Quota Matrix

| Capability | Guest User | Registered User (Free Tier) | Administrator |
| :--- | :--- | :--- | :--- |
| **Basic PDF Operations** | Yes (Limited) | Yes | Yes |
| **Max File Upload Size** | 10 MB | 100 MB (Expandable) | Unlimited / 1 GB |
| **Files Per Operation** | Up to 2 files | Up to 20 files | 100+ files |
| **Concurrent Active Jobs** | 1 job | 3 concurrent jobs | 10 concurrent jobs |
| **Daily Operation Limit** | 5 jobs / day | 50 jobs / day | Unlimited |
| **Batch Processing Mode** | No | Yes | Yes |
| **Persistent Cloud Workspace** | No | Yes (2 GB Storage) | Dedicated storage |
| **File Retention Policy** | Auto-purged after 2 hours | Permanent until deleted | Configurable |
| **Processing History** | Browser session only | Permanent searchable history | Global platform log |
| **Shareable Link Generation** | No | Yes (Up to 10 active links) | Full access |
| **OCR & AI Extraction** | Limited (1 page preview) | Full (up to 30 pages/job) | Unlimited |
| **Platform Administration** | No | No | Yes |

---

## 3. High-Level System Architecture & Client-Server Differentiation

### 3.1 Strict Client vs. Server Separation of Concerns

PDF Pride enforces an unyielding architectural and security boundary between the **Frontend (Client)** and the **Backend (Server)**. The client is treated as an untrusted consumer and presentation surface, while the backend is the authoritative, secure boundary.

```
+-----------------------------------------------------------------------------------------+
|                                UNTRUSTED CLIENT BOUNDARY                                |
|                                                                                         |
|   Frontend Client (Next.js 14+ / React / TypeScript / Browser Canvas)                  |
|   - Presentation, Routing, and Responsive Layouts                                       |
|   - Client-side File Sniffing & Basic Pre-checks (File size, extension)                |
|   - Interactive PDF Rendering via PDF.js (In-browser viewer & visual page selector)     |
|   - Drag-and-Drop UX & Multi-file Sequencing                                            |
|   - Real-time Job Status Polling / Server-Sent Events (SSE) Listener                    |
|   - Session Cookie Transport & Ephemeral Client State Management                        |
|   * ZERO Direct Database Access | ZERO Direct Cloud Storage Credentials                |
|   * ZERO Native Document Modification (No in-browser PDF manipulation)                  |
+-----------------------------------------------------------------------------------------+
                                             |
                         HTTPS / TLS 1.3     |  Strict REST JSON Contract
                         HttpOnly Cookies    |  Pre-signed S3 URLs for Binaries
                                             v
+-----------------------------------------------------------------------------------------+
|                                 TRUSTED SERVER BOUNDARY                                 |
|                                                                                         |
|   API Server (FastAPI / Python Modular Monolith)                                        |
|   - Authoritative Authentication, Session Verification & RBAC                           |
|   - Rate Limiting, Abuse Prevention & Quota Accounting                                  |
|   - File Ingestion Gatekeeper: Magic-byte inspection, SHA-256 hashing, AV scanning      |
|   - Signed Object Storage URL Issuer (Cloudflare R2 / AWS S3)                           |
|   - Central Tool Registry Enforcement & Job Dispatcher                                  |
|                                                                                         |
|   Distributed Worker Server Pool (Celery + Isolated Linux Containers)                   |
|   - Sandboxed Execution: Restricted syscalls, no network egress, hard memory limits    |
|   - Native Document Processing Engines (PyMuPDF, pypdf, Ghostscript, LibreOffice)       |
|   - Step-by-step Execution Progress Reporting to Redis Broker                           |
|   - Strict Output Integrity Validation (qpdf check, PDF syntax verification)            |
|   - Automatic Scratch Volume Scavenging & Ephemeral File Erasure                        |
|                                                                                         |
|   Authoritative Persistence Layer                                                       |
|   - PostgreSQL 16 (Relational Metadata, ACID Workspaces, RLS Isolation)                 |
|   - Redis 7 (Task Message Broker, State Cache, Distributed Locks)                       |
|   - Object Store (Encrypted At Rest Document Binaries)                                  |
+-----------------------------------------------------------------------------------------+
```

| Dimension | Frontend (Client) | Backend (Server) |
| :--- | :--- | :--- |
| **Technology** | Next.js 14, React 18, TypeScript, Tailwind CSS, TanStack Query | Python 3.11+, FastAPI, SQLAlchemy 2.0 Async, Celery, Redis, PostgreSQL 16 |
| **Runtime Environment** | User Browser / Client-side Edge CDN | Hardened Linux Containers / Cloud Infrastructure |
| **Trust Level** | **Untrusted** — subject to user tampering and network inspection | **Authoritative & Trusted** — holds secrets, credentials, DB access |
| **File Processing Role** | Renders visual previews (PDF.js), captures user intent and options | Executes actual byte-level operations (merge, split, compress, convert, OCR) |
| **Storage Access** | Obtains short-lived, pre-signed upload/download URLs from server | Generates cryptographically signed URLs; controls object keys and buckets |
| **State Management** | Ephemeral UI state, optimistic feedback, active job polling cache | Persistent transactional state in PostgreSQL, pub/sub queues in Redis |
| **Security Controls** | Form validation, sanitization of rendered text | Input sanitization, magic-byte verification, decompression bomb prevention, sandboxed execution |

### 3.2 Architectural Topology: Modular Monolith + Worker Pool
The server architecture adopts a modular monolith approach for API orchestration and database consistency, paired with independently scalable background worker processes for CPU- and memory-intensive document rendering and transformation tasks.

```
                      +-----------------------------+
                      |   Cloudflare CDN / WAF      |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |  Next.js Frontend (Vercel)  |
                      |  TypeScript + Tailwind CSS  |
                      +--------------+--------------+
                                     |
                       HTTPS REST / Signed URLs
                                     |
                                     v
                      +-----------------------------+
                      |     FastAPI Backend API     |
                      |  (Auth, Metadata, Dispatch) |
                      +-------+--------------+------+
                              |              |
         +--------------------+              +-------------------+
         |                                                       |
         v                                                       v
+------------------+                                    +------------------+
| PostgreSQL 16    |                                    | Redis 7 Broker   |
| (ACID Metadata,  |                                    | (Task Queues &   |
| RLS, Quotas)     |                                    | Job Pub/Sub)     |
+------------------+                                    +--------+---------+
                                                                 |
               +-------------------------------------------------+
               | Celery Task Distribution
               v
+--------------------------------------------------------------------------+
|                       Specialized Worker Pools                           |
|  +--------------------+  +--------------------+  +--------------------+  |
|  |    PDF Workers     |  | Conversion Workers |  | Compression Workers|  |
|  |  (PyMuPDF / pypdf) |  |   (LibreOffice)    |  |    (Ghostscript)   |  |
|  +--------------------+  +--------------------+  +--------------------+  |
|  +--------------------+  +--------------------+  +--------------------+  |
|  |   Image Workers    |  |    OCR Workers     |  | Intelligence Workers| |
|  |  (Pillow / OpenCV) |  | (Tesseract/OCRmyPDF)| | (Classification/AI)|  |
|  +--------------------+  +--------------------+  +--------------------+  |
+------------------------------------+-------------------------------------+
                                     |
                                     v
                     +-------------------------------+
                     | S3 / Cloudflare R2 / MinIO    |
                     | Encrypted Object Storage      |
                     +-------------------------------+
```

### 3.2 Processing Pipeline & Job State Machine
Every processing request adheres to a strictly validated lifecycle:
1. **Submission:** Client uploads file(s) directly to S3 via pre-signed URL or multipart stream to the API.
2. **Registration:** Backend validates mime-types, SHA-256 checksums, and quota availability, creating a `processing_jobs` record in `QUEUED` status.
3. **Dispatch:** Task dispatched to Redis queue matching the workload domain (e.g. `pdf_queue`, `conversion_queue`).
4. **Execution:** Worker picks up task, transitions status to `PROCESSING`, streams intermediate progress stages (0% to 100%), and writes temporary working files to an ephemeral ramdisk or scratch volume.
5. **Validation:** Worker verifies the integrity of generated output documents (`VALIDATING`).
6. **Completion:** Output persisted to Object Storage (`processed/` or `workspace/`). Job transitioned to `COMPLETED`.
7. **Failure Handling:** If an unrecoverable exception occurs, job transitions to `FAILED`, stores sanitized user-facing error diagnostics, and triggers automatic cleanup of orphaned files.

```
+------------+       +------------+       +------------+       +-------------+
|   QUEUED   | ----> | PROCESSING | ----> | VALIDATING | ----> |  COMPLETED  |
+------------+       +------------+       +------------+       +-------------+
       |                   |                    |                     |
       v                   v                    v                     v
   [EXPIRED]           [FAILED]             [FAILED]            [Downloaded]
                                                                [Saved to WS]
```

---

## 4. Comprehensive Feature Catalogue

### 4.1 Module 1: PDF Operations (Catalogue IDs PDF-001 to PDF-040)

| Tool ID | Feature Name | Core Processing Engine | Input / Output | Key Operational Parameters |
| :--- | :--- | :--- | :--- | :--- |
| **PDF-001** | Merge PDF | `PyMuPDF` / `pypdf` | Multiple PDFs -> Single PDF | Custom file order, bookmark retention, outline stitching |
| **PDF-002** | Split PDF | `pypdf` | Single PDF -> Multiple PDFs / ZIP | By page ranges, split by N pages, burst all pages |
| **PDF-003** | Compress PDF | `Ghostscript` / `qpdf` | Single PDF -> Optimized PDF | Quality presets (screen, ebook, printer, prepress), DPI reduction |
| **PDF-004** | Rotate PDF | `PyMuPDF` | Single PDF -> Rotated PDF | 90°, 180°, 270°, selective page filtering (all, even, odd, range) |
| **PDF-005** | Organize PDF | `PyMuPDF` | Single PDF -> Reordered PDF | Visual page reordering, page rotation, deletion, duplication |
| **PDF-006** | Extract Pages | `pypdf` | Single PDF -> Extracted PDF | Extract custom ranges (e.g., `1,3-5,8`), merge into one or zip |
| **PDF-007** | Delete Pages | `pypdf` | Single PDF -> Cleaned PDF | Selectively strip page numbers or custom sets |
| **PDF-008** | Duplicate Pages| `pypdf` | Single PDF -> Extended PDF | Repeat specific pages N times in sequence |
| **PDF-009** | Reverse Pages | `pypdf` | Single PDF -> Inverted PDF | Inverts reading order (last page to first page) |
| **PDF-010** | Crop PDF | `PyMuPDF` | Single PDF -> Cropped PDF | Crop box coordinates (margins in pt/mm), apply to all or selected |
| **PDF-011** | Repair PDF | `qpdf` | Corrupted PDF -> Repaired PDF | Reconstruct corrupted XRef tables and fix stream lengths |
| **PDF-012** | Flatten PDF | `PyMuPDF` | PDF with Forms -> Flat PDF | Bakes interactive form fields, annotations, and layers into page stream |
| **PDF-013** | Compare PDF | `PyMuPDF` / `Pillow` | 2 PDFs -> Visual Diff PDF / Report | Side-by-side visual diff, highlight pixel and text alterations |
| **PDF-014** | OCR PDF | `OCRmyPDF` / `Tesseract` | Scanned PDF -> Searchable PDF | Multilingual OCR, deskew, clean background, searchable text layer |
| **PDF-015** | PDF to Images | `PyMuPDF` | Single PDF -> JPG/PNG/WebP (ZIP) | Custom DPI (72-600), image format, transparency support |
| **PDF-016** | Images to PDF | `Pillow` / `PyMuPDF` | Multiple Images -> Single PDF | Page orientation (Auto, Portrait, Landscape), margins, page size |
| **PDF-017** | Page Numbering | `PyMuPDF` | Single PDF -> Numbered PDF | Position (6 anchors), font style, size, prefix/suffix, offset |
| **PDF-018** | Watermark PDF | `PyMuPDF` | Single PDF -> Watermarked PDF | Text or Image stamp, opacity, rotation angle, layer (over/under) |
| **PDF-019** | Header & Footer| `PyMuPDF` | Single PDF -> Branded PDF | Left, center, right text slots with dynamic tokens (`{page}`, `{date}`) |
| **PDF-020** | Metadata Editor| `PyMuPDF` | Single PDF -> Updated PDF | View/modify Title, Author, Subject, Keywords, Creator, Producer |
| **PDF-021** | PDF Info/Inspect| `PyMuPDF` / `qpdf` | Single PDF -> JSON Report | Page count, dimensions, PDF version, security, fonts, color spaces |
| **PDF-022** | Add Bookmarks | `PyMuPDF` | Single PDF -> Bookmarked PDF | Generate hierarchical Table of Contents (TOC) with destination links |
| **PDF-023** | Remove Blank Pgs| `PyMuPDF` | Single PDF -> Compact PDF | Threshold-based blank page detection (ink density & whitespace) |
| **PDF-024** | Deduplicate Pgs| `PyMuPDF` + `ImageHash` | Single PDF -> Deduplicated PDF | Perceptual hashing (pHash) to identify identical consecutive slides |
| **PDF-025** | Extract Attach | `PyMuPDF` | Single PDF -> ZIP of attachments | Extract embedded file attachments |
| **PDF-026** | Extract Images | `PyMuPDF` | Single PDF -> Images ZIP | Lossless extraction of embedded raster images |
| **PDF-027** | Extract Fonts | Specialized PDF tools | Single PDF -> Fonts archive | Extract embedded TrueType / OpenType font objects |
| **PDF-028** | Linearize PDF | `qpdf` | Single PDF -> Linearized PDF | Fast Web View optimization for progressive streaming |
| **PDF-029** | PDF/A Convert | `Ghostscript` | Standard PDF -> PDF/A-1b/2b/3b | Long-term archival compliance, color profile embedding |
| **PDF-030** | PDF/X Convert | Prepress tooling | Standard PDF -> PDF/X-1a/3/4 | Prepress graphic arts compliance (CMYK, bounding boxes) |
| **PDF-031** | PDF Portfolio | PyMuPDF / Struct | Multiple files -> Portfolio PDF | Package heterogeneous documents in a standardized container |
| **PDF-032** | Object Inspect | `PyMuPDF` / `qpdf` | Single PDF -> Tree JSON | Low-level COS object browser and stream decompressor |
| **PDF-033** | Strip Annotations| `PyMuPDF` | Single PDF -> Cleaned PDF | Remove highlights, comments, freehand drawings, sticky notes |
| **PDF-034** | Strip JavaScript| `qpdf` / `PyMuPDF` | Potentially unsafe PDF -> Safe PDF | Sanitizes document by removing `/JavaScript`, `/JS`, `/Launch` actions |
| **PDF-035** | Strip Multimedia| `PyMuPDF` | Heavy PDF -> Lightweight PDF | Removes embedded Flash, audio, and video streams |
| **PDF-036** | Page Templates | `PyMuPDF` | Single PDF -> Templated PDF | Apply grid, margins, letterhead templates across document |
| **PDF-037** | Add Attachments| `PyMuPDF` | PDF + Files -> Hybrid PDF | Embed arbitrary files (XML, data sheets) into PDF catalogue |
| **PDF-038** | Strip Attachments| `PyMuPDF` | Hybrid PDF -> Clean PDF | Remove all embedded non-page attachments |
| **PDF-039** | Convert Dimensions| `PyMuPDF` | Single PDF -> Scaled PDF | Resize pages (e.g. Letter to A4, A3 to A4) maintaining aspect ratio |
| **PDF-040** | Version Inspect| `qpdf` | Single PDF -> Metadata | Detect PDF specification version (1.0 through 2.0) & conformance |

---

### 4.2 Module 2: Conversion Engine & Compatibility Matrix

#### Supported Conversion Pathways

```
[Inbound Office/Text Formats]                   [Intermediate Engines]                  [Outbound Deliverables]
DOC / DOCX --------------------------------+                                          +--> PDF
XLS / XLSX --------------------------------+                                          +--> DOCX
PPT / PPTX --------------------------------+                                          +--> XLSX
ODT / ODS / ODP ---------------------------+---> [ LibreOffice Headless Engine ] ----+--> PPTX
RTF / TXT / Markdown / HTML / CSV ---------+                                          +--> HTML / TXT
                                                                                       +--> Images (JPG/PNG)

[Inbound Images]                                [Raster & Vector Engines]
JPG / PNG / WebP / TIFF / SVG -------------+---> [ Pillow / PyMuPDF / Cairo ] --------+--> PDF / Multi-page PDF
```

#### Conversion Rules:
1. **Office to PDF:** Uses headless LibreOffice running in sandboxed container instances with strict memory capping.
2. **PDF to Office:** 
   - PDF to DOCX: Uses `pdf2docx` layout-preserving reconstruction engine (extracting tables, paragraphs, text styles).
   - PDF to XLSX: Uses structured table extraction (`pdfplumber` / layout analysis) to produce authentic worksheets.
3. **Markdown / Text to PDF / DOCX:** Uses `pandoc` / `weasyprint` for styled typography.
4. **Data Transformations:** Bi-directional converters between CSV, XLSX, JSON, XML.

---

### 4.3 Module 3: Advanced Compression Subsystem
* **Absolute Size-Invariance Guarantee:** The compression engine guarantees that output files are NEVER larger than the input file (`compressed_size <= original_size`). If a PDF is already optimally packed or contains uncompressible vector streams, the engine safely preserves the original without bloated re-serialization and reports `0.0%` reduction.
* **Lossless Compression:** Re-compressing uncompressed object streams, deduplicating font subsets, removing redundant structural metadata via `qpdf --linearize --object-streams=generate`.
* **Standard / Balanced Compression:** Downsampling images to 150 DPI, applying JPEG compression with quality factor 70, stripping thumbnail dictionaries.
* **Extreme Compression:** Aggressive downsampling to 72 DPI, JPEG quality factor 35, converting colored figures to grayscale (optional toggle).
* **Metrics Tracked per Job:**
  - `original_size_bytes`, `compressed_size_bytes`
  - `reduction_percentage` ($1 - \frac{\text{compressed}}{\text{original}}$)
  - `images_recompressed`, `execution_duration_ms`
  - Applied profile name & parameter manifest

---

### 4.4 Module 4: PDF Visual Editor & Interactive Canvas
* **In-Browser Rendering:** High-performance viewing utilizing `PDF.js` with client-side zoom, pan, and virtualized page rendering.
* **Annotation Layer:** Fabric.js / SVG overlay for:
  - Freehand drawing and pen highlights.
  - Text box insertion with font selection, color pickers, and bounding box alignment.
  - Image stamping (logos, stamps, initials).
  - Shape tools (rectangles, ellipses, callout arrows, lines).
* **Form Filling & Flattening:** Detect interactive AcroForm widgets, accept user input in native browser inputs, and compile back into document streams.
* **Redaction Tool:** True destruction of underlying vector content and text runs within user-selected bounding boxes (not simply black overlays).

---

### 4.5 Module 5: Security, Digital Signatures & Encryption
* **Encryption & Password Protection:** Standard PDF 128-bit / 256-bit AES encryption with separate Owner (administrative) and User (read) passwords.
* **Authorized Password Removal:** Decrypt protected files when valid password is supplied.
* **Granular Permissions:** Restrict printing (low-res vs high-res), content copying, annotation modifications, and form field filling.
* **Digital Signatures:**
  - Visible signature placement (visual autograph / seal).
  - Cryptographic validation of existing signatures (reporting signer identity, timestamp validity, and document tamper check).
  - Explicit notification that editing a cryptographically signed document invalidates existing seals.

---

### 4.6 Module 6: OCR & Document Intelligence
* **Full-Page OCR:** Scan-to-searchable-PDF conversion via `OCRmyPDF` using `Tesseract 5`.
* **Table Extraction:** Automated detection of table borders and whitespace grids, serializing extracted data directly to Excel (.xlsx) and CSV.
* **Structured Data Extraction:** Invoice and receipt key-value pair parsing (Vendor, Date, Invoice Number, Subtotal, Tax, Total Amount).
* **Semantic Document Comparison:** Textual diff tool that extracts normalized text streams and generates a redline comparison report highlighting additions, deletions, and displacements.

---

### 4.7 Module 7: Image Studio & Web Dev Utilities
* **Image to Favicon & Web App Manifest Studio:** Complete multi-asset generator for web developers:
  - Multi-resolution `favicon.ico` (16x16, 32x32, 48x48)
  - PNG Favicons: `favicon-16x16.png`, `favicon-32x32.png`
  - Apple Touch Icon: `apple-touch-icon.png` (180x180)
  - Android Chrome / PWA Icons: `android-chrome-192x192.png`, `android-chrome-512x512.png`
  - Manifest & Code: `site.webmanifest` and copy-pasteable HTML `<head>` link tags (`favicon_tags.html`)
  - Packaged deployable `favicon_bundle.zip`
* **Format Conversions:** Seamless interchange between JPG, PNG, WebP, TIFF, SVG, and BMP.
* **Transformations:** Non-destructive image cropping, free rotation, vertical/horizontal flipping, and aspect-ratio scaling.
* **Metadata Management:** Read, extract, and completely strip sensitive EXIF data (GPS coordinates, camera serials, timestamps).
* **Barcodes & QR Codes:** Generate high-resolution vector and raster QR codes, plus reading/decoding embedded barcodes from uploaded images.

---

### 4.8 Module 8: Batch Processing Engine
* Multi-file drag-and-drop supporting up to 20 files per operation for authenticated users.
* Parallel job dispatch with per-item status indicators (Queued, Running, Succeeded, Failed).
* Failure isolation: A corrupt file in item #3 does not terminate or abort items #4 through #20.
* One-click bulk download packaging all outputs into an organized `.zip` archive.

---

### 4.9 Module 9: Cloud Workspace & File Management
* **Virtual Folder Hierarchy:** Intuitive folder tree navigation with move, rename, duplicate, and nesting capabilities.
* **Document Versioning:** Maintain version history for documents transformed multiple times within the workspace.
* **Soft Deletion & Recovery:** 30-day Trash bin retention with one-click restore and permanent purge actions.
* **Full-Text & Tag Search:** Instant indexing of file names, tags, page counts, and extracted OCR text.

---

### 4.10 Module 10: Document Sharing & Secure Public Links
* Generate opaque, cryptographically random share URLs (`/s/{share_token}`).
* Database stores only the SHA-256 hash of the token (`token_hash`).
* Granular share options:
  - Expiration timestamp (e.g. 1 hour, 1 day, 7 days, never).
  - Optional access password protection (bcrypt hashed).
  - Maximum download count limits.
  - Direct download vs browser-view-only mode.

---

### 4.11 Module 11: Dynamic Tool Registry
Instead of hardcoding tool metadata across both frontend and backend, the platform is driven by a unified **Tool Registry** (`packages/tool-registry` and database table `tool_registry`):
* Every tool has a unique slug (e.g., `merge-pdf`, `compress-pdf`), category, display name, description, icon identifier, input constraints, supported extensions, and execution handler mapping.
* Features can be dynamically enabled/disabled in real-time by administrators without redeploying code.

---

## 5. Database Architecture & Schema Specification

The database utilizes **PostgreSQL 16+** with UUID primary keys, UTC timestamps, JSONB configurations, and soft-delete conventions.

### 5.1 Entity Relationship Diagram (ERD)

```
       +--------------------+                +--------------------+
       |       USERS        | 1            * |     WORKSPACES     |
       |--------------------|----------------|--------------------|
       | id (UUID) [PK]     |                | id (UUID) [PK]     |
       | email (VARCHAR)    |                | owner_id (UUID)[FK]|
       | password_hash (STR)|                | name (VARCHAR)     |
       | status (VARCHAR)   |                | storage_limit (BIG)|
       +---------+----------+                +---------+----------+
                 | 1                                   | 1
                 |                                     |
                 | *                                   | *
       +---------v----------+                +---------v----------+
       |  PROCESSING_JOBS   | *            1 |       FILES        |
       |--------------------|----------------|--------------------|
       | id (UUID) [PK]     |                | id (UUID) [PK]     |
       | user_id (UUID) [FK]|                | workspace_id [FK]  |
       | operation (VARCHAR)|                | folder_id (UUID)   |
       | status (VARCHAR)   |                | original_name (STR)|
       | progress (INT)     |                | storage_key (TEXT) |
       | options (JSONB)    |                | checksum_sha256    |
       +---------+----------+                +---------+----------+
                 | 1                                   | 1
                 |                                     |
                 | *                                   | *
       +---------v----------+                +---------v----------+
       |     JOB_FILES      |                |    SHARED_LINKS    |
       |--------------------|                |--------------------|
       | id (UUID) [PK]     |                | id (UUID) [PK]     |
       | job_id (UUID) [FK] |                | file_id (UUID) [FK]|
       | file_id (UUID) [FK]|                | token_hash (STR)   |
       | role (input/output)|                | expires_at (TIME)  |
       +--------------------+                +--------------------+
```

### 5.2 Table Schemas

#### A. Identity & Access (`users`, `user_sessions`)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'USER', -- SUPER_ADMIN, ADMIN, MODERATOR, USER
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, SUSPENDED, PENDING_VERIFICATION
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token_hash VARCHAR(64) NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### B. Workspace & File Metadata (`workspaces`, `folders`, `files`)
```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    storage_limit_bytes BIGINT NOT NULL DEFAULT 2147483648, -- 2 GB
    storage_used_bytes BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES folders(id) ON DELETE SET NULL,
    original_name VARCHAR(255) NOT NULL,
    stored_name VARCHAR(255) NOT NULL,
    storage_key TEXT NOT NULL UNIQUE,
    mime_type VARCHAR(150) NOT NULL,
    extension VARCHAR(20) NOT NULL,
    size_bytes BIGINT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    page_count INTEGER,
    width INTEGER,
    height INTEGER,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    is_starred BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_files_workspace ON files(workspace_id);
CREATE INDEX idx_files_owner ON files(owner_id);
CREATE INDEX idx_files_folder ON files(folder_id);
CREATE INDEX idx_files_checksum ON files(checksum_sha256);
CREATE INDEX idx_files_status_deleted ON files(status, is_deleted);
```

#### C. Processing & Jobs (`processing_jobs`, `job_files`, `job_events`)
```sql
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    operation VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'QUEUED', -- QUEUED, PROCESSING, VALIDATING, COMPLETED, FAILED, CANCELLED
    progress INTEGER NOT NULL DEFAULT 0,
    stage_message VARCHAR(255) DEFAULT 'Job queued',
    options JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT,
    celery_task_id VARCHAR(255),
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE job_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'input' or 'output'
    sequence_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE job_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    progress INTEGER NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_jobs_user ON processing_jobs(user_id);
CREATE INDEX idx_jobs_status ON processing_jobs(status);
```

#### D. Document Sharing (`shared_links`, `shared_link_access`)
```sql
CREATE TABLE shared_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    allow_download BOOLEAN NOT NULL DEFAULT TRUE,
    max_downloads INTEGER,
    download_count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 6. API Architecture & Endpoint Specifications

**Base URL:** `https://api.pdfpride.com/api/v1`  
All standard requests consume and return `application/json`. Authenticated endpoints utilize secure HTTP-only session cookies.

### 6.1 Authentication Endpoints
* `POST /auth/register` - Create account with email, password.
* `POST /auth/login` - Authenticate credentials, set HttpOnly session cookie.
* `POST /auth/logout` - Invalidate active session token.
* `GET /auth/me` - Retrieve current authenticated profile and quota status.
* `POST /auth/forgot-password` - Trigger password recovery token.
* `POST /auth/reset-password` - Complete password reset.

### 6.2 File & Storage Endpoints
* `POST /files/upload/init` - Request upload authorization / pre-signed S3 URL.
* `POST /files/upload/direct` - Direct multipart file upload (fallback / dev mode).
* `GET /files` - Paginated workspace files listing with filters (`folder_id`, `mime_type`, `starred`).
* `GET /files/{id}` - File metadata object.
* `GET /files/{id}/download` - Stream binary or return short-lived signed S3 download URL.
* `GET /files/{id}/preview` - Stream web-optimized preview image/PDF.
* `DELETE /files/{id}` - Soft-delete file into Trash.
* `POST /files/{id}/restore` - Restore file from Trash.

### 6.3 Tool Processing Endpoints (Unified Job Dispatch Pattern)
All transformation endpoints accept input file IDs and options, immediately returning a `202 Accepted` response with the job representation.

* `POST /pdf/merge` - Merge multiple input PDFs according to `file_order`.
* `POST /pdf/split` - Split PDF via mode (`ranges`, `pages_per_file`, `all`).
* `POST /pdf/compress` - Compress with profile (`low`, `balanced`, `high`, `extreme`, `custom`).
* `POST /pdf/rotate` - Rotate pages (`angle`, `page_filter`).
* `POST /pdf/organize` - Reorder, delete, and rotate pages based on structural map.
* `POST /pdf/watermark` - Apply text or image stamp with opacity, angle, positioning.
* `POST /pdf/page-numbers` - Overlay dynamic page numbers.
* `POST /pdf/protect` - Encrypt with user/owner password and permission bitmask.
* `POST /pdf/unlock` - Decrypt protected document with password.
* `POST /conversions` - Cross-format conversion (e.g. `docx` -> `pdf`, `pdf` -> `docx`).
* `POST /ocr` - Execute OCR pipeline on scanned document.
* `POST /images/convert` - Convert and compress raster images.

### 6.4 Job Polling & Event Stream
* `GET /jobs/{id}` - Fetch live job status, progress percentage (0-100), stage message, and output file metadata once completed.
* `POST /jobs/{id}/cancel` - Cancel a queued or active processing job.
* `GET /jobs/{id}/events` - Server-Sent Events (SSE) or polling endpoint for real-time progress updates.

---

## 7. Frontend User Experience Architecture

### 7.1 Design System & Aesthetic Principles (Anti-AI, Swiss Precision)
* **Design Philosophy:** Avoid generic "AI-generated" templates (no soft gradient blobs, no floating purple bubbles, no pale washed-out pastels). The interface embraces **Swiss International Style / High-End Industrial Precision** with an authoritative, commercial-grade premium feel.
* **Geometry:** **Zero Curved Radiuses.** All cards, inputs, dropzones, progress bars, and modal containers use flat boxes with sharp 90-degree right angles (`border-radius: 0px`).
* **Color Palette:** Strictly major, definitive, bold colors. Zero gradients:
  - **Major Black:** Absolute Jet Black (`#000000`) for authoritative structural borders, primary headings, and buttons.
  - **Major White:** Stark Optical White (`#FFFFFF`) for crisp high-contrast backgrounds.
  - **Major Red:** Bold Crimson (`#D00000`) for primary action highlights, warnings, and brand accents.
  - **Major Blue:** Cobalt Ultramarine (`#0038FF`) for status indicators and active progress states.
  - **Major Surface:** Precision Neutral (`#F4F4F5` / `#18181B`) for flat containers and table headers.
* **Iconography:** **FontAwesome (FA 6 Solid)** icon pack across all client navigation, tool identifiers, and actions.
* **Component Primitives:** Flat rectangular containers with 2px solid black borders, flat geometric shadows (`4px 4px 0px #000000`), and monospace uppercase tracking for technical metadata.
* **State & Data Fetching:** TanStack Query v5 with optimistic updates and automatic polling for active job IDs.

### 7.2 Core Application Navigation Structure
```
PDF Pride Platform
├── Public Marketing & Tool Gateway
│   ├── / (Hero, Feature Grid, Quick Action Dropzone)
│   ├── /tools (Categorized Catalogue of all 80+ operations)
│   ├── /tools/[slug] (Dynamic Universal Tool Runner page)
│   ├── /converters (Format Conversion Directory)
│   └── /pricing (Tiers, limits, commercial plans)
├── Authenticated Cloud Workspace
│   ├── /workspace (Overview, recent activity, storage usage bar)
│   ├── /workspace/files (Interactive File Manager, grid/list view)
│   ├── /workspace/folders/[id] (Nested folder views)
│   ├── /workspace/history (Searchable log of previous processing jobs)
│   └── /workspace/shared (Active share links management)
└── System Governance
    └── /admin (Metrics, queue latency, user management, tool toggles)
```

### 7.3 Reusable Universal Tool Runner Framework
Every single tool page (`/tools/[slug]`) implements a standardized, high-conversion, intuitive 4-step UX pattern:
1. **Dropzone & File Picker:** Drag-and-drop supporting multi-file selection, format validation, and client-side page previews.
2. **Interactive Configuration Panel:** Tool-specific options (e.g., compression sliders, rotation handles, watermark text, page selector thumbnails).
3. **Action & Live Progress Bar:** One-click CTA ("Process PDF Now"), transitioning immediately into an animated progress bar indicating real server stages ("Uploading", "Optimizing streams", "Validating output").
4. **Completion & Action Hub:** Visual before/after file size comparison, instant "Download Result" button, "Save to My Workspace" button, and contextual next-step recommendations (e.g. "Now compress your merged PDF").

---

## 8. Non-Functional & Security Requirements

### 8.1 Security & File Sandboxing
* **Untrusted Input Isolation:** Processing workers operate in unprivileged execution environments with restricted file-system read access, strictly bounded memory (`RLIMIT_AS`), and execution timeouts (`SIGKILL` after 120s max).
* **Malicious File Mitigation:**
  - Strict magic byte file header sniffing (rejecting executable binaries disguised with `.pdf` extensions).
  - Decompression bomb detection (limiting maximum uncompressed raster image buffers and zip expansion ratios to 1:100 max).
  - Sanitization of PDF streams to strip `/JavaScript`, `/Launch`, and `/EmbeddedFiles` with unknown mime-types unless explicitly preserved.
* **Network Egress Block:** Worker processes performing PDF rendering and conversions have outbound internet access blocked via container network namespaces to prevent SSRF and data exfiltration.

### 8.2 Performance & Scalability Targets
* **P95 Latency for Standard PDF Operations:**
  - Merge (up to 50 pages): < 1.5 seconds.
  - Split / Extract: < 800 ms.
  - Standard Compression: < 3.0 seconds.
* **Throughput:** Monolith API capable of handling 500 req/sec; worker pools auto-scale based on Redis queue depth (`celery_queue_length > 20`).
* **Storage Optimization:** Pre-signed S3 direct uploads bypass backend API servers, preventing memory bottlenecks on large file transfers.

---

## 9. Phased Implementation Roadmap

```
Phase 1: Foundation & Monorepo Scaffold (Milestone 01)
├── Docker Compose, FastAPI, Next.js, Redis, PostgreSQL
└── Core Engine: Merge, Split, Compress, JPG<->PDF

Phase 2: Authentication & Cloud Workspace
├── Session Auth, S3 Storage Abstraction, File Manager
└── Folder Trees, Soft Deletion, SHA-256 Checksumming

Phase 3: Extended PDF Suite (PDF-001 through PDF-020)
├── Organize, Rotate, Crop, Page Numbers, Watermarks
└── Repair, Metadata, Flatten, Bookmarks

Phase 4: Office & Multi-Format Conversion Engine
├── LibreOffice Worker integration (DOCX, XLSX, PPTX to PDF)
└── PDF to Word/Excel extraction pipelines

Phase 5: Visual PDF Editor & Annotation Canvas
├── PDF.js interactive client, Fabric.js annotation layer
└── AcroForm filling, form flattening, true redaction

Phase 6: OCR, Image Studio & Document Intelligence
├── Tesseract / OCRmyPDF pipelines, table extraction
└── Image format transformations, EXIF scrubbers, QR generation

Phase 7: Public Sharing, Quotas & Platform Hardening
├── Opaque token sharing, password-protected links
└── Granular rate limiting, guest quotas, security sandbox

Phase 8: Admin Dashboard, Analytics & SaaS Readiness
├── Operational metrics, tool registry toggles, queue metrics
└── Subscription schema readiness and commercial launch
```

---

## 10. Acceptance Criteria & QA Strategy

Every released tool must pass automated test suites asserting:
1. **Output Structural Validity:** Merged/split/compressed files must pass `qpdf --check` with zero syntax errors.
2. **Page Count Invariance:** Merging a 5-page PDF and a 7-page PDF must deterministically yield a 12-page PDF.
3. **Visual Fidelity:** Text rendering and layout must not degrade unexpectedly during compression or conversion.
4. **Error Resiliency:** Corrupted files, password-locked files without passwords, or zero-byte payloads must trigger clear, user-friendly error codes (`CORRUPTED_DOCUMENT`, `PASSWORD_REQUIRED`, `UNSUPPORTED_FORMAT`) rather than unhandled 500 server crashes.
5. **No Data Leakage:** Temporary processing artifacts in scratch volumes must be guaranteed wiped after job termination.
