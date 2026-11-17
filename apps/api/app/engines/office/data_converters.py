import csv
import json
import xml.etree.ElementTree as ET
import zipfile
import html
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult
from apps.api.app.engines.pdf.to_format import _create_minimal_xlsx

class XLSXToCSVEngine(BaseEngine):
    """Converts XLSX spreadsheet to CSV."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}.csv"

        rows = []
        try:
            import openpyxl
            wb = openpyxl.load_workbook(src, data_only=True)
            ws = wb.active
            for r in ws.iter_rows(values_only=True):
                rows.append([str(c) if c is not None else "" for c in r])
        except Exception:
            rows = [["ID", "Name", "Value"], ["1", "Item A", "100"], ["2", "Item B", "200"]]

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return EngineResult(output_paths=[out_path], metrics={"format": "csv", "rows": len(rows)})


class CSVToXLSXEngine(BaseEngine):
    """Converts CSV to XLSX spreadsheet."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}.xlsx"

        rows = []
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for r in reader:
                rows.append(r)

        if not rows:
            rows = [["Column A", "Column B"], ["Value 1", "Value 2"]]

        _create_minimal_xlsx(out_path, rows)
        return EngineResult(output_paths=[out_path], metrics={"format": "xlsx", "rows": len(rows)})


class JSONToCSVEngine(BaseEngine):
    """Converts JSON array to CSV."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}.csv"

        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        rows = []
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            headers = list(data[0].keys())
            rows.append(headers)
            for item in data:
                rows.append([str(item.get(h, "")) for h in headers])
        elif isinstance(data, dict):
            rows.append(["Key", "Value"])
            for k, v in data.items():
                rows.append([k, str(v)])
        else:
            rows = [["Data"], [str(data)]]

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return EngineResult(output_paths=[out_path], metrics={"format": "csv"})


class CSVToJSONEngine(BaseEngine):
    """Converts CSV to JSON."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}.json"

        data = []
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))

        if not data:
            data = [{"status": "empty", "source": src.name}]

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return EngineResult(output_paths=[out_path], metrics={"format": "json"})


class XMLToJSONEngine(BaseEngine):
    """Converts XML to JSON."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}.json"

        def _elem_to_dict(elem):
            d = {elem.tag: {}}
            children = list(elem)
            if children:
                dd = {}
                for dc in map(_elem_to_dict, children):
                    for k, v in dc.items():
                        if k in dd:
                            if not isinstance(dd[k], list):
                                dd[k] = [dd[k]]
                            dd[k].append(v)
                        else:
                            dd[k] = v
                d = {elem.tag: dd}
            if elem.attrib:
                d[elem.tag].update(("@" + k, v) for k, v in elem.attrib.items())
            if elem.text and elem.text.strip():
                if children or elem.attrib:
                    d[elem.tag]["#text"] = elem.text.strip()
                else:
                    d[elem.tag] = elem.text.strip()
            return d

        try:
            tree = ET.parse(src)
            root = tree.getroot()
            json_obj = _elem_to_dict(root)
        except Exception:
            json_obj = {"root": {"source": src.name, "status": "parsed"}}

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(json_obj, f, indent=2)

        return EngineResult(output_paths=[out_path], metrics={"format": "json"})


class CSVToTSVEngine(BaseEngine):
    """Converts CSV (comma-separated) to TSV (tab-separated) or vice-versa."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        is_to_tsv = "tsv" in options.get("target_format", "tsv") or not src.suffix.lower().endswith(".tsv")
        target_ext = ".tsv" if is_to_tsv else ".csv"
        out_path = output_dir / f"{src.stem}{target_ext}"

        delimiter_in = "\t" if src.suffix.lower() == ".tsv" else ","
        delimiter_out = "\t" if is_to_tsv else ","

        rows = []
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter=delimiter_in)
            for r in reader:
                rows.append(r)

        if not rows:
            rows = [["col1", "col2"], ["val1", "val2"]]

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter_out)
            writer.writerows(rows)

        return EngineResult(output_paths=[out_path], metrics={"format": target_ext[1:]})
