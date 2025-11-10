thonimport hashlib
import logging
from typing import Any, Dict
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class TikTokExtractor:
    """
    Lightweight TikTok extractor that builds structured metadata without
    depending on TikTok APIs. It generates deterministic example data
    based on the URL.
    """

    source_name = "tiktok"

    def extract(self, url: str) -> Dict[str, Any]:
        logger.debug("Extracting TikTok URL: %s", url)
        video_id = self._extract_video_id(url)
        author = self._extract_author(url)
        title = f"TikTok video by {author}"
        duration_ms = self._duration_from_id(video_id)

        base_thumbnail = (
            f"https://dummy.tiktokcdn.com/thumbnail/{video_id or 'unknown'}.jpg"
        )

        medias = [
            {
                "url": f"https://dummy.tiktokcdn.com/{video_id}_hd_no_watermark.mp4",
                "quality": "hd_no_watermark",
                "extension": "mp4",
                "type": "video",
            },
            {
                "url": f"https://dummy.tiktokcdn.com/{video_id}_no_watermark.mp4",
                "quality": "no_watermark",
                "extension": "mp4",
                "type": "video",
            },
            {
                "url": f"https://dummy.tiktokcdn.com/{video_id}_audio.mp3",
                "duration": int(duration_ms / 1000),
                "quality": "audio",
                "extension": "mp3",
                "type": "audio",
            },
        ]

        record = {
            "url": url,
            "source": self.source_name,
            "author": author,
            "title": title,
            "thumbnail": base_thumbnail,
            "duration": duration_ms,
            "medias": medias,
            "type": "multiple",
            "error": False,
        }
        logger.debug("TikTok extraction result: %s", record)
        return record

    @staticmethod
    def _extract_video_id(url: str) -> str:
        """
        Extracts video ID from common TikTok URL patterns.
        """
        parsed = urlparse(url)
        # Pattern: /@username/video/<id>
        parts = [p for p in parsed.path.split("/") if p]
        if "video" in parts:
            idx = parts.index("video")
            if idx + 1 < len(parts):
                return parts[idx + 1]

        # Fallback: hash of URL
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _extract_author(url: str) -> str:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        for part in parts:
            if part.startswith("@"):
                return part.lstrip("@")
        # Fallback: check query param "author"
        qs = parse_qs(parsed.query)
        if "author" in qs and qs["author"]:
            return qs["author"][0]
        return "unknown"

    @staticmethod
    def _duration_from_id(video_id: str) -> int:
        """
        Produces a pseudo-random but stable duration based on the video id.
        """
        if not video_id:
            return 60000
        digest = hashlib.md5(video_id.encode("utf-8")).hexdigest()
        # map to 10–240 seconds
        value = int(digest[:4], 16)
        seconds = 10 + (value % 231)
        return seconds * 1000