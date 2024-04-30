import sys
import os
import time
import shutil
import logging
import zipfile
import requests
import subprocess
import tqdm
import certifi
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from enum import Enum
import pkg_resources
from yolk.pypi import CheeseShop


# Fixes "SSL: CERTIFICATE_VERIFY_FAILED" error on Windows from CheeseShop.
# TODO: Further test this. Only Windows? Only on certain networks/systems?
os.environ["SSL_CERT_FILE"] = certifi.where()


class Choice(Enum):
    """
    Enum representing the choice of the user.

    Attributes:
        YES (str): Represents the choice of yes.
        NO (str): Represents the choice of no.
    """

    YES = "y"
    NO = "n"
    SELECT = "s"
    BACK = "b"
    MENU = "m"


LOGGER_NAME = "YouTubeArchiver"
LOG_FILE = "log.log"


def create_folder(folder: Path):
    """
    Create a folder at the specified path.

    Args:
        folder (Path): The path of the folder to create.
        logger (logging.Logger): The logger object for logging messages.

    Returns:
        bool: True if the folder was created successfully, False otherwise.
    """
    try:
        folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created folder: {str(folder)}")
        return True
    except (OSError, PermissionError, NotADirectoryError):
        logger.error(
            "An error occurred while creating the folder. Please refer to the logs if this continues.",
            exc_info=True,
        )
        return False


def get_user_input(prompt: str, default: str = Choice.YES.value, lower: bool = True):
    """
    Prompts the user for input with the given prompt and returns the user's input.
    If the user enters an empty string, the default value is returned instead.

    Args:
        prompt (str): The prompt to display to the user.
        default (str, optional): The default value to return if the user enters an empty string.
            Defaults to Choice.YES.value.
        lower (bool, optional): Whether to convert the user's input to lowercase. Defaults to True.

    Returns:
        str: The user's input or the default value if the user enters an empty string.
    """
    return (input(prompt) or default).lower() if lower else input(prompt) or default


def clear():
    """
    Clears the console screen.

    This function checks the platform and uses the appropriate command to clear the console screen.
    On Windows, it uses the "cls" command, and on other platforms, it uses the "clear" command.

    Note: This function relies on the `os` and `sys` modules.

    Example usage:
    clear()
    """
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def not_valid_input(option: str):
    """
    Prints a message for an invalid input.

    This function prints a message to the console for an invalid input option.

    Args:
        option (str): The invalid input option.

    Example usage:
    not_valid_input("X")
    """
    print(f"Invalid option: {option if option else None}. Please enter a valid option.")
    time.sleep(3)


def ffmpeg_is_installed():
    """
    Check if ffmpeg is installed on the system.

    Returns:
        bool: True if ffmpeg is installed, False otherwise.
    """
    return any(
        [
            shutil.which("ffmpeg") is not None,
            os.path.isfile("bin/ffmpeg"),
            os.path.isfile("bin/ffmpeg.exe"),
        ]
    )


class InstallationHelper:
    """
    Helper class for installation-related tasks.

    This class provides methods for extracting compressed files, downloading ffmpeg,
    and updating yt-dlp to the latest version.

    Example usage:\n
    helper = InstallationHelper()\n
    helper.extract_file("ffmpeg.zip", "bin")\n
    helper.download_ffmpeg()\n
    helper.update_ytdlp()
    """

    def __init__(self) -> None:
        self.logger = logger

    def get_installed_version(self, package_name: str) -> str | None:
        """
        Get the installed version of a package.

        Args:
            package_name (str): The name of the package.

        Returns:
            str | None: The installed version of the package, or None if the package is not installed.
        """
        try:
            return pkg_resources.get_distribution(package_name).version
        except pkg_resources.DistributionNotFound:
            return None

    def get_latest_version(self, package_name: str) -> str | None:
        """
        Get the latest version of a package from PyPI.

        Args:
            package_name (str): The name of the package.

        Returns:
            str | None: The latest version of the package, or None if the package is not found on PyPI.
        """
        # TODO: Properly test this function. Dumb corporate proxy is messing with the SSL certificate.
        pypi = CheeseShop()
        versions = pypi.query_versions_pypi(package_name)
        if not versions:
            return None
        return versions[1][0]

    def extract_file(self, from_file: str, to_dir: str):
        """
        Extracts the contents of a compressed file to a directory.

        This function extracts the contents of a compressed file to a directory.
        It supports zip files, and if the extracted file already exists, it will be overwritten.

        Args:
            from_file (str): The path to the compressed file.
            to_dir (str): The path to the directory where the contents will be extracted.

        Note: This function relies on the `zipfile` module.

        Example usage:
        extract_file("ffmpeg.zip", "bin")
        """
        # Extract the zip file to the specified directory and show progress using tqdm
        with zipfile.ZipFile(from_file, "r") as archive:
            for file in tqdm.tqdm(archive.namelist(), desc="Extracting", unit="files"):
                if "/bin/ffmpeg" in file:
                    with archive.open(file) as source, open(
                        os.path.join(to_dir, Path(file).name), "wb"
                    ) as target:
                        shutil.copyfileobj(source, target)
                    break
        os.unlink(from_file)

    def download_ffmpeg(self):
        from lib.utility import ffmpeg_is_installed

        """
        Download the ffmpeg executable for the current platform.

        This function downloads the ffmpeg executable for the current platform
        (Windows, or macOS) and saves it to the `bin` directory.

        Note: This function relies on the `os`, `requests`, `sys`, and `tqdm` modules.

        Example usage:
        download_ffmpeg()
        """

        # Define the download URLs for ffmpeg binaries
        ffmpeg_urls = {
            "Windows": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            "macOS": "https://evermeet.cx/ffmpeg/get/zip",
            "Linux": None,  # Use the system package manager to install ffmpeg on Linux
        }

        if sys.platform == "win32":
            self.logger.debug("Detected Windows platform")
            download_url = ffmpeg_urls["Windows"]
            download_file = "bin/ffmpeg.zip"
        elif sys.platform == "darwin":
            self.logger.debug("Detected macOS platform")
            download_url = ffmpeg_urls["macOS"]
            download_file = "bin/ffmpeg.zip"

        # Create the `bin` directory if it does not exist
        os.makedirs("bin", exist_ok=True)

        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        self.logger.info(f"Downloading ffmpeg from: {download_url}")
        # Download the compressed ffmpeg binary and show progress using tqdm
        with tqdm.tqdm.wrapattr(
            response.raw, "read", total=total_size, desc="Downloading"
        ) as r:
            with open(download_file, "wb") as f:
                shutil.copyfileobj(r, f)

        # Extract the downloaded ffmpeg binary
        self.extract_file(f"{download_file}", "bin")

        if ffmpeg_is_installed():
            self.logger.info(
                "Download and extraction of ffmpeg completed successfully. ffmpeg is now available in the `bin` directory."
            )
        else:
            self.logger.error(
                "An error occurred while downloading and extracting ffmpeg. Please install ffmpeg manually."
            )
            time.sleep(3)
            exit(1)

    def update_ytdlp(self):
        """
        Update yt-dlp to the latest version.

        This function updates yt-dlp to the latest version by running the command `pip install -U yt-dlp`.

        Note: This function relies on the `os` and `time` modules.

        Example usage:
        update_ytdl()
        """
        installed_version = self.get_installed_version("yt-dlp")
        latest_version = self.get_latest_version("yt-dlp")
        if not latest_version:
            self.logger.error(
                "Failed to get the latest version of yt-dlp. Please check your internet connection and try again."
            )
            time.sleep(3)
            return
        if installed_version == latest_version:
            self.logger.info("yt-dlp is already up to date.")
            time.sleep(2)
            return
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
        self.logger.info(
            "yt-dlp has been updated to the latest version. The script will now exit to apply the changes."
        )
        time.sleep(2)
        sys.exit(0)

    def update_youtube_archiver(self):
        """
        Update YouTubeArchiver to the latest version.

        This function updates YouTubeArchiver to the latest version by running the command `git pull`.

        Note: This function relies on the `subprocess` and `time` modules.

        Example usage:
        update_youtube_archiver()
        """
        std_out, std_err = subprocess.Popen(
            ["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).communicate()
        if std_err:
            self.logger.error(
                "An error occurred while updating YouTubeArchiver. Please refer to the logs for more information.",
                exc_info=True,
            )
            time.sleep(3)
            sys.exit(1)
        if (b"Already up to date" or b"Already up-to-date") in std_out:
            self.logger.info("YouTubeArchiver is already up to date.")
            time.sleep(2)
            return
        self.logger.info(
            "YouTubeArchiver has been updated to the latest version. The script will now exit to apply the changes."
        )
        time.sleep(2)
        sys.exit(0)


class LoggingHelper:
    """
    A helper class for creating and configuring loggers.

    This class provides methods to create and configure loggers with file and stream handlers.
    It also supports creating log directories and checking if a logger with a specified name exists.
    """

    def __init__(
        self,
        logger_name: str,
        log_file: str,
        include_timestamp: bool = True,
        log_level_left_padding: int = 0,
        file_log_level: int = logging.INFO,
        stream_log_level: int = logging.ERROR,
        interval: str = "midnight",
        backup_count: int = 7,
    ):
        self.logger_name = logger_name
        self.log_file = log_file
        self.include_timestamp = include_timestamp
        self.log_level_left_padding = log_level_left_padding
        self.file_log_level = file_log_level
        self.stream_log_level = stream_log_level
        self.interval = interval
        self.backup_count = backup_count

    def logger_exists(self) -> bool:
        """
        Check if the logger with the specified name exists.

        Returns:
            bool: True if the logger exists, False otherwise.
        """
        return self.logger_name in logging.Logger.manager.loggerDict

    def create_logger(self) -> logging.Logger:
        """
        Creates a logger with the given name and log file.

        Helper function to create, configure, and return a logger with the given name and log file.
        The logger will have a file handler and a stream handler attached to it.
        If the logger already exists, it will be returned without any changes.
        if the interval is specified, a TimedRotatingFileHandler will be created instead of a FileHandler.

        Returns:
            logging.Logger: The created logger.
        """
        if not Path(self.log_file).parent.exists():
            self.create_log_dir(str(Path(self.log_file).parent))

        if self.logger_exists():
            return logging.getLogger(self.logger_name)

        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)

        stream_handler = self._create_stream_handler()
        logger.addHandler(stream_handler)

        if self.interval:
            file_handler = self._create_timed_rotating_file_handler()
        else:
            file_handler = self._create_file_handler()
        logger.addHandler(file_handler)

        return logger

    def _create_file_handler(self) -> logging.FileHandler:
        """
        Creates a logging FileHandler with the specified log file and level.

        Returns:
            logging.FileHandler: The file handler object.

        """
        handler = logging.FileHandler(
            filename=self.log_file,
            encoding="utf-8",
            mode="a",
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            self._format_builder(),
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(self.file_log_level)
        return handler

    def _create_stream_handler(self) -> logging.StreamHandler:
        """
        Creates a logging StreamHandler with the specified log level.

        Returns:
            logging.StreamHandler: The created StreamHandler object.

        """
        handler = logging.StreamHandler()
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            self._format_builder(),
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(self.stream_log_level)
        return handler

    def _create_timed_rotating_file_handler(self) -> TimedRotatingFileHandler:
        """
        Creates a logging TimedRotatingFileHandler with the specified log file, level, interval, and backup count.

        Returns:
            logging.handlers.TimedRotatingFileHandler: The created TimedRotatingFileHandler object.
        """
        handler = TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.interval,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}",
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(self.file_log_level)
        return handler

    def _format_builder(self) -> str:
        """
        Builds the format string for the logger.

        Returns:
            str: The format string for the logger.
        """
        format_string = ""
        if self.include_timestamp:
            format_string += "[{asctime}] "
        format_string += (
            "[{levelname:<" + str(self.log_level_left_padding) + "}] {name}: {message}"
        )
        return format_string

    def create_log_dir(self):
        """
        Creates a log directory if it does not exist.

        Args:
            log_dir (str): The path to the log directory.

        """
        os.makedirs(str(Path(self.log_file).parent), exist_ok=True)


# Create a logger in the utility module so we can import and use it in other modules.
log_helper = LoggingHelper(
    logger_name=LOGGER_NAME,
    log_file=LOG_FILE,
    file_log_level=logging.DEBUG,
    stream_log_level=logging.INFO,
    include_timestamp=False,
)

logger = log_helper.create_logger()


# Create an installation helper object in the utility module so we can import and use it in other modules.
installation_helper = InstallationHelper()
