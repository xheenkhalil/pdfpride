import os
import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from apps.api.app.engines import get_engine, BaseEngine
from apps.api.app.engines.pdf.to_format import _create_minimal_xlsx, _create_minimal_docx

def create_mock_pdf(path: Path):
    try:
        import fitz
        doc = fitz.open()
        p = doc.new_page(width=595, height=842)
        p.insert_text((50, 80), "PDF Pride Test Document", fontsize=20)
        p.insert_text((50, 120), "Item A    Category 1    $120.00", fontsize=12)
        p.insert_text((50, 140), "Item B    Category 2    $240.00", fontsize=12)
        doc.save(str(path))
        doc.close()
    except Exception:
        # Minimal PDF
        with open(path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj<<>>endobj\nxref\n0 2\n0000000000 65535 f\n0000000010 00000 n\ntrailer<< /Size 2 /Root 1 0 R >>\nstartxref\n30\n%%EOF")

def create_mock_image(path: Path):
    from PIL import Image
    im = Image.new("RGBA", (256, 256), color=(208, 0, 0, 255))
    im.save(path)

def create_mock_docx(path: Path):
    _create_minimal_docx(path, ["Header Paragraph", "Second paragraph of Word document."])

def create_mock_xlsx(path: Path):
    _create_minimal_xlsx(path, [["Column 1", "Column 2"], ["Data A", "Data B"]])

def create_mock_csv(path: Path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("ColA,ColB,ColC\n1,2,3\n4,5,6\n")

def create_mock_json(path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([{"name": "Alpha", "val": 10}, {"name": "Beta", "val": 20}], f)

def create_mock_xml(path: Path):
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0"?><data><item id="1">Alpha</item></data>')

def create_mock_txt(path: Path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("Line 1\nLine 2 text content\nLine 3.")

def run_all_tool_tests():
    # Load tools list
    tools_paths = [
        Path(__file__).resolve().parent.parent / "src" / "data" / "tools.json",
        Path("./apps/web/src/data/tools.json"),
        Path("./packages/tool-registry/tools.json"),
    ]
    tools = []
    for tp in tools_paths:
        if tp.exists():
            with open(tp, "r", encoding="utf-8") as f:
                tools = json.load(f)
            break

    if not tools:
        print("ERROR: tools.json not found!")
        return False

    print("=" * 80)
    print(f"PDF PRIDE — AUTOMATED TEST HARNESS FOR ALL {len(tools)} REGISTERED CAPABILITIES")
    print("=" * 80)

    passed = 0
    failed = 0
    failures = []

    with tempfile.TemporaryDirectory() as temp_dir_str:
        work_dir = Path(temp_dir_str)
        fixtures_dir = work_dir / "fixtures"
        fixtures_dir.mkdir(parents=True, exist_ok=True)

        # Pre-create test fixtures
        pdf_fixture = fixtures_dir / "sample.pdf"
        pdf_fixture_2 = fixtures_dir / "sample2.pdf"
        create_mock_pdf(pdf_fixture)
        create_mock_pdf(pdf_fixture_2)

        img_fixture = fixtures_dir / "sample.png"
        create_mock_image(img_fixture)

        docx_fixture = fixtures_dir / "sample.docx"
        create_mock_docx(docx_fixture)

        xlsx_fixture = fixtures_dir / "sample.xlsx"
        create_mock_xlsx(xlsx_fixture)

        csv_fixture = fixtures_dir / "sample.csv"
        create_mock_csv(csv_fixture)

        json_fixture = fixtures_dir / "sample.json"
        create_mock_json(json_fixture)

        xml_fixture = fixtures_dir / "sample.xml"
        create_mock_xml(xml_fixture)

        txt_fixture = fixtures_dir / "sample.txt"
        create_mock_txt(txt_fixture)

        for tool in tools:
            tool_id = tool.get("id", "N/A")
            num = tool.get("number", 0)
            name = tool.get("name", "Unknown")
            op = tool.get("operation", "")
            badge = tool.get("badge", "")

            # Select suitable input fixture
            op_lower = op.lower()
            cat_name = tool.get("category", "").lower()
            cat_id = tool.get("category_id", 0)

            if any(k in op_lower for k in ["word_to", "docx_to"]):
                inputs = [docx_fixture]
            elif any(k in op_lower for k in ["excel_to", "xlsx_to"]):
                inputs = [xlsx_fixture]
            elif "json_to" in op_lower:
                inputs = [json_fixture]
            elif "xml_to" in op_lower:
                inputs = [xml_fixture]
            elif "csv_to" in op_lower:
                inputs = [csv_fixture]
            elif any(k in op_lower for k in ["txt_to", "text_to", "markdown"]):
                inputs = [txt_fixture]
            elif op_lower.startswith("pdf_to_") or "pdf_image" in op_lower or "extract_powerpoint" in op_lower:
                inputs = [pdf_fixture]
            elif any(k in op_lower for k in ["image", "jpg_to", "jpeg_to", "png_to", "webp_to", "tiff_to", "svg_to", "favicon", "exif"]) or cat_id == 8 or "image studio" in cat_name:
                inputs = [img_fixture]
            elif "merge" in op_lower:
                inputs = [pdf_fixture, pdf_fixture_2]
            else:
                inputs = [pdf_fixture]

            # Execute engine in isolated sub-directory
            tool_output_dir = work_dir / f"out_{num:03d}_{op}"
            tool_output_dir.mkdir(parents=True, exist_ok=True)

            # Safely extract options schema defaults
            raw_props = tool.get("options_schema", {}).get("properties", {})
            exec_options = {}
            for k, v in raw_props.items():
                if isinstance(v, dict) and "default" in v:
                    exec_options[k] = v["default"]

            # Sensible defaults for specialized engines
            if "compress" in op_lower:
                exec_options.setdefault("profile", "balanced")
            if "rotate" in op_lower:
                exec_options.setdefault("angle", 90)
            if "protect" in op_lower or "encrypt" in op_lower:
                exec_options.setdefault("password", "SecurePride2026")
            if "watermark" in op_lower:
                exec_options.setdefault("text", "CONFIDENTIAL")

            try:
                engine = get_engine(op)
                res = engine.execute(
                    input_paths=inputs,
                    output_dir=tool_output_dir,
                    options=exec_options
                )

                if not res.output_paths:
                    raise ValueError("Engine completed but produced zero output paths!")

                first_out = res.output_paths[0]
                if not first_out.exists():
                    raise FileNotFoundError(f"Output file does not exist: {first_out}")

                if first_out.stat().st_size == 0:
                    raise ValueError(f"Output file is 0 bytes: {first_out}")

                out_ext = first_out.suffix.lower()

                # CRITICAL VERIFICATION: Strictly assert target format compliance
                if "_to_pdf" in op_lower or op_lower.endswith("to_pdf") or op_lower.startswith("pdf_to_pdf"):
                    if out_ext != ".pdf":
                        raise AssertionError(f"VIOLATION: {name} expected .pdf but produced {out_ext}!")

                elif any(k in op_lower for k in ["pdf_to_excel", "pdf_to_xlsx", "tables_to_excel", "extract_tables", "csv_to_xlsx"]):
                    if out_ext != ".xlsx":
                        raise AssertionError(f"VIOLATION: {name} expected authentic .xlsx but produced {out_ext}!")

                elif any(k in op_lower for k in ["pdf_to_word", "pdf_to_docx", "markdown_to_docx"]):
                    if out_ext != ".docx":
                        raise AssertionError(f"VIOLATION: {name} expected authentic .docx but produced {out_ext}!")

                elif any(k in op_lower for k in ["pdf_to_txt", "docx_to_txt", "extract_text"]):
                    if out_ext != ".txt":
                        raise AssertionError(f"VIOLATION: {name} expected .txt but produced {out_ext}!")

                elif any(k in op_lower for k in ["pdf_to_html", "docx_to_html"]):
                    if out_ext != ".html":
                        raise AssertionError(f"VIOLATION: {name} expected .html but produced {out_ext}!")

                elif any(k in op_lower for k in ["pdf_to_csv", "xlsx_to_csv", "excel_to_csv", "json_to_csv"]):
                    if out_ext != ".csv":
                        raise AssertionError(f"VIOLATION: {name} expected .csv but produced {out_ext}!")

                elif "csv_to_tsv" in op_lower:
                    if out_ext != ".tsv":
                        raise AssertionError(f"VIOLATION: {name} expected .tsv but produced {out_ext}!")

                elif "pdf_to_svg" in op_lower:
                    if out_ext != ".svg":
                        raise AssertionError(f"VIOLATION: {name} expected .svg but produced {out_ext}!")

                elif any(k in op_lower for k in ["pdf_to_jpg", "pdf_to_jpeg"]):
                    if out_ext not in [".jpg", ".jpeg"]:
                        raise AssertionError(f"VIOLATION: {name} expected .jpg but produced {out_ext}!")

                elif "pdf_to_png" in op_lower:
                    if out_ext != ".png":
                        raise AssertionError(f"VIOLATION: {name} expected .png but produced {out_ext}!")

                elif "favicon" in op_lower:
                    if out_ext not in [".zip", ".ico", ".png"]:
                        raise AssertionError(f"VIOLATION: {name} expected .zip or .ico but produced {out_ext}!")

                if "compress" in op_lower:
                    if inputs[0].suffix == ".pdf":
                        orig_s = inputs[0].stat().st_size
                        comp_s = first_out.stat().st_size
                        if comp_s > orig_s:
                            raise AssertionError(f"VIOLATION: Compression increased size ({orig_s} -> {comp_s})!")

                print(f"[PASS] Tool #{num:03d} [{badge}] {name:<35} -> Generated: {first_out.name} ({first_out.stat().st_size} bytes)")
                passed += 1

            except Exception as e:
                print(f"[FAIL] Tool #{num:03d} [{badge}] {name:<35} -> ERROR: {str(e)}")
                failed += 1
                failures.append({"number": num, "name": name, "error": str(e)})

    print("=" * 80)
    print(f"AUDIT COMPLETE: {passed} PASSED | {failed} FAILED | TOTAL: {len(tools)}")
    print("=" * 80)

    if failed == 0:
        print("SUCCESS: All tools verified. Zero format violations detected!")
        return True
    else:
        print(f"ATTENTION: {failed} tools failed verification.")
        for f in failures[:5]:
            print(f"  - #{f['number']} {f['name']}: {f['error']}")
        return False

if __name__ == "__main__":
    success = run_all_tool_tests()
    sys.exit(0 if success else 1)
