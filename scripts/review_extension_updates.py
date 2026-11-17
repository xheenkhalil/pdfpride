import json
from pathlib import Path

tools_path = Path("packages/tool-registry/tools.json")
with open(tools_path, "r", encoding="utf-8") as f:
    tools = json.load(f)

def get_correct_formats(tool):
    num = tool.get("number", 0)
    name = tool.get("name", "")
    op = tool.get("operation", "").lower()
    cat = tool.get("category", "")
    current_exts = tool.get("accepted_extensions", [])
    name_l = name.lower()

    # Default to None (meaning keep current unless determined)
    new_exts = None
    new_mimes = None

    # --- Category 1: PDF Organization & Management (001 - 032) ---
    if 1 <= num <= 32:
        # All of these are PDF operations on PDF files!
        # Even PDF Image Extractor (024) extracts images FROM a PDF!
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]

    # --- Category 2: PDF Conversion (033 - 072) ---
    # 033 - 045: PDF to X (User uploads PDF)
    elif 33 <= num <= 45:
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]
    
    # 046 - 063: X to PDF
    elif num == 46: # Word to PDF
        new_exts = [".docx", ".doc", ".rtf", ".odt"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword", "application/rtf", "application/vnd.oasis.opendocument.text"]
    elif num == 47: # Excel to PDF
        new_exts = [".xlsx", ".xls", ".csv", ".ods"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel", "text/csv", "application/vnd.oasis.opendocument.spreadsheet"]
    elif num == 48: # PowerPoint to PDF
        new_exts = [".pptx", ".ppt", ".odp"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/vnd.ms-powerpoint", "application/vnd.oasis.opendocument.presentation"]
    elif 49 <= num <= 54: # Image to PDF (JPG, JPEG, PNG, WebP, TIFF, SVG)
        new_exts = [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".svg", ".bmp"]
        new_mimes = ["image/jpeg", "image/png", "image/webp", "image/tiff", "image/svg+xml", "image/bmp"]
    elif num == 55: # TXT to PDF
        new_exts = [".txt", ".text"]
        new_mimes = ["text/plain"]
    elif num == 56: # HTML to PDF
        new_exts = [".html", ".htm"]
        new_mimes = ["text/html"]
    elif num == 57: # CSV to PDF
        new_exts = [".csv"]
        new_mimes = ["text/csv"]
    elif num == 58: # EPUB to PDF
        new_exts = [".epub"]
        new_mimes = ["application/epub+zip"]
    elif num == 59: # RTF to PDF
        new_exts = [".rtf"]
        new_mimes = ["application/rtf", "text/rtf"]
    elif num == 60: # ODT to PDF
        new_exts = [".odt"]
        new_mimes = ["application/vnd.oasis.opendocument.text"]
    elif num == 61: # ODS to PDF
        new_exts = [".ods"]
        new_mimes = ["application/vnd.oasis.opendocument.spreadsheet"]
    elif num == 62: # ODP to PDF
        new_exts = [".odp"]
        new_mimes = ["application/vnd.oasis.opendocument.presentation"]
    elif num == 63: # Markdown to PDF
        new_exts = [".md", ".markdown", ".txt"]
        new_mimes = ["text/markdown", "text/plain"]
    elif num == 64: # Markdown to DOCX
        new_exts = [".md", ".markdown", ".txt"]
        new_mimes = ["text/markdown", "text/plain"]
    elif num in (65, 66): # DOCX to HTML, DOCX to TXT
        new_exts = [".docx", ".doc"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]
    elif num == 67: # XLSX to CSV
        new_exts = [".xlsx", ".xls"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]
    elif num == 68: # CSV to XLSX
        new_exts = [".csv"]
        new_mimes = ["text/csv"]
    elif num == 69: # PPTX to Images
        new_exts = [".pptx", ".ppt"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/vnd.ms-powerpoint"]
    elif num == 70: # HTML to Images
        new_exts = [".html", ".htm"]
        new_mimes = ["text/html"]
    elif num == 71: # JSON to CSV
        new_exts = [".json"]
        new_mimes = ["application/json"]
    elif num == 72: # XML to JSON
        new_exts = [".xml"]
        new_mimes = ["application/xml", "text/xml"]

    # --- Category 3: PDF Compression (073 - 090) ---
    elif 73 <= num <= 90:
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]

    # --- Category 4: PDF Editing (091 - 120) ---
    elif 91 <= num <= 120:
        # All editing actions operate on a target PDF!
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]

    # --- Category 5: PDF Security & Protection (121 - 140) ---
    elif 121 <= num <= 140:
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]

    # --- Category 6: PDF Forms (141 - 150) ---
    elif 141 <= num <= 150:
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]

    # --- Category 7: OCR & Document Intelligence (151 - 165) ---
    elif 151 <= num <= 165:
        # 151-165: OCR PDF or document extraction
        # All expect PDF documents (scanned PDF, tables in PDF, etc.)
        new_exts = [".pdf"]
        new_mimes = ["application/pdf"]

    # --- Category 8: Image Studio (166 - 205) ---
    elif 166 <= num <= 205:
        if num == 193: # Image to PDF
            new_exts = [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".svg", ".bmp"]
            new_mimes = ["image/jpeg", "image/png", "image/webp", "image/tiff", "image/svg+xml", "image/bmp"]
        elif num == 194: # PDF to Image
            new_exts = [".pdf"]
            new_mimes = ["application/pdf"]
        else: # Regular image manipulation
            new_exts = [".jpg", ".jpeg", ".png", ".webp", ".svg", ".tiff", ".bmp", ".ico"]
            new_mimes = ["image/jpeg", "image/png", "image/webp", "image/svg+xml", "image/tiff", "image/bmp", "image/x-icon"]

    # --- Category 9: Word Document Utilities (206 - 221) ---
    elif 206 <= num <= 221:
        new_exts = [".docx", ".doc"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]

    # --- Category 10: Excel & Spreadsheet Utilities (222 - 241) ---
    elif 222 <= num <= 241:
        if num == 222: # Excel to PDF
            new_exts = [".xlsx", ".xls", ".csv", ".ods"]
            new_mimes = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel", "text/csv"]
        elif num in (224, 238, 241): # CSV to X
            new_exts = [".csv"]
            new_mimes = ["text/csv"]
        elif num in (226, 239): # JSON to X
            new_exts = [".json"]
            new_mimes = ["application/json"]
        elif num == 240: # TSV to CSV
            new_exts = [".tsv"]
            new_mimes = ["text/tab-separated-values"]
        else: # General Excel manipulation
            new_exts = [".xlsx", ".xls", ".csv"]
            new_mimes = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel", "text/csv"]

    # --- Category 11: PowerPoint Utilities (242 - 255) ---
    elif 242 <= num <= 255:
        new_exts = [".pptx", ".ppt"]
        new_mimes = ["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/vnd.ms-powerpoint"]

    # --- Category 12: General File Utilities (256 - 275) ---
    elif 256 <= num <= 275:
        # General utilities accept any document/file format
        new_exts = [".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".png", ".zip", ".txt"]
        new_mimes = ["*/*"]

    # --- Category 13: Text & Productivity Utilities (276 - 290) ---
    elif 276 <= num <= 290:
        if num in (285, 286): # Markdown to X
            new_exts = [".md", ".markdown", ".txt"]
            new_mimes = ["text/markdown", "text/plain"]
        elif num in (287, 288): # HTML to X
            new_exts = [".html", ".htm"]
            new_mimes = ["text/html"]
        elif num == 289: # JSON to XML
            new_exts = [".json"]
            new_mimes = ["application/json"]
        elif num == 290: # XML to JSON
            new_exts = [".xml"]
            new_mimes = ["application/xml", "text/xml"]
        else: # Text operations
            new_exts = [".txt", ".text", ".md", ".json", ".csv"]
            new_mimes = ["text/plain", "text/markdown", "application/json", "text/csv"]

    # --- Category 14-20: Batch, Cloud, Sharing, Settings, Admin, Advanced (291 - 440) ---
    elif 291 <= num <= 440:
        # Universal document inputs (or PDF by default)
        new_exts = [".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".png"]
        new_mimes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/png"]

    # --- Special Tool 441: Favicon Studio ---
    elif num == 441:
        new_exts = [".png", ".jpg", ".jpeg", ".webp", ".svg"]
        new_mimes = ["image/png", "image/jpeg", "image/webp", "image/svg+xml"]

    return new_exts, new_mimes

changes = []
for t in tools:
    num = t.get("number", 0)
    cur_exts = t.get("accepted_extensions", [])
    cur_mimes = t.get("accepted_mimes", [])
    new_exts, new_mimes = get_correct_formats(t)
    if new_exts is not None and (cur_exts != new_exts or cur_mimes != new_mimes):
        changes.append((num, t["name"], cur_exts, new_exts))

print(f"Total tools to update: {len(changes)}")
for num, name, old, new in changes[:20]:
    print(f"#{num:03d} {name}: {old} -> {new}")
if len(changes) > 20:
    print(f"... and {len(changes) - 20} more.")
