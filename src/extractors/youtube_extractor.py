thonimport hashlib
import logging
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class YouTubeExtractor:
    """
    Example YouTube extractor that parses common video URLs and yields
    structured metadata for downstream processing and export.
    """

    source_name = "youtube"

    def extract(self, url: str) -> Dict[str, Any]:
        logger.debug("Extracting YouTube URL: %s", url)
        video_id = self._extract_video_id(url)
        title = f"YouTube video {video_id}"
        author = self._guess_author(video_id)
        duration_ms = self._duration_from_id(video_id)

        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        medias = [
            {
                "url": f"https://youtube.com/watch?v={video_id}&fmt=mp4_1080p",
                "quality": "1080p",
                "extension": "mp4",
                "type": "video",
            },
            {
                "url": f"https://youtube.com/watch?v={video_id}&fmt=mp4_720p",
                "quality": "720p",
                "extension": "mp4",
                "type": "video",
            },
            {
                "url": f"https://youtube.com/watch?v={video_id}&fmt=audio_mp3",
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
            "thumbnail": thumbnail,
            "duration": duration_ms,
            "medias": medias,
            "type": "multiple",
            "error": False,
        }
        logger.debug("YouTube extraction result: %s", record)
        return record

    @staticmethod
    def _extract_video_id(url: str) -> str:
        parsed = urlparse(url)
        if parsed.netloc in {"youtu.be"}:
            # Short URL: https://youtu.be/<id>
            parts = [p for p in parsed.path.split("/") if p]
            if parts:
                return parts[0]
        # Standard: https://www.youtube.com/watch?v=<id>
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]

        # Fallback: hash URL
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:11]

    @staticmethod
    def _guess_author(video_id: str) -> str:
        # We can't know the author without API calls, so derive a stable pseudo value.
        digest = hashlib.md5(video_id.encode("utf-8")).hexdigest()
        return f"channel_{digest[:8]}"

    @staticmethod
    def _duration_from_id(video_id: str) -> int:
        if not video_id:
            return 300000
        digest = hashlib.sha1(video_id.encode("utf-8")).hexdigest()
        # map to 2–30 minutes
        value = int(digest[:4], 16)
        minutes = 2 + (value % 29)
        return minutes * 60 * 1000