import os
import zipfile
import requests
import sys
import tqdm
import time
import subprocess
import shutil
from pathlib import Path

from .logging_helper import create_logger, FileAndStreamHandler
from .misc import ffmpeg_is_installed


class InstallationHelper:
    """
    Helper class for installation-related tasks.

    This class provides methods for extracting compressed files and downloading the ffmpeg executable.

    Args:
        log (logging_helper.FileAndStreamHandler): The log file and stream handler.

    Attributes:
        logger: The logger instance for logging messages.

    Note: This class relies on the `zipfile`, `os`, `shutil`, `requests`, `sys`, and `tqdm` modules.
    """

    def __init__(self, log: FileAndStreamHandler) -> None:
        self.logger = create_logger(log)

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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
        self.logger.info(
            "yt-dlp has been updated to the latest version. The script will now exit to apply the changes."
        )
        time.sleep(2)
        sys.exit(0)
