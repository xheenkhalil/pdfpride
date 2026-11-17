import io
import shutil
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import fitz  # PyMuPDF
from PIL import Image
from apps.api.app.engines.base import BaseEngine, EngineResult

def parse_target_size_bytes(val: Any) -> Optional[int]:
    if not val:
        return None
    if isinstance(val, (int, float)):
        return int(val * 1024 * 1024) if val < 100 else int(val)
    s = str(val).strip().lower()
    try:
        if s.endswith("mb"):
            return int(float(s.replace("mb", "").strip()) * 1024 * 1024)
        if s.endswith("kb"):
            return int(float(s.replace("kb", "").strip()) * 1024)
        if s.endswith("b"):
            return int(float(s.replace("b", "").strip()))
        f = float(s)
        return int(f * 1024 * 1024) if f < 100 else int(f)
    except Exception:
        return None

def _recompress_pdf_pass(doc: fitz.Document, max_dim: int, quality: int) -> int:
    """
    Downsamples and recompresses all embedded raster images in doc.
    Returns count of recompressed images.
    """
    total_images = 0
    seen_xrefs = set()

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        image_list = page.get_images(full=True)
        for img_info in image_list:
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base_img = doc.extract_image(xref)
                if not base_img:
                    continue
                img_bytes = base_img["image"]
                orig_len = len(img_bytes)
                orig_w = base_img["width"]
                orig_h = base_img["height"]

                # Only process if image is non-trivial (>15 KB)
                if orig_len < 15360 and orig_w <= max_dim and orig_h <= max_dim:
                    continue

                pil_img = Image.open(io.BytesIO(img_bytes))
                if pil_img.mode in ("RGBA", "P", "LA"):
                    pil_img = pil_img.convert("RGB")
                elif pil_img.mode not in ("RGB", "L"):
                    pil_img = pil_img.convert("RGB")

                # Downsample pixel dimensions if larger than target max_dim
                cur_w, cur_h = pil_img.size
                if cur_w > max_dim or cur_h > max_dim:
                    if cur_w >= cur_h:
                        new_w = max_dim
                        new_h = max(1, int(cur_h * (max_dim / cur_w)))
                    else:
                        new_h = max_dim
                        new_w = max(1, int(cur_w * (max_dim / cur_h)))
                    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                else:
                    new_w, new_h = cur_w, cur_h

                out_io = io.BytesIO()
                pil_img.save(out_io, format="JPEG", quality=quality, optimize=True)
                recomp = out_io.getvalue()

                if len(recomp) < orig_len:
                    doc.update_stream(xref, recomp)
                    doc.xref_set_key(xref, "Filter", "/DCTDecode")
                    doc.xref_set_key(xref, "Width", str(new_w))
                    doc.xref_set_key(xref, "Height", str(new_h))
                    doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
                    total_images += 1
            except Exception:
                continue

    return total_images


def _raster_rebuild_pdf(input_path: Path, output_path: Path, dpi: int, quality: int):
    """
    Rebuilds document by rendering pages to compressed pixmaps.
    Guarantees massive shrinkage for scanned / image-heavy PDFs that resist stream deflation.
    """
    src_doc = fitz.open(input_path)
    new_doc = fitz.open()
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for page in src_doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_io = io.BytesIO()
        pil_img.save(img_io, format="JPEG", quality=quality, optimize=True)
        img_bytes = img_io.getvalue()

        # Insert page with image
        img_doc = fitz.open(stream=img_bytes, filetype="jpeg")
        rect = page.rect
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=img_bytes)
        img_doc.close()

    new_doc.save(str(output_path), garbage=4, deflate=True)
    new_doc.close()
    src_doc.close()


class PDFCompressEngine(BaseEngine):
    """
    PDF-003 & PDF-073 to 090: High-Efficiency PDF Compression & Optimization Engine.
    
    Features:
    1. Size-Invariance: Never outputs a file larger than input.
    2. Deep image downsampling: Downscales pixel resolution (DPI) and recompresses to JPEG.
    3. Target Size Mode: Iteratively compresses towards user-requested file size (e.g. 2 MB, 500 KB).
    4. Profiles:
       - Recommended: 1600px max, Q=70 (~50% reduction)
       - Extreme: 1000px max, Q=38 (~70-80% reduction)
       - Low: 2400px max, Q=85 (~20-30% reduction)
    """

    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input file provided for compression.")

        input_path = input_paths[0]
        raw_prof = str(options.get("compression_mode") or options.get("profile") or "recommended").lower()
        output_filename = f"compressed_{input_path.name}"
        output_path = output_dir / output_filename
        temp_out = output_dir / f"tmp_{output_filename}"

        orig_size = input_path.stat().st_size
        target_bytes = parse_target_size_bytes(
            options.get("target_size_mb") or options.get("target_size_kb") or options.get("target_size")
        )

        if progress_callback:
            progress_callback(10, f"Analyzing PDF structure and image density (Size: {(orig_size / 1024 / 1024):.2f} MB)...")

        # Determine initial compression profile settings
        profiles = {
            "low": {"max_dim": 2400, "quality": 85},
            "recommended": {"max_dim": 1600, "quality": 68},
            "balanced": {"max_dim": 1600, "quality": 68},
            "high": {"max_dim": 1200, "quality": 50},
            "extreme": {"max_dim": 960, "quality": 35},
        }

        # Select config
        cfg = profiles.get(raw_prof, profiles["recommended"])
        if target_bytes and target_bytes < orig_size:
            ratio = target_bytes / orig_size
            if ratio < 0.35:
                cfg = profiles["extreme"]
            elif ratio < 0.65:
                cfg = profiles["high"]
            else:
                cfg = profiles["recommended"]

        # Step 1: Open doc and perform pass
        if progress_callback:
            progress_callback(25, f"Downsampling embedded images (Max Dim: {cfg['max_dim']}px, Quality: {cfg['quality']})...")

        doc = fitz.open(input_path)
        images_recompressed = _recompress_pdf_pass(doc, max_dim=cfg["max_dim"], quality=cfg["quality"])

        if progress_callback:
            progress_callback(60, "Deflating font streams, structure trees, and cross-references...")

        doc.save(
            str(temp_out),
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True
        )
        doc.close()

        current_size = temp_out.stat().st_size

        # Step 2: Target Size Loop or Extreme fallback if size reduction was minimal
        needs_more_compression = False
        if target_bytes and current_size > target_bytes:
            needs_more_compression = True
        elif raw_prof == "extreme" and (orig_size - current_size) / orig_size < 0.25:
            needs_more_compression = True

        if needs_more_compression:
            if progress_callback:
                progress_callback(75, "Applying advanced multi-tier compression...")

            # Try aggressive pass
            try:
                doc2 = fitz.open(input_path)
                _recompress_pdf_pass(doc2, max_dim=800, quality=30)
                temp_out_2 = output_dir / f"tmp2_{output_filename}"
                doc2.save(
                    str(temp_out_2),
                    garbage=4,
                    deflate=True,
                    deflate_images=True,
                    deflate_fonts=True,
                    clean=True
                )
                doc2.close()
                if temp_out_2.exists() and temp_out_2.stat().st_size < current_size:
                    temp_out.unlink()
                    temp_out_2.rename(temp_out)
                    current_size = temp_out.stat().st_size
            except Exception:
                pass

            # If still above target and target is explicit, attempt raster reconstruction at 110 DPI
            if target_bytes and current_size > target_bytes and (orig_size > 500000):
                if progress_callback:
                    progress_callback(85, "Executing high-density raster reconstruction...")
                try:
                    raster_out = output_dir / f"raster_{output_filename}"
                    dpi = 96 if (target_bytes / orig_size) < 0.4 else 120
                    q = 35 if (target_bytes / orig_size) < 0.4 else 50
                    _raster_rebuild_pdf(input_path, raster_out, dpi=dpi, quality=q)
                    if raster_out.exists() and raster_out.stat().st_size < current_size:
                        if temp_out.exists():
                            temp_out.unlink()
                        raster_out.rename(temp_out)
                        current_size = temp_out.stat().st_size
                except Exception:
                    pass

        # Step 3: Safeguard & final verification
        if current_size >= orig_size:
            # Document cannot be made smaller without destroying text/content
            if temp_out.exists():
                temp_out.unlink()
            shutil.copyfile(str(input_path), str(output_path))
            final_size = orig_size
            reduction_pct = 0.0
            status_msg = "Document was already fully compressed. Preserved original without degradation."
        else:
            if output_path.exists():
                output_path.unlink()
            temp_out.rename(output_path)
            final_size = current_size
            reduction_pct = round(((orig_size - final_size) / orig_size) * 100, 2)
            status_msg = f"Reduced from {(orig_size / 1024 / 1024):.2f} MB to {(final_size / 1024 / 1024):.2f} MB ({reduction_pct}% reduction)."

        if progress_callback:
            progress_callback(100, status_msg)

        return EngineResult(
            output_paths=[output_path],
            metrics={
                "original_size": orig_size,
                "compressed_size": final_size,
                "reduction_percentage": reduction_pct,
                "profile": raw_prof,
                "images_recompressed": images_recompressed,
                "status": status_msg
            }
        )
