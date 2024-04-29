import os
import sys
import logging
import time
from lib import logging_helper, installation_helper, settings, menu, utility


relative_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(relative_path)

LOGGER_NAME = "YouTubeArchiver"
LOG_FILE = "log.log"

log_helper = logging_helper.LoggingHelper(
    logger_name=LOGGER_NAME,
    log_file=LOG_FILE,
    file_log_level=logging.DEBUG,
    stream_log_level=logging.INFO,
    include_timestamp=False,
)

logger = log_helper.create_logger()

installation_helper = installation_helper.InstallationHelper(logger)

logger.debug(f"Changed working directory to {relative_path}")

settings = settings.Settings()
settings.logger = logger

try:
    import yt_dlp  # noqa We need to check if yt-dlp is installed
except ImportError:
    logger.error(
        "yt-dlp is not installed. Please install it using `pip install yt-dlp` or `pip install -r requirements.txt`."
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
else:
    logger.debug("ffmpeg is installed and detected.")


main_menu_text = f"""
Welcome to YouTube Archiver!
FFmpeg detected: {settings.ffmpeg_is_installed}
\nPlease select an option
\n[D]ownload
\n[A]rchive
\n[U]pdate
\n[E]xit
"""

# Options for the main menu.
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
    utility.clear()
    print(main_menu_text)
    option = input("Enter your choice: ").upper()
    if option in options:
        options[option]()
    else:
        utility.not_valid_input(option)
