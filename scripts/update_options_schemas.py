import json
from pathlib import Path

SCHEMAS = {
    "rotate_pdf": {
        "type": "object",
        "properties": {
            "rotation_type": {
                "type": "string",
                "title": "Rotation Cycle",
                "enum": ["right_90", "left_90", "flip_180", "reset_0"],
                "default": "right_90"
            },
            "page_selection": {
                "type": "string",
                "title": "Pages to Rotate",
                "enum": ["all", "odd", "even", "custom"],
                "default": "all"
            },
            "page_range": {
                "type": "string",
                "title": "Custom Page Range (if custom selected)",
                "default": ""
            }
        }
    },
    "batch_pdf_rotation": {
        "type": "object",
        "properties": {
            "rotation_type": {
                "type": "string",
                "title": "Rotation Cycle",
                "enum": ["right_90", "left_90", "flip_180", "reset_0"],
                "default": "right_90"
            }
        }
    },
    "compress_pdf": {
        "type": "object",
        "properties": {
            "compression_mode": {
                "type": "string",
                "title": "Compression Level",
                "enum": ["recommended", "extreme", "low", "target_size"],
                "default": "recommended"
            },
            "target_size_mb": {
                "type": "string",
                "title": "Target Size (e.g. 1.5 MB or 500 KB)",
                "default": "1.0 MB"
            }
        }
    },
    "duplicate_pdf_pages": {
        "type": "object",
        "properties": {
            "duplicate_mode": {
                "type": "string",
                "title": "Pages to Duplicate",
                "enum": ["all", "selected"],
                "default": "all"
            },
            "copies": {
                "type": "string",
                "title": "Number of Copies",
                "enum": ["2", "3", "4", "5"],
                "default": "2"
            },
            "placement": {
                "type": "string",
                "title": "Placement Order",
                "enum": ["consecutive", "end"],
                "default": "consecutive"
            },
            "page_range": {
                "type": "string",
                "title": "Custom Pages to Duplicate",
                "default": ""
            }
        }
    },
    "reverse_pdf_pages": {
        "type": "object",
        "properties": {
            "reverse_scope": {
                "type": "string",
                "title": "Reverse Scope",
                "enum": ["all_pages", "odd_only", "even_only"],
                "default": "all_pages"
            }
        }
    },
    "delete_pdf_pages": {
        "type": "object",
        "properties": {
            "pages_to_delete": {
                "type": "string",
                "title": "Pages to Delete (e.g. 1, 3-5, odd, even, last)",
                "default": "1"
            }
        }
    },
    "extract_pdf_pages": {
        "type": "object",
        "properties": {
            "pages_to_extract": {
                "type": "string",
                "title": "Pages to Extract (e.g. 1, 3-5, odd, even)",
                "default": "1"
            },
            "output_mode": {
                "type": "string",
                "title": "Extraction Output",
                "enum": ["single_pdf", "separate_pdfs"],
                "default": "single_pdf"
            }
        }
    },
    "split_pdf": {
        "type": "object",
        "properties": {
            "split_mode": {
                "type": "string",
                "title": "Split Method",
                "enum": ["all", "range", "every_n"],
                "default": "all"
            },
            "page_ranges": {
                "type": "string",
                "title": "Page Ranges (if range selected)",
                "default": "1-2"
            },
            "every_n_pages": {
                "type": "string",
                "title": "Every N Pages (if every N selected)",
                "enum": ["1", "2", "3", "5", "10"],
                "default": "2"
            }
        }
    },
    "organize_pdf_pages": {
        "type": "object",
        "properties": {
            "page_order": {
                "type": "string",
                "title": "New Page Order (e.g. 3, 1, 2, 4 or reverse, odd_first)",
                "default": "reverse"
            }
        }
    },
    "reorder_pdf_pages": {
        "type": "object",
        "properties": {
            "page_order": {
                "type": "string",
                "title": "New Page Order (e.g. 3, 1, 2, 4 or reverse, odd_first)",
                "default": "reverse"
            }
        }
    },
    "watermark_pdf": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "title": "Watermark Stamp Text",
                "default": "CONFIDENTIAL"
            }
        }
    },
    "protect_pdf": {
        "type": "object",
        "properties": {
            "password": {
                "type": "string",
                "title": "Document Protection Password",
                "default": "SecureDoc2026!"
            }
        }
    },
    "image_to_favicon": {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "title": "Web Application Title",
                "default": "My Application"
            },
            "short_name": {
                "type": "string",
                "title": "Short PWA Name",
                "default": "App"
            },
            "theme_color": {
                "type": "string",
                "title": "Brand Theme Hex Color",
                "default": "#D00000"
            }
        }
    }
}

# Also apply compression schema to compression variations (tools 73-90, 296)
COMPRESSION_OPS = [
    "compress_pdf", "batch_pdf_compression", "basic_pdf_compression",
    "recommended_pdf_compression", "strong_pdf_compression", "extreme_pdf_compression"
]

def update_file(path_str):
    p = Path(path_str)
    if not p.exists():
        print(f"File not found: {path_str}")
        return
    with open(p, "r", encoding="utf-8") as f:
        tools = json.load(f)

    updated = 0
    for t in tools:
        op = t.get("operation", "")
        if op in SCHEMAS:
            t["options_schema"] = SCHEMAS[op]
            updated += 1
        elif op in COMPRESSION_OPS:
            t["options_schema"] = SCHEMAS["compress_pdf"]
            updated += 1

    with open(p, "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)

    print(f"Updated {updated} tool options schemas in {path_str}")

update_file("packages/tool-registry/tools.json")
update_file("apps/web/src/data/tools.json")
