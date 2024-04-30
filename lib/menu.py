from enum import Enum
from pydantic import BaseModel, ConfigDict

from lib import settings, ui, utility, menu_components
from lib.utility import logger, Choice


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
    Settings: settings.Settings
    download_type: DownloadType

    class Config(ConfigDict):
        arbitrary_types_allowed = True


def menu(menu_param: MenuParam):
    """
    Main menu for the application.

    Args:
        MenuParam (MenuParam): The parameters for the menu.
    """
    download_type = (
        "download" if menu_param.download_type == DownloadType.DOWNLOAD else "archive"
    )
    settings = menu_param.Settings  # noqa TODO: Remove noqa when used
    utility.clear()

    # Loop to get the URL of the video or playlist to download
    while True:
        url = utility.get_user_input(
            "Enter the URL of the video or playlist you want to download. Write 'back' to return to the main menu: ",
            default="",
            lower=False,
        )
        if url.lower() == "back":
            logger.debug("User chose to return to the main menu.")
            return  # Return to the main menu
        if not menu_components.url_is_valid(url):
            continue  # Ask for the URL again

        print(
            f"\nPlease select the folder where you want to {download_type} the videos: "
        )
        # Loop to get the desired folder location for storing the downloaded videos
        while True:
            folder = ui.select_folder()
            if not folder:
                logger.info("No folder selected.")
                option = utility.get_user_input(
                    "Do you want to select a folder again? (Y/n): "
                )
                if option == Choice.NO.value:
                    logger.debug("User chose not to select a folder.")
                    return
                elif option == Choice.YES.value:
                    logger.debug("User chose to select a folder again.")
                    continue
            logger.debug(f"User selected folder: {folder}")
            break

        print(
            "\nyt-dlp supports using an archive file to keep track of downloaded videos. It defaults to 'archive.txt'."
        )
        while True:
            option = utility.get_user_input(
                "Would you like to use an archive file? (Y/n): "
            )
            if option == Choice.YES.value:
                logger.debug("User chose to use an archive file.")
                archive_file = ui.select_archive_file()
                if not archive_file:
                    logger.info("No archive file selected.")
                    option = utility.get_user_input(
                        "Do you want to select an archive file again? (Y/n): "
                    )
                    if option == Choice.NO.value:
                        logger.debug("User chose not to select an archive file.")
                        return
                    elif option == Choice.YES.value:
                        logger.debug("User chose to select an archive file again.")
                        continue
                logger.debug(f"User selected archive file: {archive_file}")
                break
            elif option == Choice.NO.value:
                logger.debug("User chose not to use an archive file.")
                archive_file = None
                break
            else:
                utility.not_valid_input(option)
                continue
