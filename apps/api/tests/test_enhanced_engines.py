import sys
import tempfile
from pathlib import Path
import fitz

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from apps.api.app.engines import get_engine
from apps.api.app.engines.pdf.page_ops import (
    PDFDuplicateEngine,
    PDFReverseEngine,
    PDFDeletePagesEngine,
    PDFExtractPagesEngine,
    PDFOrganizeEngine,
)
from apps.api.app.engines.pdf.security_and_edit import PDFRotateEngine
from apps.api.app.engines.pdf.compress import PDFCompressEngine
from apps.api.app.engines.image.favicon import FaviconGeneratorEngine
from PIL import Image

def create_multipage_pdf(path: Path, num_pages: int = 5):
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 100), f"Page Number {i + 1}", fontsize=28)
        page.insert_text((50, 150), f"Sample content line on page {i + 1}", fontsize=14)
    doc.save(str(path))
    doc.close()

def create_image_file(path: Path):
    im = Image.new("RGBA", (256, 256), color=(208, 0, 0, 255))
    im.save(path, format="PNG")

def test_rotate_cycles():
    print("Testing PDF Rotate Engine (4 cycles)...")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src = td / "multi.pdf"
        create_multipage_pdf(src, 4)

        engine = PDFRotateEngine()

        # 1. Right 90°
        res = engine.execute([src], td, {"rotation_type": "right_90"})
        with fitz.open(res.output_paths[0]) as d:
            assert d[0].rotation == 90, f"Expected 90, got {d[0].rotation}"
        print("  ✓ Rotate Right 90° PASSED")

        # 2. Left 90° (270°)
        res = engine.execute([src], td, {"rotation_type": "left_90"})
        with fitz.open(res.output_paths[0]) as d:
            assert d[0].rotation == 270, f"Expected 270, got {d[0].rotation}"
        print("  ✓ Rotate Left 90° (270°) PASSED")

        # 3. Flip 180°
        res = engine.execute([src], td, {"rotation_type": "flip_180"})
        with fitz.open(res.output_paths[0]) as d:
            assert d[0].rotation == 180, f"Expected 180, got {d[0].rotation}"
        print("  ✓ Flip 180° PASSED")

        # 4. Reset 0°
        res = engine.execute([src], td, {"rotation_type": "reset_0"})
        with fitz.open(res.output_paths[0]) as d:
            assert d[0].rotation == 0, f"Expected 0, got {d[0].rotation}"
        print("  ✓ Reset 0° PASSED")

        # 5. Odd pages only
        res = engine.execute([src], td, {"rotation_type": "right_90", "page_selection": "odd"})
        with fitz.open(res.output_paths[0]) as d:
            assert d[0].rotation == 90, f"P1 expected 90, got {d[0].rotation}"
            assert d[1].rotation == 0, f"P2 expected 0, got {d[1].rotation}"
            assert d[2].rotation == 90, f"P3 expected 90, got {d[2].rotation}"
            assert d[3].rotation == 0, f"P4 expected 0, got {d[3].rotation}"
        print("  ✓ Rotate Odd Pages Filter PASSED")

def test_duplication():
    print("\nTesting PDF Duplicate Engine...")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src = td / "multi.pdf"
        create_multipage_pdf(src, 3)

        engine = PDFDuplicateEngine()

        # Duplicate all 2x consecutive
        res = engine.execute([src], td, {"copies": 2, "duplicate_mode": "all", "placement": "consecutive"})
        with fitz.open(res.output_paths[0]) as d:
            assert len(d) == 6, f"Expected 6 pages, got {len(d)}"
            text0 = d[0].get_text()
            text1 = d[1].get_text()
            assert "Page Number 1" in text0 and "Page Number 1" in text1
        print("  ✓ Consecutive 2x duplication PASSED (3 pages -> 6 pages)")

        # Duplicate end placement
        res = engine.execute([src], td, {"copies": 2, "duplicate_mode": "all", "placement": "end"})
        with fitz.open(res.output_paths[0]) as d:
            assert len(d) == 6
            assert "Page Number 1" in d[0].get_text()
            assert "Page Number 3" in d[2].get_text()
            assert "Page Number 1" in d[3].get_text()
        print("  ✓ End-of-document duplication PASSED")

def test_reverse():
    print("\nTesting PDF Reverse Engine...")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src = td / "multi.pdf"
        create_multipage_pdf(src, 4)

        engine = PDFReverseEngine()
        res = engine.execute([src], td, {})
        with fitz.open(res.output_paths[0]) as d:
            assert len(d) == 4
            assert "Page Number 4" in d[0].get_text()
            assert "Page Number 3" in d[1].get_text()
            assert "Page Number 2" in d[2].get_text()
            assert "Page Number 1" in d[3].get_text()
        print("  ✓ Reverse page order PASSED (4, 3, 2, 1)")

def test_delete_pages():
    print("\nTesting PDF Delete Pages Engine...")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src = td / "multi.pdf"
        create_multipage_pdf(src, 5)

        engine = PDFDeletePagesEngine()
        # Delete pages 2 and 4
        res = engine.execute([src], td, {"pages_to_delete": "2, 4"})
        with fitz.open(res.output_paths[0]) as d:
            assert len(d) == 3, f"Expected 3 pages, got {len(d)}"
            assert "Page Number 1" in d[0].get_text()
            assert "Page Number 3" in d[1].get_text()
            assert "Page Number 5" in d[2].get_text()
        print("  ✓ Delete specific pages (2, 4) PASSED")

def test_compress_engine():
    print("\nTesting PDF Compression Engine...")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src = td / "image_heavy.pdf"

        # Create image-heavy PDF (simulate 2-3MB PDF)
        doc = fitz.open()
        big_img = Image.new("RGB", (1800, 1200), color=(180, 50, 50))
        img_bytes_io = io.BytesIO() if 'io' in globals() else __import__("io").BytesIO()
        big_img.save(img_bytes_io, format="PNG")
        raw_bytes = img_bytes_io.getvalue()

        for _ in range(3):
            p = doc.new_page(width=595, height=842)
            p.insert_image(p.rect, stream=raw_bytes)
        doc.save(str(src))
        doc.close()

        orig_size = src.stat().st_size
        print(f"  Created test PDF: {orig_size / 1024:.1f} KB")

        engine = PDFCompressEngine()

        # Recommended
        res = engine.execute([src], td, {"compression_mode": "recommended"})
        comp_size = res.output_paths[0].stat().st_size
        print(f"  ✓ Recommended mode: {orig_size / 1024:.1f} KB -> {comp_size / 1024:.1f} KB (saved {((orig_size - comp_size) / orig_size) * 100:.1f}%)")
        assert comp_size <= orig_size

        # Extreme
        res_ext = engine.execute([src], td, {"compression_mode": "extreme"})
        ext_size = res_ext.output_paths[0].stat().st_size
        print(f"  ✓ Extreme mode: {orig_size / 1024:.1f} KB -> {ext_size / 1024:.1f} KB (saved {((orig_size - ext_size) / orig_size) * 100:.1f}%)")
        assert ext_size <= orig_size

        # Target size
        res_tgt = engine.execute([src], td, {"compression_mode": "target_size", "target_size_mb": "100 KB"})
        tgt_size = res_tgt.output_paths[0].stat().st_size
        print(f"  ✓ Target size (100 KB) mode: result is {tgt_size / 1024:.1f} KB")
        assert tgt_size <= orig_size

def test_favicon_zip():
    print("\nTesting Favicon Generator Engine (Zipped output)...")
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        src = td / "logo.png"
        create_image_file(src)

        engine = FaviconGeneratorEngine()
        res = engine.execute([src], td, {"app_name": "TestApp", "theme_color": "#D00000"})
        assert len(res.output_paths) == 1
        assert res.output_paths[0].suffix == ".zip"
        assert res.output_paths[0].name == "favicon_complete_suite.zip"

        import zipfile
        with zipfile.ZipFile(res.output_paths[0], "r") as zf:
            namelist = zf.namelist()
            assert "favicon.ico" in namelist
            assert "site.webmanifest" in namelist
            assert "favicon_tags.html" in namelist
            assert "apple-touch-icon.png" in namelist
            print(f"  ✓ Output is single clean ZIP bundle containing {len(namelist)} items: {namelist}")

if __name__ == "__main__":
    test_rotate_cycles()
    test_duplication()
    test_reverse()
    test_delete_pages()
    test_compress_engine()
    test_favicon_zip()
    print("\n==========================================")
    print("ALL ENHANCED TESTS PASSED PERFECTLY!")
    print("==========================================")
