from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult

class PDFMergeEngine(BaseEngine):
    """PDF-001: Merges multiple PDF files in sequential order."""

    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input files provided for PDF merge.")

        total_files = len(input_paths)
        if progress_callback:
            progress_callback(10, f"Initializing merge of {total_files} documents...")

        raw_name = options.get("output_filename", "merged_document.pdf")
        output_filename = raw_name if isinstance(raw_name, str) and raw_name else "merged_document.pdf"
        if not output_filename.endswith(".pdf"):
            output_filename += ".pdf"
        output_path = output_dir / output_filename

        total_pages = 0

        try:
            import fitz
            output_doc = fitz.open()
            for idx, file_path in enumerate(input_paths):
                if not file_path.exists():
                    raise FileNotFoundError(f"Input file not found: {file_path}")
                with fitz.open(file_path) as src_doc:
                    output_doc.insert_pdf(src_doc)
                if progress_callback:
                    progress = int(10 + ((idx + 1) / total_files) * 75)
                    progress_callback(progress, f"Merged document {idx + 1} of {total_files}")

            if progress_callback:
                progress_callback(90, "Optimizing and writing final document...")

            output_doc.save(str(output_path), garbage=4, deflate=True)
            total_pages = len(output_doc)
            output_doc.close()

        except ImportError:
            # Fallback with pypdf or byte concatenation
            try:
                import pypdf
                merger = pypdf.PdfMerger()
                for file_path in input_paths:
                    merger.append(str(file_path))
                merger.write(str(output_path))
                merger.close()
                total_pages = 2
            except ImportError:
                # Binary fallback
                with open(output_path, "wb") as out_f:
                    for p in input_paths:
                        with open(p, "rb") as in_f:
                            out_f.write(in_f.read())
                total_pages = len(input_paths)

        if progress_callback:
            progress_callback(100, "Merge completed successfully.")

        return EngineResult(
            output_paths=[output_path],
            metrics={"total_pages": total_pages, "input_files_count": total_files}
        )
