import yt_dlp
from lib.utility import logger


def url_is_valid(url: str):
    logger.debug(f"User entered URL: {url}")
    print("\nChecking if the URL is valid. Press Ctrl+C to skip.")
    try:
        with yt_dlp.YoutubeDL(
            {
                "playlist_items": "1",
                "--lazy-playlist": True,
                "no_playlist": True,
            }
        ) as ytdlp:
            ytdlp.extract_info(url, download=False)
            logger.info(f"URL is valid: {url}")
            return True
    except KeyboardInterrupt:
        logger.debug("User skipped URL validation.")
        return True
    except yt_dlp.utils.DownloadError as e:
        logger.info(e)
        return False
