import json
from pathlib import Path

tools_path = Path("packages/tool-registry/tools.json")
with open(tools_path, "r", encoding="utf-8") as f:
    tools = json.load(f)

print(f"Total tools loaded: {len(tools)}")

anomalies = []

for t in tools:
    num = t.get("number", 0)
    name = t.get("name", "")
    op = t.get("operation", "")
    cat = t.get("category", "")
    exts = t.get("accepted_extensions", [])
    mimes = t.get("accepted_mimes", [])
    slug = t.get("slug", "")

    op_l = op.lower()
    name_l = name.lower()

    # Case 1: PDF to something
    # Name contains "pdf to " or op starts with "pdf_to_" or "convert_pdf_"
    if "pdf to " in name_l or op_l.startswith("pdf_to_") or "scanned_pdf_to" in op_l or "pdf_tables_to" in op_l:
        if exts != [".pdf"]:
            anomalies.append({
                "num": num,
                "name": name,
                "op": op,
                "type": "PDF to X",
                "current_exts": exts,
                "expected": [".pdf"],
                "expected_mime": ["application/pdf"]
            })

    # Case 2: PDF extraction tools (PDF Image Extractor, etc.)
    elif name_l.startswith("pdf ") and any(k in name_l for k in ["extractor", "remover", "counter", "inspector", "linearizer", "portfolio", "dimension"]):
        if exts != [".pdf"]:
            anomalies.append({
                "num": num,
                "name": name,
                "op": op,
                "type": "PDF Utility",
                "current_exts": exts,
                "expected": [".pdf"],
                "expected_mime": ["application/pdf"]
            })

    # Case 3: X to PDF
    # e.g., "word to pdf", "excel to pdf", "powerpoint to pdf", "jpg to pdf", "epub to pdf", etc.
    elif " to pdf" in name_l:
        # Check source
        if "word to pdf" in name_l:
            exp = [".docx", ".doc", ".rtf", ".odt"]
            exp_mime = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]
        elif "excel to pdf" in name_l:
            exp = [".xlsx", ".xls", ".csv", ".ods"]
            exp_mime = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel", "text/csv"]
        elif "powerpoint to pdf" in name_l:
            exp = [".pptx", ".ppt", ".odp"]
            exp_mime = ["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/vnd.ms-powerpoint"]
        elif any(k in name_l for k in ["jpg to pdf", "jpeg to pdf", "png to pdf", "webp to pdf", "image to pdf", "tiff to pdf", "svg to pdf"]):
            exp = [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".svg", ".bmp"]
            exp_mime = ["image/jpeg", "image/png", "image/webp", "image/tiff", "image/svg+xml"]
        elif "txt to pdf" in name_l or "text to pdf" in name_l:
            exp = [".txt", ".text"]
            exp_mime = ["text/plain"]
        elif "html to pdf" in name_l:
            exp = [".html", ".htm"]
            exp_mime = ["text/html"]
        elif "csv to pdf" in name_l:
            exp = [".csv"]
            exp_mime = ["text/csv"]
        elif "epub to pdf" in name_l:
            exp = [".epub"]
            exp_mime = ["application/epub+zip"]
        elif "rtf to pdf" in name_l:
            exp = [".rtf"]
            exp_mime = ["application/rtf", "text/rtf"]
        elif "odt to pdf" in name_l:
            exp = [".odt"]
            exp_mime = ["application/vnd.oasis.opendocument.text"]
        elif "ods to pdf" in name_l:
            exp = [".ods"]
            exp_mime = ["application/vnd.oasis.opendocument.spreadsheet"]
        elif "odp to pdf" in name_l:
            exp = [".odp"]
            exp_mime = ["application/vnd.oasis.opendocument.presentation"]
        elif "markdown to pdf" in name_l:
            exp = [".md", ".markdown", ".txt"]
            exp_mime = ["text/markdown", "text/plain"]
        else:
            exp = None

        if exp and set(exts) != set(exp):
            anomalies.append({
                "num": num,
                "name": name,
                "op": op,
                "type": "X to PDF",
                "current_exts": exts,
                "expected": exp,
                "expected_mime": exp_mime
            })

for a in anomalies:
    print(f"#{a['num']:03d} [{a['type']}] {a['name']} ({a['op']}): CURRENT={a['current_exts']} -> EXPECTED={a['expected']}")

print(f"\nTotal anomalies found: {len(anomalies)}")
