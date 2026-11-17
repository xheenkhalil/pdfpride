import sys
import pytest
import fitz
from PIL import Image
from pathlib import Path
import zipfile
import json

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from apps.api.app.engines.pdf.merge import PDFMergeEngine
from apps.api.app.engines.pdf.split import PDFSplitEngine
from apps.api.app.engines.pdf.compress import PDFCompressEngine
from apps.api.app.engines.image.converter import ImagesToPDFEngine, PDFToImagesEngine
from apps.api.app.engines.image.favicon import FaviconGeneratorEngine

def create_sample_pdf(path: Path, pages: int = 2, text: str = "Sample Page"):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((50, 100), f"{text} - Page {i+1}", fontsize=20)
    doc.save(str(path))
    doc.close()

def create_sample_image(path: Path, color=(255, 0, 0)):
    im = Image.new("RGBA", (512, 512), color=color)
    im.save(path)

def test_pdf_merge_engine(tmp_path):
    pdf1 = tmp_path / "doc1.pdf"
    pdf2 = tmp_path / "doc2.pdf"
    create_sample_pdf(pdf1, pages=2, text="Doc 1")
    create_sample_pdf(pdf2, pages=3, text="Doc 2")

    engine = PDFMergeEngine()
    result = engine.execute(
        input_paths=[pdf1, pdf2],
        output_dir=tmp_path,
        options={"output_filename": "merged.pdf"}
    )

    assert len(result.output_paths) == 1
    assert result.output_paths[0].exists()

    with fitz.open(result.output_paths[0]) as out_doc:
        assert len(out_doc) == 5

def test_pdf_split_engine(tmp_path):
    pdf = tmp_path / "source.pdf"
    create_sample_pdf(pdf, pages=4, text="Split Source")

    engine = PDFSplitEngine()
    result_range = engine.execute(
        input_paths=[pdf],
        output_dir=tmp_path,
        options={"split_mode": "range", "page_ranges": "1,3"}
    )
    assert len(result_range.output_paths) == 1
    with fitz.open(result_range.output_paths[0]) as out_doc:
        assert len(out_doc) == 2

def test_pdf_compress_size_invariance(tmp_path):
    # Test that compression NEVER produces a file larger than the input
    pdf = tmp_path / "small.pdf"
    create_sample_pdf(pdf, pages=1, text="Tiny PDF")
    orig_size = pdf.stat().st_size

    engine = PDFCompressEngine()
    result = engine.execute(
        input_paths=[pdf],
        output_dir=tmp_path,
        options={"profile": "balanced"}
    )

    out_file = result.output_paths[0]
    assert out_file.exists()
    assert out_file.stat().st_size <= orig_size, "Output file must NEVER be larger than original!"
    assert result.metrics["reduction_percentage"] >= 0.0

def test_favicon_generator_suite(tmp_path):
    logo = tmp_path / "app_logo.png"
    create_sample_image(logo)

    engine = FaviconGeneratorEngine()
    result = engine.execute(
        input_paths=[logo],
        output_dir=tmp_path,
        options={"app_name": "Test App", "theme_color": "#D00000"}
    )

    zip_file = result.output_paths[0]
    assert zip_file.exists()
    assert zipfile.is_zipfile(zip_file)

    with zipfile.ZipFile(zip_file, "r") as z:
        filenames = z.namelist()
        assert "favicon.ico" in filenames
        assert "favicon-16x16.png" in filenames
        assert "favicon-32x32.png" in filenames
        assert "apple-touch-icon.png" in filenames
        assert "android-chrome-192x192.png" in filenames
        assert "android-chrome-512x512.png" in filenames
        assert "site.webmanifest" in filenames
        assert "favicon_tags.html" in filenames
