thonimport argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from extractors.utils_parser import detect_platform
from extractors.tiktok_extractor import TikTokExtractor
from extractors.youtube_extractor import YouTubeExtractor
from extractors.instagram_extractor import InstagramExtractor
from processors.watermark_remover import remove_watermarks_from_record
from outputs.exporter_json import export_to_json
from outputs.exporter_csv import export_to_csv
from outputs.exporter_excel import export_to_excel

logger = logging.getLogger("media_downloader")

class GenericExtractor:
    """
    Fallback extractor when there is no platform-specific implementation.
    Generates a structured record with minimal, deterministic metadata.
    """

    source_name = "generic"

    def extract(self, url: str) -> Dict[str, Any]:
        title = f"Media from {self.source_name}"
        record = {
            "url": url,
            "source": self.source_name,
            "author": self._guess_author(url),
            "title": title,
            "thumbnail": "",
            "duration": 0,
            "medias": [
                {
                    "url": url,
                    "quality": "original",
                    "extension": "bin",
                    "type": "multiple",
                }
            ],
            "type": "multiple",
            "error": False,
        }
        return record

    @staticmethod
    def _guess_author(url: str) -> str:
        # Very naive guess based on path segments.
        try:
            parts = url.split("/")
            for part in parts:
                if "@" in part and len(part) > 1:
                    return part.strip("@")
        except Exception:
            pass
        return "unknown"

def setup_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

def load_settings(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        logger.info("Settings file %s not found, using defaults.", config_path)
        return {
            "default_formats": ["json"],
            "enable_watermark_removal": True,
        }

    try:
        with config_path.open("r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.debug("Loaded settings from %s", config_path)
        return settings
    except Exception as exc:
        logger.error("Failed to load settings from %s: %s", config_path, exc)
        return {
            "default_formats": ["json"],
            "enable_watermark_removal": True,
        }

def resolve_project_paths() -> Dict[str, Path]:
    # src/main.py -> src -> project root
    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent
    data_dir = project_root / "data"
    config_dir = src_dir / "config"
    return {
        "src_dir": src_dir,
        "project_root": project_root,
        "data_dir": data_dir,
        "config_dir": config_dir,
    }

def load_input_urls(input_path: Path) -> List[str]:
    if not input_path.exists():
        logger.error("Input file %s does not exist.", input_path)
        raise FileNotFoundError(f"Input file {input_path} does not exist.")

    try:
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse JSON from %s: %s", input_path, exc)
        raise

    if isinstance(data, list):
        # Either list of URLs or list of objects with 'url'
        if all(isinstance(x, str) for x in data):
            return data
        urls = [item["url"] for item in data if isinstance(item, dict) and "url" in item]
        return urls

    if isinstance(data, dict) and "urls" in data and isinstance(data["urls"], list):
        return [str(u) for u in data["urls"]]

    raise ValueError(
        f"Unsupported input format in {input_path}. Expected a list of URLs or "
        f"a list of objects with 'url' fields."
    )

def get_extractor(platform: str):
    platform = (platform or "").lower()
    if platform == "tiktok":
        return TikTokExtractor()
    if platform == "youtube":
        return YouTubeExtractor()
    if platform == "instagram":
        return InstagramExtractor()

    extractor = GenericExtractor()
    extractor.source_name = platform or "unknown"
    return extractor

def process_urls(
    urls: List[str],
    enable_watermark_removal: bool = True,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for url in urls:
        try:
            platform = detect_platform(url)
            logger.info("Processing URL: %s (platform=%s)", url, platform or "unknown")
            extractor = get_extractor(platform)
            record = extractor.extract(url)

            if enable_watermark_removal:
                record = remove_watermarks_from_record(record)

            results.append(record)
        except Exception as exc:
            logger.exception("Error processing URL %s: %s", url, exc)
            results.append(
                {
                    "url": url,
                    "source": detect_platform(url) or "unknown",
                    "author": "unknown",
                    "title": "Extraction failed",
                    "thumbnail": "",
                    "duration": 0,
                    "medias": [],
                    "type": "multiple",
                    "error": True,
                }
            )

    return results

def parse_args(argv: List[str]) -> argparse.Namespace:
    paths = resolve_project_paths()

    parser = argparse.ArgumentParser(
        description="All-in-One Media Downloader (demo implementation)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=str(paths["data_dir"] / "input_samples.json"),
        help="Path to input JSON containing URLs.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(paths["data_dir"]),
        help="Directory to write outputs into.",
    )
    parser.add_argument(
        "--formats",
        type=str,
        nargs="*",
        help="Output formats (json, csv, excel). Overrides settings file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v, -vv).",
    )

    return parser.parse_args(argv)

def main(argv: List[str]) -> int:
    args = parse_args(argv)
    setup_logging(args.verbose)

    paths = resolve_project_paths()
    config_path = paths["config_dir"] / "settings.example.json"
    settings = load_settings(config_path)

    try:
        input_path = Path(args.input)
        urls = load_input_urls(input_path)
    except Exception as exc:
        logger.error("Failed to load input URLs: %s", exc)
        return 1

    formats = args.formats or settings.get("default_formats", ["json"])
    formats = [fmt.lower() for fmt in formats]

    logger.info("Loaded %d URL(s). Output formats: %s", len(urls), ", ".join(formats))

    enable_watermark_removal = settings.get("enable_watermark_removal", True)
    records = process_urls(urls, enable_watermark_removal=enable_watermark_removal)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if "json" in formats:
        json_path = output_dir / "example_output.json"
        export_to_json(records, json_path)
        logger.info("JSON exported to %s", json_path)

    if "csv" in formats:
        csv_path = output_dir / "example_output.csv"
        export_to_csv(records, csv_path)
        logger.info("CSV exported to %s", csv_path)

    if "excel" in formats:
        excel_path = output_dir / "example_output.xlsx"
        export_to_excel(records, excel_path)
        logger.info("Excel exported to %s", excel_path)

    logger.info("Processing completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))