import json
from pathlib import Path

def get_tool_formats(t):
    num = t.get("number", 0)
    name = t.get("name", "")
    op = t.get("operation", "").lower()
    cat = t.get("category", "")
    slug = t.get("slug", "")

    # 1. PDF Organization & Management (1 - 32)
    if 1 <= num <= 32:
        return [".pdf"], ["application/pdf"]

    # 2. PDF Conversion (33 - 72)
    if 33 <= num <= 45: # PDF to Word, Excel, PPTX, JPG, JPEG, PNG, WebP, TIFF, TXT, HTML, CSV, EPUB, SVG
        return [".pdf"], ["application/pdf"]
    if num == 46: # Word to PDF
        return [".docx", ".doc", ".rtf", ".odt"], [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "application/rtf",
            "application/vnd.oasis.opendocument.text"
        ]
    if num == 47: # Excel to PDF
        return [".xlsx", ".xls", ".csv", ".ods"], [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
            "application/vnd.oasis.opendocument.spreadsheet"
        ]
    if num == 48: # PowerPoint to PDF
        return [".pptx", ".ppt", ".odp"], [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
            "application/vnd.oasis.opendocument.presentation"
        ]
    if num in (49, 50): # JPG / JPEG to PDF
        return [".jpg", ".jpeg"], ["image/jpeg"]
    if num == 51: # PNG to PDF
        return [".png"], ["image/png"]
    if num == 52: # WebP to PDF
        return [".webp"], ["image/webp"]
    if num == 53: # TIFF to PDF
        return [".tiff", ".tif"], ["image/tiff"]
    if num == 54: # SVG to PDF
        return [".svg"], ["image/svg+xml"]
    if num == 55: # TXT to PDF
        return [".txt", ".text"], ["text/plain"]
    if num == 56: # HTML to PDF
        return [".html", ".htm"], ["text/html"]
    if num == 57: # CSV to PDF
        return [".csv"], ["text/csv"]
    if num == 58: # EPUB to PDF
        return [".epub"], ["application/epub+zip"]
    if num == 59: # RTF to PDF
        return [".rtf"], ["application/rtf", "text/rtf"]
    if num == 60: # ODT to PDF
        return [".odt"], ["application/vnd.oasis.opendocument.text"]
    if num == 61: # ODS to PDF
        return [".ods"], ["application/vnd.oasis.opendocument.spreadsheet"]
    if num == 62: # ODP to PDF
        return [".odp"], ["application/vnd.oasis.opendocument.presentation"]
    if num in (63, 64): # Markdown to PDF, Markdown to DOCX
        return [".md", ".markdown", ".txt"], ["text/markdown", "text/plain"]
    if num in (65, 66): # DOCX to HTML, DOCX to TXT
        return [".docx", ".doc"], [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]
    if num == 67: # XLSX to CSV
        return [".xlsx", ".xls"], [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]
    if num == 68: # CSV to XLSX
        return [".csv"], ["text/csv"]
    if num == 69: # PPTX to Images
        return [".pptx", ".ppt"], [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint"
        ]
    if num == 70: # HTML to Images
        return [".html", ".htm"], ["text/html"]
    if num == 71: # JSON to CSV
        return [".json"], ["application/json"]
    if num == 72: # XML to JSON
        return [".xml"], ["application/xml", "text/xml"]

    # 3. PDF Compression & Optimization (73 - 90)
    if 73 <= num <= 90:
        return [".pdf"], ["application/pdf"]

    # 4. PDF Editing (91 - 115)
    if 91 <= num <= 115:
        return [".pdf"], ["application/pdf"]

    # 5. PDF Security & Protection (116 - 134)
    if 116 <= num <= 134:
        return [".pdf"], ["application/pdf"]

    # 6. PDF Forms (135 - 146)
    if 135 <= num <= 146:
        return [".pdf"], ["application/pdf"]

    # 7. OCR & Document Intelligence (147 - 178)
    if num == 148: # OCR Images
        return [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"], [
            "image/jpeg", "image/png", "image/webp", "image/tiff", "image/bmp"
        ]
    if num == 155: # Extract Images from Documents
        return [".pdf", ".docx", ".pptx"], [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ]
    if 147 <= num <= 178:
        return [".pdf"], ["application/pdf"]

    # 8. Image Studio (179 - 209, 441)
    if num == 193: # Image to PDF
        return [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"], [
            "image/jpeg", "image/png", "image/webp", "image/tiff", "image/bmp"
        ]
    if num == 194: # PDF to Image
        return [".pdf"], ["application/pdf"]
    if num == 441: # Favicon Studio
        return [".png", ".jpg", ".jpeg", ".webp", ".svg"], [
            "image/png", "image/jpeg", "image/webp", "image/svg+xml"
        ]
    if 179 <= num <= 209:
        return [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".svg", ".bmp", ".ico"], [
            "image/jpeg", "image/png", "image/webp", "image/tiff", "image/svg+xml", "image/bmp", "image/x-icon"
        ]

    # 9. Word Document Utilities (210 - 221)
    if 210 <= num <= 221:
        return [".docx", ".doc"], [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]

    # 10. Excel & Spreadsheet Utilities (222 - 241)
    if num == 222: # Excel to PDF
        return [".xlsx", ".xls", ".csv", ".ods"], [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
            "application/vnd.oasis.opendocument.spreadsheet"
        ]
    if num in (224, 236, 237, 238, 241): # CSV to Excel, CSV Merger, CSV Splitter, CSV to JSON, CSV to TSV
        return [".csv"], ["text/csv"]
    if num in (226, 239): # JSON to Excel, JSON to CSV
        return [".json"], ["application/json"]
    if num == 240: # TSV to CSV
        return [".tsv"], ["text/tab-separated-values"]
    if 223 <= num <= 241:
        return [".xlsx", ".xls"], [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]

    # 11. PowerPoint Utilities (242 - 249)
    if 242 <= num <= 249:
        return [".pptx", ".ppt"], [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint"
        ]

    # 12. General File Utilities (250 - 268)
    if num in (266, 268): # QR Code Reader, Barcode Reader
        return [".png", ".jpg", ".jpeg", ".webp"], [
            "image/png", "image/jpeg", "image/webp"
        ]
    if 250 <= num <= 268:
        return [".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".jpeg", ".png", ".webp", ".zip", ".txt", ".csv", ".json"], ["*/*"]

    # 13. Text & Productivity Utilities (269 - 294)
    if num == 269: # Word Counter
        return [".txt", ".md", ".docx", ".pdf"], [
            "text/plain", "text/markdown",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/pdf"
        ]
    if num in (282, 283): # Text to PDF, Text to DOCX
        return [".txt", ".text"], ["text/plain"]
    if num in (284, 285, 286): # Markdown Editor, Markdown to PDF, Markdown to DOCX
        return [".md", ".markdown", ".txt"], ["text/markdown", "text/plain"]
    if num in (287, 288): # HTML to PDF, HTML to Image
        return [".html", ".htm"], ["text/html"]
    if num in (289, 290): # JSON Formatter, JSON Validator
        return [".json"], ["application/json"]
    if num in (291, 292): # XML Formatter, XML Validator
        return [".xml"], ["application/xml", "text/xml"]
    if num in (293, 294): # YAML Formatter, YAML Validator
        return [".yaml", ".yml"], ["application/x-yaml", "text/yaml"]
    if 270 <= num <= 281:
        return [".txt", ".text", ".md", ".json", ".csv"], [
            "text/plain", "text/markdown", "application/json", "text/csv"
        ]

    # 14. Batch Processing (295 - 311)
    if 295 <= num <= 299: # Batch PDF
        return [".pdf"], ["application/pdf"]
    if num in (300, 301): # Batch Image
        return [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".svg"], [
            "image/jpeg", "image/png", "image/webp", "image/tiff", "image/svg+xml"
        ]
    if num == 302: # Batch Document Conversion
        return [".pdf", ".docx", ".xlsx", ".pptx", ".txt"], [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "text/plain"
        ]
    if num == 303: # Batch OCR Processing
        return [".pdf", ".jpg", ".jpeg", ".png"], [
            "application/pdf", "image/jpeg", "image/png"
        ]
    if 304 <= num <= 311:
        return [".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".png", ".zip", ".txt"], ["*/*"]

    # 15. Cloud Workspace, Sharing, User Account, Admin, Subscription, Advanced (312 - 440)
    return [".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".jpeg", ".png", ".webp", ".zip", ".txt", ".csv"], [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/png",
        "text/plain"
    ]

def update_file(path_str):
    p = Path(path_str)
    if not p.exists():
        print(f"File not found: {path_str}")
        return
    with open(p, "r", encoding="utf-8") as f:
        tools = json.load(f)

    updated_count = 0
    for t in tools:
        exts, mimes = get_tool_formats(t)
        if t.get("accepted_extensions") != exts or t.get("accepted_mimes") != mimes:
            t["accepted_extensions"] = exts
            t["accepted_mimes"] = mimes
            updated_count += 1

    with open(p, "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)

    print(f"Successfully updated {updated_count} tools in {path_str}")

update_file("packages/tool-registry/tools.json")
update_file("apps/web/src/data/tools.json")
