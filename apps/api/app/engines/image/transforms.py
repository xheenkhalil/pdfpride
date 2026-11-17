import json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult

class ImageFormatConvertEngine(BaseEngine):
    """Converts images between JPG, PNG, WebP, TIFF, BMP."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        raw_fmt = options.get("format", "png")
        target_format = raw_fmt.lower() if isinstance(raw_fmt, str) else "png"
        if target_format == "jpeg":
            target_format = "jpg"
        out_path = output_dir / f"{src.stem}.{target_format}"

        im = Image.open(src)
        if target_format in ("jpg", "jpeg") and im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        im.save(out_path)
        return EngineResult(output_paths=[out_path], metrics={"format": target_format})


class ImageCompressEngine(BaseEngine):
    """Compresses raster images."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        raw_q = options.get("quality", 75)
        try:
            quality = int(raw_q)
        except Exception:
            quality = 75
        out_path = output_dir / f"compressed_{src.name}"

        im = Image.open(src)
        fmt = im.format or "JPEG"
        if fmt == "JPEG" and im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        im.save(out_path, format=fmt, quality=quality, optimize=True)
        return EngineResult(output_paths=[out_path], metrics={"quality": quality})


class ImageResizeEngine(BaseEngine):
    """Resizes images by width/height or percentage."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"resized_{src.name}"
        raw_w = options.get("width", 1280)
        try:
            width = int(raw_w)
        except Exception:
            width = 1280

        im = Image.open(src)
        orig_w, orig_h = im.size
        aspect = orig_h / orig_w
        height = int(width * aspect)

        resized = im.resize((width, height), Image.Resampling.LANCZOS)
        resized.save(out_path)
        return EngineResult(output_paths=[out_path], metrics={"width": width, "height": height})


class ImageStripEXIFEngine(BaseEngine):
    """Removes EXIF metadata, GPS, timestamps."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"clean_{src.name}"

        im = Image.open(src)
        data = list(im.getdata())
        image_without_exif = Image.new(im.mode, im.size)
        image_without_exif.putdata(data)
        image_without_exif.save(out_path)
        return EngineResult(output_paths=[out_path], metrics={"exif_stripped": True})


class ImageWatermarkEngine(BaseEngine):
    """Applies watermark text or stamp to a raster image."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"watermarked_{src.name}"
        raw_text = options.get("text", "CONFIDENTIAL")
        text = raw_text if isinstance(raw_text, str) and raw_text else "CONFIDENTIAL"

        im = Image.open(src).convert("RGBA")
        txt_layer = Image.new("RGBA", im.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        cx, cy = im.size[0] // 2, im.size[1] // 2
        draw.text((max(0, cx - 50), cy), text, fill=(208, 0, 0, 128))
        watermarked = Image.alpha_composite(im, txt_layer)

        fmt = im.format or "PNG"
        if fmt == "JPEG" or out_path.suffix.lower() in [".jpg", ".jpeg"]:
            watermarked = watermarked.convert("RGB")
        watermarked.save(out_path)
        return EngineResult(output_paths=[out_path], metrics={"watermarked": True, "text": text})


class ImageMetadataEngine(BaseEngine):
    """Inspects and exports image metadata as JSON or sanitized image."""
    def execute(self, input_paths: List[Path], output_dir: Path, options: Dict[str, Any], progress_callback=None) -> EngineResult:
        src = input_paths[0]
        out_path = output_dir / f"{src.stem}_image_meta.json"
        im = Image.open(src)
        info = {
            "format": im.format or "PNG",
            "mode": im.mode,
            "width": im.size[0],
            "height": im.size[1],
            "info": {str(k): str(v) for k, v in getattr(im, "info", {}).items()}
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
        return EngineResult(output_paths=[out_path], metrics=info)
