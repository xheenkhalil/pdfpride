import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult

class PDFProtectEngine(BaseEngine):
    """PDF-116 & 118: Encrypts PDF with 256-bit AES password protection."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"protected_{src.name}"
        raw_pw = options.get("password")
        password = raw_pw if isinstance(raw_pw, str) and raw_pw else "pdfpride_secure"
        # PyMuPDF max password length constraint is 32-40 chars
        password = password[:32]

        doc = fitz.open(src)
        # AES-256 encryption
        perm = int(
            fitz.PDF_PERM_ACCESSIBILITY |
            fitz.PDF_PERM_PRINT |
            fitz.PDF_PERM_COPY
        )
        doc.save(
            str(out_path),
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw=password,
            user_pw=password,
            permissions=perm,
        )
        doc.close()
        return EngineResult(output_paths=[out_path], metrics={"encrypted": True, "algorithm": "AES-256"})


class PDFUnlockEngine(BaseEngine):
    """PDF-117 & 120: Authorized password removal from encrypted PDF."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"unlocked_{src.name}"
        password = str(options.get("password") or "")

        doc = fitz.open(src)
        if doc.is_encrypted:
            auth_success = doc.authenticate(password)
            if not auth_success and password:
                # Try common password or blank
                auth_success = doc.authenticate("")
            if not auth_success:
                raise ValueError("Incorrect password provided for encrypted PDF.")

        # Save without encryption
        doc.save(str(out_path), encryption=fitz.PDF_ENCRYPT_NONE, garbage=4, deflate=True)
        doc.close()
        return EngineResult(output_paths=[out_path], metrics={"unlocked": True})


class PDFRedactEngine(BaseEngine):
    """PDF-129: True permanent redaction of text and content runs."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"redacted_{src.name}"
        search_term = options.get("term", "")

        doc = fitz.open(src)
        for page in doc:
            if search_term:
                rects = page.search_for(search_term)
                for r in rects:
                    page.add_redact_annot(r, fill=(0, 0, 0))
            else:
                # Default sample redaction: redact upper margin
                rect = fitz.Rect(50, 50, 300, 75)
                page.add_redact_annot(rect, fill=(0, 0, 0))
            page.apply_redactions()

        doc.save(str(out_path), garbage=4, deflate=True)
        doc.close()
        return EngineResult(output_paths=[out_path], metrics={"redacted": True})


class PDFWatermarkEngine(BaseEngine):
    """PDF-102: Applies text or stamp watermark across all pages."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"watermarked_{src.name}"
        raw_text = options.get("text")
        text = raw_text if isinstance(raw_text, str) and raw_text else "CONFIDENTIAL"

        doc = fitz.open(src)
        for page in doc:
            p_rect = page.rect
            cx = p_rect.width / 2
            cy = p_rect.height / 2
            # PyMuPDF insert_text rotate must be 0, 90, 180, or 270
            page.insert_text(
                (cx - 100, cy),
                text,
                fontsize=36,
                fontname="helv",
                color=(0.8, 0.1, 0.1),
                rotate=0,
            )

        doc.save(str(out_path), garbage=4, deflate=True)
        doc.close()
        return EngineResult(output_paths=[out_path], metrics={"watermarked": True, "text": text})


class PDFPageNumbersEngine(BaseEngine):
    """PDF-104: Injects dynamic page numbering into document."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"numbered_{src.name}"
        total_pages = 0

        doc = fitz.open(src)
        total_pages = len(doc)
        for idx, page in enumerate(doc):
            p_rect = page.rect
            num_str = f"Page {idx + 1} of {total_pages}"
            page.insert_text(
                (p_rect.width / 2 - 40, p_rect.height - 30),
                num_str,
                fontsize=10,
                fontname="helv",
                color=(0.3, 0.3, 0.3),
            )

        doc.save(str(out_path), garbage=4, deflate=True)
        doc.close()
        return EngineResult(output_paths=[out_path], metrics={"numbered": True, "total_pages": total_pages})


class PDFRotateEngine(BaseEngine):
    """
    PDF-004 & PDF-299: Rotates PDF pages across all 4 rotation cycles:
    - Right (90° Clockwise)
    - Left (90° Counter-Clockwise / 270°)
    - Flip Upside-Down (180°)
    - Reset (0°)
    Supports page selection: All pages, Odd pages, Even pages, or Custom page range.
    """
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided.")
        src = input_paths[0]
        out_path = output_dir / f"rotated_{src.name}"

        # 1. Determine rotation cycle
        rot_type = str(options.get("rotation_type") or options.get("direction") or "").lower()
        reset = False
        if rot_type in ("left_90", "left", "270", "ccw"):
            angle = 270
        elif rot_type in ("flip_180", "180", "flip"):
            angle = 180
        elif rot_type in ("reset_0", "0", "reset"):
            angle = 0
            reset = True
        else: # default: right_90 / 90 / cw
            raw_angle = options.get("angle") or options.get("degrees") or 90
            try:
                angle = int(raw_angle)
            except Exception:
                angle = 90
            reset = (angle == 0)

        # 2. Determine target pages
        page_sel = str(options.get("page_selection", "all")).lower()
        custom_range = str(options.get("page_range", ""))

        doc = fitz.open(src)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF document has 0 pages.")

        if page_sel == "odd":
            target_indices = set(range(0, total_pages, 2))
        elif page_sel == "even":
            target_indices = set(range(1, total_pages, 2))
        elif page_sel == "custom" and custom_range:
            from apps.api.app.engines.pdf.page_ops import parse_page_spec
            target_indices = set(parse_page_spec(custom_range, total_pages))
        else:
            target_indices = set(range(total_pages))

        for idx, page in enumerate(doc):
            if idx in target_indices:
                if reset:
                    page.set_rotation(0)
                else:
                    page.set_rotation((page.rotation + angle) % 360)

        doc.save(str(out_path), garbage=4, deflate=True)
        doc.close()
        return EngineResult(
            output_paths=[out_path],
            metrics={
                "angle": angle,
                "rotated_pages_count": len(target_indices),
                "total_pages": total_pages,
                "rotation_type": rot_type or f"{angle}deg"
            }
        )


class PDFMetadataEngine(BaseEngine):
    """PDF-020: Modifies PDF Title, Author, Subject metadata."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"meta_{src.name}"

        doc = fitz.open(src)
        meta = doc.metadata
        if isinstance(options.get("title"), str):
            meta["title"] = options["title"]
        if isinstance(options.get("author"), str):
            meta["author"] = options["author"]
        meta["producer"] = "PDF Pride Platform Engine"
        doc.set_metadata(meta)

        doc.save(str(out_path), garbage=4, deflate=True)
        doc.close()
        return EngineResult(output_paths=[out_path], metrics={"metadata": meta})


class PDFInfoEngine(BaseEngine):
    """PDF-018, 019, 027: Inspects and exports PDF metadata and properties."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}_info.json"

        import json
        doc = fitz.open(src)
        info = {
            "filename": src.name,
            "page_count": len(doc),
            "metadata": doc.metadata,
            "is_encrypted": doc.is_encrypted,
            "is_pdf": getattr(doc, "is_pdf", True),
            "format": "PDF",
        }
        doc.close()

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)

        return EngineResult(output_paths=[out_path], metrics=info)
