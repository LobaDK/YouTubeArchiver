from enum import Enum
from pydantic import BaseModel, ConfigDict
import yt_dlp

from lib import settings, ui, utility


class Choice(Enum):
    """
    Enum representing the choice of the user.

    Attributes:
        YES (str): Represents the choice of yes.
        NO (str): Represents the choice of no.
    """

    YES = "y"
    NO = "n"


class DownloadType(Enum):
    """
    Enum representing the type of download.

    Attributes:
        DOWNLOAD (int): Represents a regular download.
        ARCHIVE (int): Represents an archive download.
    """

    DOWNLOAD = 1
    ARCHIVE = 2


class MenuParam(BaseModel):
    settings: settings.Settings
    download_type: DownloadType

    class Config(ConfigDict):
        arbitrary_types_allowed = True


class Menu:
    def __init__(self, menu_param: MenuParam):
        self.download_type = (
            "download"
            if menu_param.download_type == DownloadType.DOWNLOAD
            else "archive"
        )
        self.settings = menu_param.settings
        self.logger = settings.logger

    def menu(self):
        """
        Main menu for the application.

        Args:
            MenuParam (MenuParam): The parameters for the menu.
        """
        utility.clear()
        while True:
            url = utility.get_user_input(
                "Enter the URL of the video or playlist you want to download: ",
                default="",
                lower=False,
            )
            self.logger.debug(f"User entered URL: {url}")
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
                    self.logger.info(f"URL is valid: {url}")
                    break
            except KeyboardInterrupt:
                self.logger.debug("User skipped URL validation.")
                break
            except yt_dlp.utils.DownloadError as e:
                self.logger.info(e)
                continue

        print(
            f"\nPlease select the folder where you want to {self.download_type} the videos: "
        )
        while True:
            folder = ui.select_folder()
            if not folder:
                self.logger.info("No folder selected.")
                option = utility.get_user_input(
                    "Do you want to select a folder again? (Y/n): "
                )
                if option == Choice.NO.value:
                    self.logger.debug("User chose not to select a folder.")
                    return
                elif option == Choice.YES.value:
                    self.logger.debug("User chose to select a folder again.")
                    continue
            self.logger.debug(f"User selected folder: {folder}")
            break

        print(
            "\nyt-dlp supports using an archive file to keep track of downloaded videos. It defaults to 'archive.txt'."
        )
        while True:
            option = utility.get_user_input(
                "Would you like to use an archive file? (Y/n): "
            )
            if option == Choice.YES.value:
                self.logger.debug("User chose to use an archive file.")
                archive_file = ui.select_archive_file()
                if not archive_file:
                    self.logger.info("No archive file selected.")
                    option = utility.get_user_input(
                        "Do you want to select an archive file again? (Y/n): "
                    )
                    if option == Choice.NO.value:
                        self.logger.debug("User chose not to select an archive file.")
                        return
                    elif option == Choice.YES.value:
                        self.logger.debug("User chose to select an archive file again.")
                        continue
                self.logger.debug(f"User selected archive file: {archive_file}")
                break
            elif option == Choice.NO.value:
                self.logger.debug("User chose not to use an archive file.")
                archive_file = None
                break
            else:
                utility.not_valid_input(option)
                continue
