thonimport hashlib
import logging
from typing import Any, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class InstagramExtractor:
    """
    Simulated Instagram extractor that supports both single media posts and
    slideshow-style posts (multiple images).
    """

    source_name = "instagram"

    def extract(self, url: str) -> Dict[str, Any]:
        logger.debug("Extracting Instagram URL: %s", url)
        shortcode = self._shortcode_from_url(url)
        author = self._extract_author(url)
        title = f"Instagram post {shortcode} by {author}"

        is_slideshow = self._is_slideshow(shortcode)
        if is_slideshow:
            medias = self._build_slideshow_medias(shortcode)
            media_type = "multiple"
            duration_ms = 0
        else:
            medias = self._build_single_media(shortcode)
            media_type = "image"
            duration_ms = 0

        thumbnail = f"https://dummy.instagramcdn.com/p/{shortcode}/thumbnail.jpg"

        record = {
            "url": url,
            "source": self.source_name,
            "author": author,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration_ms,
            "medias": medias,
            "type": media_type,
            "error": False,
        }
        logger.debug("Instagram extraction result: %s", record)
        return record

    @staticmethod
    def _shortcode_from_url(url: str) -> str:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"p", "reel"}:
            return parts[1]
        # Fallback hash
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]

    @staticmethod
    def _extract_author(url: str) -> str:
        parsed = urlparse(url)
        # Sometimes pattern like /<username>/p/<shortcode>/
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 3 and parts[1] in {"p", "reel"}:
            return parts[0]
        return "unknown"

    @staticmethod
    def _is_slideshow(shortcode: str) -> bool:
        # Arbitrary heuristic to simulate slideshow posts.
        return int(shortcode[:2], 16) % 2 == 0 if shortcode else False

    @staticmethod
    def _build_slideshow_medias(shortcode: str) -> List[Dict[str, Any]]:
        medias: List[Dict[str, Any]] = []
        for idx in range(3):
            medias.append(
                {
                    "url": f"https://dummy.instagramcdn.com/p/{shortcode}/image_{idx+1}.jpg",
                    "quality": "standard",
                    "extension": "jpg",
                    "type": "image",
                }
            )
        return medias

    @staticmethod
    def _build_single_media(shortcode: str) -> List[Dict[str, Any]]:
        return [
            {
                "url": f"https://dummy.instagramcdn.com/p/{shortcode}/image.jpg",
                "quality": "standard",
                "extension": "jpg",
                "type": "image",
            }
        ]