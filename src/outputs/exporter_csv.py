thonimport csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List

logger = logging.getLogger(__name__)

def _flatten_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens a media record to a single row, placing the medias array into
    a JSON-encoded string field for CSV export.
    """
    flat = dict(record)
    medias = flat.pop("medias", [])
    flat["medias_json"] = json.dumps(medias, ensure_ascii=False)
    return flat

def export_to_csv(records: Iterable[Dict[str, Any]], output_path: Path) -> Path:
    """
    Exports extraction records as CSV, with one row per record. The medias list
    is stored as a JSON string in the 'medias_json' column.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    flat_records: List[Dict[str, Any]] = [_flatten_record(r) for r in records]

    if not flat_records:
        # Create an empty file with headers only.
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "source", "author", "title", "thumbnail", "duration", "type", "error", "medias_json"])
        logger.debug("Exported empty CSV with headers to %s", output_path)
        return output_path

    fieldnames = list(flat_records[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in flat_records:
            writer.writerow(row)

    logger.debug("Exported %d record(s) to CSV: %s", len(flat_records), output_path)
    return output_path