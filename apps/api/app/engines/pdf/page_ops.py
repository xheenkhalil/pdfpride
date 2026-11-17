import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional, Set
from apps.api.app.engines.base import BaseEngine, EngineResult

def parse_page_spec(spec_str: str, total_pages: int) -> List[int]:
    """
    Parses human page specifications into 0-based page index list.
    Supports:
    - 'all'
    - 'odd' (1, 3, 5...)
    - 'even' (2, 4, 6...)
    - 'last'
    - '1, 3-5, 8'
    """
    if not spec_str or spec_str.strip().lower() == "all":
        return list(range(total_pages))

    s = spec_str.strip().lower()
    if s == "odd":
        return [p for p in range(total_pages) if (p + 1) % 2 != 0]
    if s == "even":
        return [p for p in range(total_pages) if (p + 1) % 2 == 0]

    result: List[int] = []
    seen: Set[int] = set()

    tokens = [t.strip() for t in s.split(",") if t.strip()]
    for token in tokens:
        if token == "last":
            if total_pages - 1 not in seen:
                seen.add(total_pages - 1)
                result.append(total_pages - 1)
        elif "-" in token:
            parts = token.split("-", 1)
            try:
                start_raw = parts[0].strip()
                end_raw = parts[1].strip()
                start = 1 if start_raw == "first" else max(1, int(start_raw))
                end = total_pages if end_raw == "last" else min(total_pages, int(end_raw))
                for p in range(start, end + 1):
                    idx = p - 1
                    if 0 <= idx < total_pages and idx not in seen:
                        seen.add(idx)
                        result.append(idx)
            except ValueError:
                continue
        else:
            try:
                p = int(token)
                idx = p - 1
                if 0 <= idx < total_pages and idx not in seen:
                    seen.add(idx)
                    result.append(idx)
            except ValueError:
                continue

    return result


class PDFDuplicateEngine(BaseEngine):
    """
    PDF-008: Duplicate PDF Pages.
    Duplicates all pages or selected pages with customizable copy counts and placement.
    """
    def execute(
        self,
        input_paths: List[Path],
        output_dir: Path,
        options: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided.")
        src = input_paths[0]
        out_path = output_dir / f"duplicated_{src.name}"

        raw_copies = options.get("copies", 2)
        try:
            copies = max(1, min(10, int(raw_copies)))
        except (ValueError, TypeError):
            copies = 2

        mode = str(options.get("duplicate_mode", "all")).lower()
        placement = str(options.get("placement", "consecutive")).lower()
        spec = str(options.get("page_range", "all"))

        if progress_callback:
            progress_callback(10, f"Loading PDF to duplicate (Copies: {copies}x, Mode: {mode})...")

        with fitz.open(src) as doc:
            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError("PDF document has 0 pages.")

            selected_pages = set(parse_page_spec(spec if mode != "all" else "all", total_pages))

            out_doc = fitz.open()

            if placement == "end":
                # First append all original pages
                for p in range(total_pages):
                    out_doc.insert_pdf(doc, from_page=p, to_page=p)
                # Then append duplicates at the end
                for _ in range(copies - 1):
                    for p in range(total_pages):
                        if p in selected_pages:
                            out_doc.insert_pdf(doc, from_page=p, to_page=p)
            else:
                # Consecutive placement: P1, P1, P2, P2...
                for p in range(total_pages):
                    count = copies if p in selected_pages else 1
                    for _ in range(count):
                        out_doc.insert_pdf(doc, from_page=p, to_page=p)

            if progress_callback:
                progress_callback(80, f"Saving duplicated document with {len(out_doc)} pages...")

            out_doc.save(str(out_path), garbage=4, deflate=True)
            new_total = len(out_doc)
            out_doc.close()

        if progress_callback:
            progress_callback(100, f"Successfully created duplicated PDF with {new_total} pages.")

        return EngineResult(
            output_paths=[out_path],
            metrics={"original_pages": total_pages, "resulting_pages": new_total, "copies": copies}
        )


class PDFReverseEngine(BaseEngine):
    """
    PDF-009: Reverse PDF Pages.
    Reverses the page order of a PDF (e.g., from 1..N to N..1).
    """
    def execute(
        self,
        input_paths: List[Path],
        output_dir: Path,
        options: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided.")
        src = input_paths[0]
        out_path = output_dir / f"reversed_{src.name}"

        if progress_callback:
            progress_callback(10, "Loading PDF for page reversal...")

        with fitz.open(src) as doc:
            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError("PDF document has 0 pages.")

            out_doc = fitz.open()
            # Iterate in reverse order
            for p in range(total_pages - 1, -1, -1):
                out_doc.insert_pdf(doc, from_page=p, to_page=p)

            if progress_callback:
                progress_callback(80, "Compressing and saving reversed PDF...")

            out_doc.save(str(out_path), garbage=4, deflate=True)
            out_doc.close()

        if progress_callback:
            progress_callback(100, f"Successfully reversed {total_pages} pages.")

        return EngineResult(
            output_paths=[out_path],
            metrics={"reversed_pages": total_pages}
        )


class PDFDeletePagesEngine(BaseEngine):
    """
    PDF-007: Delete PDF Pages.
    Removes specified pages (single, ranges, odd, even, last) from the document.
    """
    def execute(
        self,
        input_paths: List[Path],
        output_dir: Path,
        options: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided.")
        src = input_paths[0]
        out_path = output_dir / f"deleted_pages_{src.name}"

        delete_spec = str(options.get("pages_to_delete", "1")).strip()

        with fitz.open(src) as doc:
            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError("PDF document has 0 pages.")

            to_delete = set(parse_page_spec(delete_spec, total_pages))
            if not to_delete:
                to_delete = {0} # Default: delete first page if empty input

            remaining = [p for p in range(total_pages) if p not in to_delete]
            out_doc = fitz.open()
            if not remaining:
                # If all pages were targeted for deletion, supply a clean reset document
                blank_p = out_doc.new_page(width=595, height=842)
                blank_p.insert_text((50, 100), "All pages removed. Document reset.", fontsize=14)
            else:
                for p in remaining:
                    out_doc.insert_pdf(doc, from_page=p, to_page=p)

            out_doc.save(str(out_path), garbage=4, deflate=True)
            out_doc.close()

        return EngineResult(
            output_paths=[out_path],
            metrics={"original_pages": total_pages, "deleted_pages_count": len(to_delete), "remaining_pages": len(remaining)}
        )


class PDFExtractPagesEngine(BaseEngine):
    """
    PDF-006: Extract PDF Pages.
    Extracts chosen pages into a single combined PDF or separate PDFs.
    """
    def execute(
        self,
        input_paths: List[Path],
        output_dir: Path,
        options: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided.")
        src = input_paths[0]

        extract_spec = str(options.get("pages_to_extract", "1")).strip()
        output_mode = str(options.get("output_mode", "single_pdf")).lower()

        with fitz.open(src) as doc:
            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError("PDF document has 0 pages.")

            pages_to_extract = parse_page_spec(extract_spec, total_pages)
            if not pages_to_extract:
                pages_to_extract = [0]

            output_paths: List[Path] = []

            if output_mode == "separate_pdfs":
                for p in pages_to_extract:
                    single_doc = fitz.open()
                    single_doc.insert_pdf(doc, from_page=p, to_page=p)
                    out_p = output_dir / f"{src.stem}_page_{p + 1}.pdf"
                    single_doc.save(str(out_p), garbage=4, deflate=True)
                    single_doc.close()
                    output_paths.append(out_p)
            else:
                out_doc = fitz.open()
                for p in pages_to_extract:
                    out_doc.insert_pdf(doc, from_page=p, to_page=p)
                out_p = output_dir / f"extracted_{src.name}"
                out_doc.save(str(out_p), garbage=4, deflate=True)
                out_doc.close()
                output_paths.append(out_p)

        return EngineResult(
            output_paths=output_paths,
            metrics={"extracted_pages_count": len(pages_to_extract), "output_files": len(output_paths)}
        )


class PDFOrganizeEngine(BaseEngine):
    """
    PDF-005 & PDF-010: Organize & Reorder PDF Pages.
    Re-sequences pages according to custom numerical order or presets (reverse, odd_first, even_first).
    """
    def execute(
        self,
        input_paths: List[Path],
        output_dir: Path,
        options: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided.")
        src = input_paths[0]
        out_path = output_dir / f"organized_{src.name}"

        order_spec = str(options.get("page_order", "reverse")).strip().lower()

        with fitz.open(src) as doc:
            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError("PDF document has 0 pages.")

            if order_spec == "reverse":
                new_order = list(range(total_pages - 1, -1, -1))
            elif order_spec == "odd_first":
                new_order = [p for p in range(total_pages) if (p + 1) % 2 != 0] + [p for p in range(total_pages) if (p + 1) % 2 == 0]
            elif order_spec == "even_first":
                new_order = [p for p in range(total_pages) if (p + 1) % 2 == 0] + [p for p in range(total_pages) if (p + 1) % 2 != 0]
            else:
                specified = parse_page_spec(order_spec, total_pages)
                # Append any unspecified pages at the end
                seen = set(specified)
                unspecified = [p for p in range(total_pages) if p not in seen]
                new_order = specified + unspecified

            out_doc = fitz.open()
            for p in new_order:
                out_doc.insert_pdf(doc, from_page=p, to_page=p)

            out_doc.save(str(out_path), garbage=4, deflate=True)
            out_doc.close()

        return EngineResult(
            output_paths=[out_path],
            metrics={"organized_pages": total_pages, "order": [p + 1 for p in new_order]}
        )
