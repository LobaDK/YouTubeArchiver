import os
import sys
import time
from lib import settings, menu, utility
from lib.utility import logger, installation_helper
from InquirerPy import prompt


relative_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(relative_path)

logger.debug(f"Changed working directory to {relative_path}")

settings = settings.Settings()

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


main_menu_options = [
    {
        "type": "list",
        "name": "main_menu",
        "message": "Please select an option:",
        "choices": [
            {"name": "Download", "value": "D"},
            {"name": "Archive", "value": "A"},
            {"name": "Update yt-dlp", "value": "UD"},
            {"name": "Update YouTube Archiver", "value": "UA"},
            {"name": "Exit", "value": "E"},
        ],
    }
]

# Functions for the main menu options
functions = {
    "D": lambda: menu.menu(
        menu.MenuParam(Settings=settings, download_type=menu.DownloadType.DOWNLOAD)
    ),
    "A": lambda: menu.menu(
        menu.MenuParam(Settings=settings, download_type=menu.DownloadType.ARCHIVE)
    ),
    "UD": installation_helper.update_ytdlp,
    "UA": installation_helper.update_youtube_archiver,
    "E": sys.exit,
}


# Main menu for the user
while True:
    utility.clear()
    main_menu_answer = prompt(main_menu_options)
    functions[main_menu_answer["main_menu"]]()
