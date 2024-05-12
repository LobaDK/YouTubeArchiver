import os
import sys
import time
from lib.utility import logger, installation_helper
from InquirerPy import inquirer
from prompt_toolkit.completion import FuzzyWordCompleter

try:
    import yt_dlp  # noqa We need to check if yt-dlp is installed
except ImportError:
    logger.error(
        "yt-dlp is not installed. Please install it using `pip install yt-dlp` or `pip install -r requirements.txt`."
    )
    time.sleep(3)
    sys.exit(1)
from lib import settings, menu, utility
from lib.ui import InquirerMenu

test_completer = FuzzyWordCompleter(
    [
        "%(title)s",
        "%(ext)s" "%(id)s",
        "%(uploader)s",
        "%(uploader_id)s",
        "%(upload_date)s",
        "%(view_count)s",
        "%(like_count)s",
        "%(dislike_count)s",
        "%(average_rating)s",
        "%(duration)s",
        "%(is_live)s",
        "%(start_time)s",
        "%(end_time)s",
        "%(format)s",
        "%(format_id)s",
        "%(url)s",
        "%(ext)s",
        "%(format_note)s",
        "%(format_note)s",
        "%(acodec)s",
        "%(vcodec)s",
        "%(abr)s",
        "%(vbr)s",
        "%(asr)s",
        "%(fps)s",
        "%(tbr)s",
        "%(resolution)s",
        "%(filesize)s",
        "%(container)s",
        "%(protocol)s",
        "%(extractor)s",
        "%(extractor_key)s",
    ]
)

test = inquirer.text(
    message="Enter a template",
    completer=test_completer,
    validate=lambda result: len(result) > 0,
).execute()

logger.debug("########### Starting YouTube Archiver ###########")

relative_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(relative_path)

logger.debug(f"Changed working directory to {relative_path}")

settings = settings.Settings()


if settings.ffmpeg_is_installed is False:
    logger.warning("ffmpeg is not installed.")
    option = InquirerMenu.ffmpeg_download_question.execute()
    if option is True:
        logger.debug("User chose to download ffmpeg.")
        if not sys.platform == "linux":
            try:
                installation_helper.download_ffmpeg()
                settings.ffmpeg_is_installed = True
            except Exception:
                logger.error(
                    "An error occurred while downloading ffmpeg.", exc_info=True
                )
                option = InquirerMenu.continue_without_ffmpeg_question.execute()
                if option is False:
                    sys.exit(1)
        else:
            logger.warning(
                "Automatic installation of ffmpeg is not supported on Linux. Please install it manually using your package manager."
            )
    else:
        logger.debug("User chose not to download ffmpeg.")
else:
    logger.debug("ffmpeg is installed and detected.")


# Functions for the main menu options
functions = {
    "D": lambda: menu.Menu(
        menu.MenuParam(Settings=settings, download_type=menu.DownloadType.DOWNLOAD)
    ).main_menu(),
    "A": lambda: menu.Menu(
        menu.MenuParam(Settings=settings, download_type=menu.DownloadType.ARCHIVE)
    ).main_menu(),
    "UD": installation_helper.update_ytdlp,
    "UA": installation_helper.update_youtube_archiver,
    "E": sys.exit,
}


# Main menu for the user
while True:
    utility.clear()
    main_menu_answer = InquirerMenu.main_menu_options().execute()
    functions[main_menu_answer]()
