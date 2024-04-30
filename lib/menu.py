from enum import Enum
from pydantic import BaseModel, ConfigDict
from InquirerPy import prompt

from lib import settings, ui, utility, menu_components
from lib.utility import logger, Choice
from lib.ui import InquirerMenu


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
        url = prompt(InquirerMenu.youtube_url_input)["url"]
        if not menu_components.url_is_valid(url):
            answer = prompt(InquirerMenu.youtube_url_select)["url_select"]
            if answer == Choice.SELECT.value:
                continue  # Ask for the URL again
            elif answer == Choice.MENU.value:
                return  # Return to the main menu

        print(
            f"\nPlease select the folder where you want to {download_type} the videos: "
        )
        # Loop to get the desired folder location for storing the downloaded videos
        while True:
            folder = ui.select_folder()
            if not folder:
                logger.debug("No folder selected.")
                answer = prompt(InquirerMenu.download_folder_select)["download_folder"]
                if answer == Choice.SELECT.value:
                    logger.debug("User chose to select a folder.")
                    continue  # Ask for the folder again
                elif answer == Choice.BACK.value:
                    logger.debug("User chose to go back.")
                    break  # Go back to the URL input
                elif answer == Choice.MENU.value:
                    logger.debug("User chose to return to the main menu.")
                    return

            # Loop to get the desired archive file location
            print(
                "\nyt-dlp supports using an archive file to keep track of downloaded videos. It defaults to 'archive.txt'."
            )
            while True:
                answer = prompt(InquirerMenu.use_archive_file_question)[
                    "use_archive_file"
                ]
                if answer is True:
                    logger.debug("User chose to use an archive file.")
                    print("\nPlease select the archive file: ")
                    archive_file = ui.select_file(filetypes=[("Text files", "*.txt")])
                    if not archive_file:
                        logger.debug("No archive file selected.")
                        answer = prompt(InquirerMenu.archive_file_select)[
                            "archive_file"
                        ]
                        if answer == Choice.SELECT.value:
                            logger.debug("User chose to select an archive file.")
                            continue  # Ask for the archive file again
                        elif answer == Choice.BACK.value:
                            logger.debug("User chose to go back.")
                            break  # Go back to the folder selection
                        elif answer == Choice.MENU.value:
                            logger.debug("User chose to return to the main menu.")
                            return
