thonimport logging
from copy import deepcopy
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def _remove_watermark_from_medias(medias: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns a new media list where watermark-marked videos are replaced with
    cleaned variants when possible. This is a logical transformation that
    mimics watermark removal by preferring 'no_watermark' or 'hd_no_watermark'
    qualities and generating derived URLs when needed.
    """
    cleaned: List[Dict[str, Any]] = []

    for media in medias:
        item = deepcopy(media)
        if item.get("type") == "video":
            quality = (item.get("quality") or "").lower()
            if "watermark" in quality and "no_watermark" not in quality:
                # Simulate a derived watermark-free URL.
                original_url = item.get("url", "")
                if "?" in original_url:
                    new_url = original_url + "&clean=1"
                else:
                    new_url = original_url + "?clean=1"

                item["url"] = new_url
                item["quality"] = "no_watermark"
                logger.debug(
                    "Simulated watermark removal for video %s -> %s", original_url, new_url
                )

        cleaned.append(item)

    return cleaned

def remove_watermarks_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a full extraction record and returns a new record with the medias list
    sanitized for watermarks. The function is side-effect free.
    """
    if not isinstance(record, dict):
        logger.warning("Expected dict record, got %s", type(record))
        return record

    medias = record.get("medias")
    if not isinstance(medias, list):
        return record

    cleaned_medias = _remove_watermark_from_medias(medias)
    new_record = dict(record)
    new_record["medias"] = cleaned_medias
    return new_record