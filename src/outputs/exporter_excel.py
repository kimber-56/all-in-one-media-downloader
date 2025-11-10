thonimport logging
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

logger = logging.getLogger(__name__)

def export_to_excel(records: Iterable[Dict[str, Any]], output_path: Path) -> Path:
    """
    Writes extraction records to an Excel workbook using pandas. Complex
    fields like 'medias' are converted to string representations.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    for record in records:
        row = dict(record)
        # Convert non-scalar fields to strings so Excel can display them.
        for key, value in list(row.items()):
            if isinstance(value, (list, dict)):
                row[key] = str(value)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)

    logger.debug("Exported %d record(s) to Excel: %s", len(rows), output_path)
    return output_path