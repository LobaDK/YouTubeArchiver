import os
import sys
import logging
import time
from lib import logging_helper, misc, installation_helper, settings, menu


relative_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(relative_path)

LOG_NAME = "YouTubeArchiver"
LOG_FILE = "YouTubeArchiver.log"

logger = logging_helper.create_logger(
    logging_helper.FileAndStreamHandler(
        logger_name=LOG_NAME,
        log_file=LOG_FILE,
        file_log_level=logging.DEBUG,
        stream_log_level=logging.INFO,
    )
)

installation_helper = installation_helper.InstallationHelper(
    logging_helper.FileAndStreamHandler(logger_name=LOG_NAME, log_file=LOG_FILE)
)

logger.debug(f"Changed working directory to {relative_path}")

settings = settings.Settings()
settings.logger = logger

try:
    import yt_dlp  # noqa We need to check if yt-dlp is installed
except ImportError:
    logger.error(
        "yt-dlp is not installed. Please install it using `pip install yt-dlp`"
    )
    time.sleep(3)
    sys.exit(1)

if settings.ffmpeg_is_installed is False:
    logger.warning(
        "ffmpeg is not installed. It is not required, but it is highly recommended to have it installed."
    )
    option = input("Do you want to download ffmpeg now? (Y/n): ").lower() or "y"
    if option == "y":
        logger.debug("User chose to download ffmpeg.")
        if not sys.platform == "linux":
            try:
                installation_helper.download_ffmpeg()
                settings.ffmpeg_is_installed = True
            except Exception:
                logger.error(
                    "An error occurred while downloading ffmpeg.", exc_info=True
                )
                option = (
                    input("Do you want to continue without ffmpeg? (Y/n): ").lower()
                    or "n"
                )
                if option == "n":
                    sys.exit(1)
        else:
            logger.warning(
                "Automatic installation of ffmpeg is not supported on Linux. Please install it manually using your package manager."
            )
    else:
        logger.debug("User chose not to download ffmpeg.")


main_menu_text = f"""
Welcome to YouTube Archiver!
FFmpeg detected: {settings.ffmpeg_is_installed}
\nPlease select an option
\n[D]ownload
\n[A]rchive
\n[U]pdate
\n[E]xit
"""

options = {
    "D": lambda: menu.menu(
        menu.MenuParam(settings=settings, download_type=menu.DownloadType.DOWNLOAD)
    ),
    "A": lambda: menu.menu(
        menu.MenuParam(settings=settings, download_type=menu.DownloadType.ARCHIVE)
    ),
    "U": installation_helper.update_ytdlp,
    "E": sys.exit,
}


# Main menu for the user
while True:
    misc.clear()
    print(main_menu_text)
    option = input("Enter your choice: ").upper()
    if option in options:
        options[option]()
    else:
        misc.not_valid_input(option)
