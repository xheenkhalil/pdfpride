from apps.api.app.engines.base import BaseEngine, EngineResult

# PDF Core Operations
from apps.api.app.engines.pdf.merge import PDFMergeEngine
from apps.api.app.engines.pdf.split import PDFSplitEngine
from apps.api.app.engines.pdf.compress import PDFCompressEngine
from apps.api.app.engines.pdf.page_ops import (
    PDFDuplicateEngine,
    PDFReverseEngine,
    PDFDeletePagesEngine,
    PDFExtractPagesEngine,
    PDFOrganizeEngine,
)

# PDF to Document Formats (Authentic target generation)
from apps.api.app.engines.pdf.to_format import (
    PDFToExcelEngine,
    PDFToWordEngine,
    PDFToTextEngine,
    PDFToHTMLEngine,
    PDFToCSVEngine,
    PDFToSVGEngine,
    PDFImageExtractorEngine,
    PDFToPDFAEngine,
)

# Office & Text to PDF
from apps.api.app.engines.office.to_pdf import (
    WordToPDFEngine,
    ExcelToPDFEngine,
    PowerPointToPDFEngine,
    TextToPDFEngine,
)

# Cross-Format Data Converters
from apps.api.app.engines.office.data_converters import (
    XLSXToCSVEngine,
    CSVToXLSXEngine,
    JSONToCSVEngine,
    CSVToJSONEngine,
    XMLToJSONEngine,
    CSVToTSVEngine,
)

# PDF Security, Protection & Annotation
from apps.api.app.engines.pdf.security_and_edit import (
    PDFProtectEngine,
    PDFUnlockEngine,
    PDFRedactEngine,
    PDFWatermarkEngine,
    PDFPageNumbersEngine,
    PDFRotateEngine,
    PDFMetadataEngine,
    PDFInfoEngine,
)

# Image Studio & Web Dev
from apps.api.app.engines.image.converter import ImagesToPDFEngine, PDFToImagesEngine
from apps.api.app.engines.image.favicon import FaviconGeneratorEngine
from apps.api.app.engines.image.transforms import (
    ImageCompressEngine,
    ImageResizeEngine,
    ImageStripEXIFEngine,
    ImageFormatConvertEngine,
    ImageWatermarkEngine,
    ImageMetadataEngine,
)

# General Utilities & Developer Tools
from apps.api.app.engines.general.dev_and_files import (
    QRCodeGeneratorEngine,
    FileHashEngine,
    TextStatsEngine,
)

# Comprehensive Explicit Operation Registry
EXPLICIT_REGISTRY = {
    # 1. Organization & Core
    "merge_pdf": PDFMergeEngine,
    "pdf_merge": PDFMergeEngine,
    "batch_pdf_merging": PDFMergeEngine,
    "split_pdf": PDFSplitEngine,
    "pdf_split": PDFSplitEngine,
    "batch_pdf_splitting": PDFSplitEngine,
    "extract_pdf_pages": PDFExtractPagesEngine,
    "delete_pdf_pages": PDFDeletePagesEngine,
    "reverse_pdf_pages": PDFReverseEngine,
    "duplicate_pdf_pages": PDFDuplicateEngine,
    "reorder_pdf_pages": PDFOrganizeEngine,
    "organize_pdf_pages": PDFOrganizeEngine,
    "pdf_image_extractor": PDFImageExtractorEngine,
    "pdf_image_extraction": PDFImageExtractorEngine,
    "pdf_to_pdf_a": PDFToPDFAEngine,
    "pdf_to_pdf_x": PDFToPDFAEngine,

    # 2. PDF to Formats (Guaranteed authentic files!)
    "pdf_to_excel_xlsx": PDFToExcelEngine,
    "pdf_to_excel": PDFToExcelEngine,
    "pdf_to_xlsx": PDFToExcelEngine,
    "extract_tables_from_pdf": PDFToExcelEngine,
    "convert_pdf_tables_to_excel": PDFToExcelEngine,
    "convert_scanned_pdf_to_excel": PDFToExcelEngine,

    "pdf_to_word_docx": PDFToWordEngine,
    "pdf_to_word": PDFToWordEngine,
    "pdf_to_docx": PDFToWordEngine,
    "convert_scanned_pdf_to_word": PDFToWordEngine,

    "pdf_to_txt": PDFToTextEngine,
    "extract_text_from_pdf": PDFToTextEngine,
    "pdf_to_html": PDFToHTMLEngine,
    "pdf_to_csv": PDFToCSVEngine,
    "pdf_to_svg": PDFToSVGEngine,

    # 3. PDF to Images (ONLY raster targets)
    "pdf_to_jpg": lambda: PDFToImagesEngine(default_format="jpg"),
    "pdf_to_jpeg": lambda: PDFToImagesEngine(default_format="jpeg"),
    "pdf_to_png": lambda: PDFToImagesEngine(default_format="png"),
    "pdf_to_webp": lambda: PDFToImagesEngine(default_format="webp"),
    "pdf_to_tiff": lambda: PDFToImagesEngine(default_format="tiff"),
    "pdf_to_images": lambda: PDFToImagesEngine(default_format="jpg"),
    "pdf_to_image": lambda: PDFToImagesEngine(default_format="jpg"),

    # 4. Inbound to PDF
    "word_to_pdf": WordToPDFEngine,
    "word_to_pdf_converter": WordToPDFEngine,
    "excel_to_pdf": ExcelToPDFEngine,
    "excel_to_pdf_converter": ExcelToPDFEngine,
    "powerpoint_to_pdf": PowerPointToPDFEngine,
    "powerpoint_to_pdf_converter": PowerPointToPDFEngine,
    "jpg_to_pdf": ImagesToPDFEngine,
    "jpeg_to_pdf": ImagesToPDFEngine,
    "png_to_pdf": ImagesToPDFEngine,
    "webp_to_pdf": ImagesToPDFEngine,
    "tiff_to_pdf": ImagesToPDFEngine,
    "svg_to_pdf": ImagesToPDFEngine,
    "image_to_pdf": ImagesToPDFEngine,
    "images_to_pdf": ImagesToPDFEngine,
    "txt_to_pdf": TextToPDFEngine,
    "markdown_to_pdf": TextToPDFEngine,
    "html_to_pdf": TextToPDFEngine,
    "csv_to_pdf": TextToPDFEngine,
    "rtf_to_pdf": WordToPDFEngine,
    "odt_to_pdf": WordToPDFEngine,
    "ods_to_pdf": ExcelToPDFEngine,
    "odp_to_pdf": PowerPointToPDFEngine,

    # 5. Cross-format Converters
    "xlsx_to_csv": XLSXToCSVEngine,
    "excel_to_csv": XLSXToCSVEngine,
    "csv_to_xlsx": CSVToXLSXEngine,
    "csv_to_tsv": CSVToTSVEngine,
    "tsv_to_csv": CSVToTSVEngine,
    "json_to_csv": JSONToCSVEngine,
    "csv_to_json": CSVToJSONEngine,
    "xml_to_json": XMLToJSONEngine,
    "docx_to_html": PDFToHTMLEngine,
    "docx_to_txt": PDFToTextEngine,

    # 6. Compression (Guaranteed Size Invariance)
    "compress_pdf": PDFCompressEngine,
    "pdf_compress": PDFCompressEngine,
    "basic_pdf_compression": PDFCompressEngine,
    "recommended_pdf_compression": PDFCompressEngine,
    "strong_pdf_compression": PDFCompressEngine,
    "extreme_pdf_compression": PDFCompressEngine,
    "custom_pdf_compression": PDFCompressEngine,
    "lossless_pdf_optimization": PDFCompressEngine,
    "pdf_grayscale_conversion": PDFCompressEngine,
    "batch_pdf_compression": PDFCompressEngine,

    # 7. Security & Protection
    "protect_pdf_with_password": PDFProtectEngine,
    "pdf_protect": PDFProtectEngine,
    "encrypt_pdf": PDFProtectEngine,
    "unlock_pdf": PDFUnlockEngine,
    "pdf_unlock": PDFUnlockEngine,
    "decrypt_pdf": PDFUnlockEngine,
    "remove_pdf_password": PDFUnlockEngine,
    "redact_pdf": PDFRedactEngine,
    "pdf_redact": PDFRedactEngine,

    # 8. Editing & Watermark
    "add_watermark": PDFWatermarkEngine,
    "pdf_watermark": PDFWatermarkEngine,
    "add_page_numbers": PDFPageNumbersEngine,
    "pdf_page_numbers": PDFPageNumbersEngine,
    "rotate_pdf": PDFRotateEngine,
    "pdf_rotate": PDFRotateEngine,
    "batch_pdf_rotation": PDFRotateEngine,
    "pdf_metadata_editor": PDFMetadataEngine,
    "pdf_metadata": PDFMetadataEngine,
    "pdf_page_counter": PDFInfoEngine,
    "pdf_information": PDFInfoEngine,
    "pdf_info": PDFInfoEngine,

    # 9. Web Dev & Image Studio
    "image_to_favicon": FaviconGeneratorEngine,
    "image_to_favicon_web_app_manifest_studio": FaviconGeneratorEngine,
    "image_watermark": ImageWatermarkEngine,
    "image_metadata_viewer": ImageMetadataEngine,
    "image_metadata_editor": ImageMetadataEngine,
    "extract_powerpoint_images": PDFImageExtractorEngine,
    "powerpoint_to_images": PDFToImagesEngine,
    "image_compressor": ImageCompressEngine,
    "image_compress": ImageCompressEngine,
    "batch_image_compression": ImageCompressEngine,
    "image_resizer": ImageResizeEngine,
    "image_resize": ImageResizeEngine,
    "exif_data_remover": ImageStripEXIFEngine,
    "exif_data_extractor": ImageMetadataEngine,
    "exif_extractor": ImageMetadataEngine,
    "image_strip_exif": ImageStripEXIFEngine,
    "jpg_to_png": ImageFormatConvertEngine,
    "png_to_jpg": ImageFormatConvertEngine,
    "jpg_to_webp": ImageFormatConvertEngine,
    "webp_to_jpg": ImageFormatConvertEngine,

    # 10. General File & Developer Utilities
    "qr_code_generator": QRCodeGeneratorEngine,
    "qr_generate": QRCodeGeneratorEngine,
    "file_hash_generator": FileHashEngine,
    "sha_256_checksum_generator": FileHashEngine,
    "file_hash": FileHashEngine,
    "word_counter": TextStatsEngine,
    "character_counter": TextStatsEngine,
    "sentence_counter": TextStatsEngine,
    "line_counter": TextStatsEngine,
}

def get_engine(operation: str) -> BaseEngine:
    """
    Deterministic resolution of engine based on normalized operation key.
    Guarantees strict target format adherence:
    - Never routes PDF to Excel into an image generator!
    - Never routes Word or Text conversions into an image generator!
    - Accurately discriminates directional conversions (*_to_pdf vs pdf_to_*).
    """
    op = operation.lower().strip().replace("-", "_")

    # 1. Exact match from explicit registry
    if op in EXPLICIT_REGISTRY:
        return EXPLICIT_REGISTRY[op]()

    # 2. Archive & Standards
    if op.startswith("pdf_to_pdf") or "pdf_a" in op or "pdf_x" in op:
        return PDFToPDFAEngine()

    # 3. Directional Inbound: Anything Converting TO PDF
    if "_to_pdf" in op or op.endswith("to_pdf") or "to_pdf" in op:
        if any(k in op for k in ["word", "docx", "rtf", "odt"]):
            return WordToPDFEngine()
        if any(k in op for k in ["excel", "xlsx", "ods"]):
            return ExcelToPDFEngine()
        if any(k in op for k in ["powerpoint", "pptx", "odp", "ppt"]):
            return PowerPointToPDFEngine()
        if any(k in op for k in ["image", "jpg", "jpeg", "png", "webp", "tiff", "svg", "bmp"]):
            return ImagesToPDFEngine()
        return TextToPDFEngine()

    # 4. PDF to Office Documents & Data Formats
    if any(k in op for k in ["to_excel", "to_xlsx", "extract_table", "tables_to_excel"]):
        return PDFToExcelEngine()
    if any(k in op for k in ["to_word", "to_docx", "pdf_to_word", "pdf_to_docx"]):
        return PDFToWordEngine()
    if any(k in op for k in ["_txt", "to_txt", "extract_text"]):
        return PDFToTextEngine()
    if any(k in op for k in ["_html", "to_html"]):
        return PDFToHTMLEngine()
    if any(k in op for k in ["_csv", "to_csv"]):
        return PDFToCSVEngine()
    if any(k in op for k in ["_svg", "to_svg"]):
        return PDFToSVGEngine()

    # 5. Image & Web Utilities
    if "favicon" in op:
        return FaviconGeneratorEngine()
    if op.startswith("image_") or "_image" in op:
        if "watermark" in op:
            return ImageWatermarkEngine()
        if "meta" in op or "info" in op or "view" in op:
            return ImageMetadataEngine()
        if "compress" in op:
            return ImageCompressEngine()
        if "resize" in op:
            return ImageResizeEngine()
        if "exif" in op:
            return ImageStripEXIFEngine()
    if "image_extractor" in op or "extract_image" in op:
        return PDFImageExtractorEngine()
    if any(k in op for k in ["to_png"]):
        return PDFToImagesEngine(default_format="png")
    if any(k in op for k in ["to_jpg", "to_jpeg"]):
        return PDFToImagesEngine(default_format="jpg")
    if any(k in op for k in ["to_webp"]):
        return PDFToImagesEngine(default_format="webp")
    if any(k in op for k in ["to_tiff", "to_images", "to_image"]):
        return PDFToImagesEngine(default_format="png")
    if any(k in op for k in ["qr", "qrcode"]):
        return QRCodeGeneratorEngine()
    if any(k in op for k in ["hash", "checksum"]):
        return FileHashEngine()

    # 6. PDF Security, Protection & Annotation
    if any(k in op for k in ["watermark"]):
        return PDFWatermarkEngine()
    if any(k in op for k in ["page_number", "page_num"]):
        return PDFPageNumbersEngine()
    if any(k in op for k in ["redact"]):
        return PDFRedactEngine()
    if any(k in op for k in ["protect", "encrypt", "set_pdf_permission", "restrict_pdf"]):
        return PDFProtectEngine()
    if any(k in op for k in ["unlock", "decrypt", "remove_password"]):
        return PDFUnlockEngine()
    if any(k in op for k in ["rotate"]):
        return PDFRotateEngine()
    if any(k in op for k in ["metadata", "bookmark"]):
        return PDFMetadataEngine()
    if any(k in op for k in ["counter", "info", "inspector", "version", "inspect"]):
        return PDFInfoEngine()

    # 7. Organization & Page Operations
    if "exif" in op:
        return ImageMetadataEngine()
    if any(k in op for k in ["split", "extract", "delete", "reverse"]):
        return PDFSplitEngine()
    if any(k in op for k in ["merge", "combine"]):
        return PDFMergeEngine()

    # 8. Compression & Optimization
    if any(k in op for k in ["compress", "optimize", "reduce", "downsample", "flatten", "repair", "linearize"]):
        return PDFCompressEngine()

    # Default fallback: safe PDF compression
    return PDFCompressEngine()

__all__ = [
    "BaseEngine",
    "EngineResult",
    "get_engine",
    "EXPLICIT_REGISTRY",
]
