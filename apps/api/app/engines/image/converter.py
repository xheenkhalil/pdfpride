from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult

class ImagesToPDFEngine(BaseEngine):
    """PDF-016: Converts single or multiple raster images (JPG, PNG, WebP) into a unified PDF."""

    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No images provided for PDF conversion.")

        total_images = len(input_paths)
        if progress_callback:
            progress_callback(10, f"Loading {total_images} images...")

        images: List[Image.Image] = []
        for idx, img_path in enumerate(input_paths):
            im = Image.open(img_path)
            # Normalize image modes for standard PDF spec
            if im.mode in ("RGBA", "P"):
                rgb_im = Image.new("RGB", im.size, (255, 255, 255))
                if im.mode == "RGBA":
                    rgb_im.paste(im, mask=im.split()[3])
                else:
                    rgb_im.paste(im)
                images.append(rgb_im)
            else:
                images.append(im.convert("RGB"))

            if progress_callback:
                progress = int(10 + ((idx + 1) / total_images) * 60)
                progress_callback(progress, f"Processed image {idx + 1} of {total_images}")

        raw_out = options.get("output_filename", "converted_images.pdf")
        output_filename = raw_out if isinstance(raw_out, str) and raw_out else "converted_images.pdf"
        if not output_filename.endswith(".pdf"):
            output_filename += ".pdf"

        output_path = output_dir / output_filename

        if progress_callback:
            progress_callback(85, "Assembling PDF document...")

        if images:
            images[0].save(
                output_path, 
                "PDF", 
                resolution=100.0, 
                save_all=True, 
                append_images=images[1:]
            )

        if progress_callback:
            progress_callback(100, "Images converted to PDF successfully.")

        return EngineResult(
            output_paths=[output_path],
            metrics={"images_count": total_images}
        )

class PDFToImagesEngine(BaseEngine):
    """PDF-015: Converts each page of a PDF document into high-resolution JPG or PNG images."""

    def __init__(self, default_format: str = "jpg"):
        self.default_format = default_format

    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input PDF provided.")

        input_path = input_paths[0]
        raw_dpi = options.get("dpi", 150)
        try:
            dpi = int(raw_dpi)
        except Exception:
            dpi = 150
        raw_fmt = options.get("format") or self.default_format
        img_format = raw_fmt.lower() if isinstance(raw_fmt, str) else self.default_format
        if img_format not in ("jpg", "jpeg", "png", "webp", "tiff"):
            img_format = "jpg"

        doc = fitz.open(input_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF is empty.")

        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        output_paths: List[Path] = []
        base_name = input_path.stem

        for page_num in range(total_pages):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            ext = "jpeg" if img_format in ("jpg", "jpeg") else ("png" if img_format in ("png", "webp", "tiff") else img_format)
            out_file = output_dir / f"{base_name}_page_{page_num + 1}.{ext}"
            pix.save(str(out_file))
            output_paths.append(out_file)

            if progress_callback:
                progress = int(((page_num + 1) / total_pages) * 90)
                progress_callback(progress, f"Rendered page {page_num + 1} of {total_pages}")

        doc.close()

        if progress_callback:
            progress_callback(100, "PDF converted to images successfully.")

        return EngineResult(
            output_paths=output_paths,
            metrics={"pages_rendered": total_pages, "dpi": dpi, "format": img_format}
        )
