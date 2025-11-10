thonimport logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def detect_platform(url: str) -> Optional[str]:
    """
    Detects the media platform based on the hostname or simple URL patterns.
    Returns a lowercase platform name like 'tiktok', 'youtube', 'instagram',
    or None if the platform is unknown.
    """
    try:
        parsed = urlparse(url)
    except Exception as exc:
        logger.warning("Failed to parse URL %s: %s", url, exc)
        return None

    host = parsed.netloc.lower()

    if "tiktok.com" in host:
        return "tiktok"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "instagram.com" in host or "instagr.am" in host:
        return "instagram"
    if "facebook.com" in host or "fb.watch" in host:
        return "facebook"
    if "reddit.com" in host:
        return "reddit"
    if "spotify.com" in host:
        return "spotify"

    # Unknown but still usable as "generic"
    return None