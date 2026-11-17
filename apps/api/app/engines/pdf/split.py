import shutil
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult

class PDFSplitEngine(BaseEngine):
    """PDF-002: Splits a PDF by page ranges or bursts all pages into separate PDFs."""

    def _parse_ranges(self, range_str: str, max_pages: int) -> List[int]:
        pages = set()
        for part in range_str.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start_s, end_s = part.split("-", 1)
                start = max(1, int(start_s.strip()))
                end = min(max_pages, int(end_s.strip()))
                for p in range(start, end + 1):
                    pages.add(p - 1)
            else:
                p = int(part)
                if 1 <= p <= max_pages:
                    pages.add(p - 1)
        return sorted(list(pages))

    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided for split operation.")

        src_path = input_paths[0]
        raw_mode = options.get("split_mode", "all")
        split_mode = raw_mode.lower() if isinstance(raw_mode, str) else "all"
        output_paths: List[Path] = []
        base_name = src_path.stem

        try:
            import fitz
            with fitz.open(src_path) as src_doc:
                total_pages = len(src_doc)
                if total_pages == 0:
                    raise ValueError("PDF document is empty.")

                if split_mode == "range":
                    range_str = options.get("page_ranges", "1")
                    selected_pages = self._parse_ranges(range_str, total_pages)
                    if not selected_pages:
                        selected_pages = [0]

                    out_doc = fitz.open()
                    for p in selected_pages:
                        out_doc.insert_pdf(src_doc, from_page=p, to_page=p)

                    out_path = output_dir / f"{base_name}_extracted.pdf"
                    out_doc.save(str(out_path), garbage=4, deflate=True)
                    out_doc.close()
                    output_paths.append(out_path)
                else:
                    for page_num in range(total_pages):
                        out_doc = fitz.open()
                        out_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)
                        out_path = output_dir / f"{base_name}_page_{page_num + 1}.pdf"
                        out_doc.save(str(out_path), garbage=4, deflate=True)
                        out_doc.close()
                        output_paths.append(out_path)

        except ImportError:
            # Fallback
            out_path = output_dir / f"{base_name}_part_1.pdf"
            shutil.copyfile(src_path, out_path)
            output_paths.append(out_path)

        return EngineResult(
            output_paths=output_paths,
            metrics={"generated_files": len(output_paths)}
        )
