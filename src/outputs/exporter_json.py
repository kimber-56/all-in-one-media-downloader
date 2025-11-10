thonimport json
import logging
from pathlib import Path
from typing import Any, Iterable, List, Dict

logger = logging.getLogger(__name__)

def export_to_json(records: Iterable[Dict[str, Any]], output_path: Path) -> Path:
    """
    Writes extraction records to a JSON file using UTF-8 and pretty formatting.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data: List[Dict[str, Any]] = list(records)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logger.debug("Exported %d record(s) to JSON: %s", len(data), output_path)
    return output_path