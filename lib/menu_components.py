from yt_dlp import YoutubeDL, DownloadError
from lib.utility import logger


def url_is_valid(url: str):
    logger.debug(f"User entered URL: {url}")
    print("\nTesting URL. Press Ctrl+C to skip.")
    try:
        with YoutubeDL(
            {
                "logger": logger,
                "playlist_items": "1",
                "lazy_playlist": True,
                "noplaylist": True,
            }
        ) as ytdlp:
            ytdlp.extract_info(url, download=False)
            logger.info(f"Test complete: {url}")
            return True
    except KeyboardInterrupt:
        logger.debug("User skipped URL testing.")
        return True
    except DownloadError as e:
        logger.info(e)
        return False
