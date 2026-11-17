import zipfile
import json
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from apps.api.app.engines.base import BaseEngine, EngineResult

class FaviconGeneratorEngine(BaseEngine):
    """
    Image to Favicon & Web App Manifest Studio:
    Produces complete production-ready favicon suites for modern web development:
    - Multi-resolution favicon.ico (16x16, 32x32, 48x48)
    - PNG Favicons: 16x16, 32x32
    - Apple Touch Icon: 180x180
    - Android Chrome / PWA Icons: 192x192, 512x512
    - site.webmanifest (PWA configuration JSON)
    - favicon_tags.html (Copy-pasteable HTML meta tags)
    - favicon_bundle.zip (Packaged ready for deployment)
    """

    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        if not input_paths:
            raise ValueError("No input image provided for favicon generation.")

        src_path = input_paths[0]
        app_name = options.get("app_name", "My Application")
        short_name = options.get("short_name", "App")
        theme_color = options.get("theme_color", "#000000")
        background_color = options.get("background_color", "#ffffff")

        if progress_callback:
            progress_callback(10, "Loading source image...")

        src_img = Image.open(src_path)
        if src_img.mode != "RGBA":
            src_img = src_img.convert("RGBA")

        # Create output staging directory
        bundle_dir = output_dir / "favicon_assets"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # 1. Multi-resolution favicon.ico (16, 32, 48)
        if progress_callback:
            progress_callback(25, "Generating multi-resolution favicon.ico (16, 32, 48)...")
        ico_path = bundle_dir / "favicon.ico"
        ico_sizes = [(16, 16), (32, 32), (48, 48)]
        src_img.save(ico_path, format="ICO", sizes=ico_sizes)
        generated_files.append(ico_path)

        # 2. PNG Favicons
        for size in [16, 32]:
            png_path = bundle_dir / f"favicon-{size}x{size}.png"
            resized = src_img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(png_path, "PNG", optimize=True)
            generated_files.append(png_path)

        if progress_callback:
            progress_callback(50, "Generating Apple Touch and Android Chrome icons...")

        # 3. Apple Touch Icon (180x180)
        apple_path = bundle_dir / "apple-touch-icon.png"
        apple_img = src_img.resize((180, 180), Image.Resampling.LANCZOS)
        apple_img.save(apple_path, "PNG", optimize=True)
        generated_files.append(apple_path)

        # 4. Android Chrome / PWA Icons (192, 512)
        for size in [192, 512]:
            pwa_path = bundle_dir / f"android-chrome-{size}x{size}.png"
            pwa_img = src_img.resize((size, size), Image.Resampling.LANCZOS)
            pwa_img.save(pwa_path, "PNG", optimize=True)
            generated_files.append(pwa_path)

        # 5. site.webmanifest
        if progress_callback:
            progress_callback(75, "Generating PWA site.webmanifest and HTML snippet...")

        manifest_data = {
            "name": app_name,
            "short_name": short_name,
            "icons": [
                {
                    "src": "/android-chrome-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/android-chrome-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "theme_color": theme_color,
            "background_color": background_color,
            "display": "standalone"
        }
        manifest_path = bundle_dir / "site.webmanifest"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
        generated_files.append(manifest_path)

        # 6. HTML Link tags snippet
        html_content = f"""<!-- Copy and paste these tags into your HTML <head> -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="{theme_color}">
"""
        html_path = bundle_dir / "favicon_tags.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_files.append(html_path)

        # 7. Package everything into a deployable ZIP
        if progress_callback:
            progress_callback(90, "Bundling complete favicon package into ZIP archive...")

        zip_output_path = output_dir / "favicon_complete_suite.zip"
        with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in generated_files:
                zipf.write(file_path, arcname=file_path.name)

        if progress_callback:
            progress_callback(100, "Favicon suite generated successfully.")

        return EngineResult(
            output_paths=[zip_output_path],
            metrics={
                "generated_sizes": ["16x16", "32x32", "48x48", "180x180", "192x192", "512x512"],
                "included_manifest": True,
                "included_html_tags": True,
                "app_name": app_name,
                "zipped_package": True,
            }
        )
