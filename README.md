# PDF Pride (Document Studio)

> **Enterprise-Grade Cloud Document Processing Platform**  
> *All your document tools in one place.*

---

## 1. Architectural Demarcation: Client vs. Server

PDF Pride is engineered with a strict **Zero-Trust Boundary** separating the presentation surface from authoritative server operations.

```
+-------------------------------------------------------------------------------+
|                        CLIENT BOUNDARY (apps/web)                             |
|                                                                               |
|   Platform: Next.js 14+ (App Router), React 18, TypeScript, Tailwind CSS      |
|   Role: Presentation & User Interaction                                      |
|   - Universal Tool Runner dynamically rendered from Tool Registry.            |
|   - In-browser interactive preview & visual page reordering (PDF.js).         |
|   - File upload streaming via short-lived signed URLs.                        |
|   - Real-time job polling & optimistic feedback.                              |
|   * ZERO database access, ZERO master S3 secrets, ZERO document tampering.   |
+-------------------------------------------------------------------------------+
                                       |
                   HTTPS / TLS 1.3     |  Strict REST v1 JSON Contract
                   HttpOnly Cookies    |  Pre-signed S3 Binaries
                                       v
+-------------------------------------------------------------------------------+
|                        SERVER BOUNDARY (apps/api)                             |
|                                                                               |
|   Platform: FastAPI, Celery, SQLAlchemy 2.0 Async, PostgreSQL 16, Redis 7     |
|   Role: Authoritative Business Logic & Compute Workers                        |
|   - Authentication, session verification, and user quota management.          |
|   - Input Gatekeeper: Magic-byte inspection, SHA-256 integrity, bomb check.  |
|   - Distributed Worker Pools: PyMuPDF, pypdf, Ghostscript, Pillow, OpenCV.   |
|   - Sandboxed Execution: Restricted syscalls, no network egress, memory cap.  |
|   - Automatic Ephemeral Hygiene: Temporary working directories purged.        |
+-------------------------------------------------------------------------------+
```

---

## 2. Design Philosophy: Anti-AI & Swiss Precision

PDF Pride rejects generic AI-generated template styling (no gradient blobs, no floating purple bubbles, no pale pastels, no soft curved pills). Instead, it implements **Swiss Industrial Engineering Precision**:

* **Flat Boxes & Zero Curved Radius:** All cards, dropzones, inputs, progress tracks, and buttons feature strict 90-degree right angles (`border-radius: 0px`).
* **Major Colors Only (Zero Gradients):** High-contrast, bold, definitive palette:
  - **Major Black (`#000000`):** Authoritative structural outlines (2px / 4px borders) and typography.
  - **Major White (`#FFFFFF`):** High-contrast, optical background planes.
  - **Major Red (`#D00000`):** Primary action buttons, alerts, and brand emphasis.
  - **Major Blue (`#0038FF`):** Processing states and active indicators.
* **Iconography:** Standardized on **FontAwesome 6 Solid** (`FaFilePdf`, `FaLayerGroup`, `FaScissors`, `FaCompress`, `FaFolder`, etc.).
* **Tactile Flat Shadows:** `shadow-flat` (`4px 4px 0px 0px #000000`) for high-precision tactile feedback.

---

## 3. Monorepo Structure

```
pdfpride/
├── apps/
│   ├── api/                   # Server API & Worker Pool
│   │   ├── app/
│   │   │   ├── api/v1/        # Versioned endpoints (health, tools, files, jobs)
│   │   │   ├── core/          # Config, database engine, security
│   │   │   ├── engines/       # Pure Python document processing engines
│   │   │   │   ├── pdf/       # Merge, split, compress, rotate, organize
│   │   │   │   └── image/     # JPG<->PDF, PDF<->JPG converters
│   │   │   ├── models/        # SQLAlchemy 2.0 async database models
│   │   │   ├── schemas/       # Pydantic v2 schemas
│   │   │   ├── storage/       # Local filesystem & S3 storage abstraction
│   │   │   └── workers/       # Celery task definitions & dispatcher
│   │   ├── tests/             # Automated test suite (pytest)
│   │   └── requirements.txt
│   │
│   └── web/                   # Client Web Application
│       ├── src/
│       │   ├── app/           # Next.js 14 App Router pages
│       │   ├── components/    # UniversalToolRunner, Dropzone, ProgressBar
│       │   ├── lib/           # ApiClient wrapper
│       │   └── types/         # TypeScript definitions
│       └── package.json
│
├── packages/
│   └── tool-registry/         # Central dynamic tool catalog (tools.json)
│
├── docker-compose.yml         # Full local stack orchestrator
├── prd.md                     # Product Requirements Document
├── implementation.md          # Technical Implementation Specification
├── .env.example               # Environment variables template
└── README.md
```

---

## 3. Quickstart Guide (Local Development)

### Option A: Complete Docker Compose Stack (Recommended)
Clone the repository and launch the full environment (Postgres, Redis, API Server, Celery Worker, Next.js Web Client):

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Build and launch all services
docker compose up --build
```

Access the applications:
* **Frontend Web Client:** [http://localhost:3000](http://localhost:3000)
* **Backend Server API Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
* **API Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Option B: Local Standalone Development

#### 1. Backend API Server (`apps/api`)
```bash
cd apps/api
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn apps.api.app.main:app --reload --port 8000
```

#### 2. Frontend Web Client (`apps/web`)
```bash
cd apps/web
npm install
npm run dev
```

---

## 4. Automated Testing

Verify the server transformation engines and integrity assertions:

```bash
cd apps/api
pytest tests/ -v
```

Tests cover:
* Multi-file sequential PDF Merging
* Page Range and Burst PDF Splitting
* Stream Deflation & PDF Compression
* Bi-directional JPG <-> PDF conversions

---

## 5. Security & Verification Acceptance Checklist
* [x] **No Master Credentials on Client:** S3 keys and DB secrets exist strictly within server runtime.
* [x] **Magic Byte Sniffing:** Disallow arbitrary executables disguised as PDFs.
* [x] **Ephemeral Cleanup:** Scratch directories wiped after completion.
* [x] **Deterministic Operation:** Zero artificial mock conversions.
