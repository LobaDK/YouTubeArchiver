import yt_dlp
from lib.utility import logger


def url_is_valid(url: str):
    logger.debug(f"User entered URL: {url}")
    print("\nTesting URL. Press Ctrl+C to skip.")
    try:
        with yt_dlp.YoutubeDL(
            {
                "playlistitems": "1",
                "lazyplaylist": True,
                "noplaylist": True,
            }
        ) as ytdlp:
            ytdlp.extract_info(url, download=False)
            logger.info(f"Test complete: {url}")
            return True
    except KeyboardInterrupt:
        logger.debug("User skipped URL testing.")
        return True
    except yt_dlp.utils.DownloadError as e:
        logger.info(e)
        return False
