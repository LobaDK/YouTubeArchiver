from enum import Enum
from pydantic import BaseModel, ConfigDict
from textwrap import dedent
from datetime import datetime

from lib import settings, ui, utility, menu_components
from lib.utility import logger, ChoiceEnum
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
    logger.debug(
        dedent(
            f"""
            download_type: {download_type}
            is_ffmpeg_installed: {settings.ffmpeg_is_installed}
            """
        )
    )

    command_params = {}
    if settings.ffmpeg_is_installed:
        command_params["--ffmpeg_location"] = settings.ffmpeg_location

    go_back = False

    # Loop to get the URL of the video or playlist to download
    while True:
        url = InquirerMenu.youtube_url_input.execute()
        if not menu_components.url_is_valid(url):
            answer = InquirerMenu.youtube_url_select.execute()
            if answer == ChoiceEnum.SELECT.value:
                continue  # Ask for the URL again
            elif answer == ChoiceEnum.MENU.value:
                return  # Return to the main menu

        settings.url = url

        print(
            f"\nPlease select the folder where you want to {download_type} the videos: "
        )
        # Loop to get the desired folder location for storing the downloaded videos
        while True:
            folder = ui.select_folder()
            if not folder:
                logger.debug("No folder selected.")
                answer = InquirerMenu.download_folder_select.execute()
                if answer == ChoiceEnum.SELECT.value:
                    logger.debug("User chose to select a folder.")
                    continue  # Ask for the folder again
                elif answer == ChoiceEnum.BACK.value:
                    logger.debug("User chose to go back.")
                    break  # Go back to the URL input
                elif answer == ChoiceEnum.MENU.value:
                    logger.debug("User chose to return to the main menu.")
                    return

            command_params["--output"] = folder

            # Loop to get the desired archive file location
            print(
                f"\nyt-dlp supports using an archive file to keep track of {download_type + ('ed' if menu_param.download_type == DownloadType.DOWNLOAD else 'd')} videos. It defaults to 'archive.txt'."
            )
            while True:
                answer = InquirerMenu.use_archive_file_question.execute()
                if answer is True:
                    logger.debug("User chose to use an archive file.")
                    print("\nPlease select the archive file: ")
                    archive_file = ui.select_file(filetypes=[("Text files", "*.txt")])
                    if not archive_file:
                        logger.debug("No archive file selected.")
                        answer = InquirerMenu.archive_file_select.execute()
                        if answer == ChoiceEnum.SELECT.value:
                            logger.debug("User chose to select an archive file.")
                            continue  # Ask for the archive file again
                        elif answer == ChoiceEnum.BACK.value:
                            logger.debug("User chose to go back.")
                            break  # Go back to the folder selection
                        elif answer == ChoiceEnum.MENU.value:
                            logger.debug("User chose to return to the main menu.")
                            return  # Return to the main menu
                    command_params["--download-archive"] = archive_file
                elif answer is False:
                    command_params["--no-download-archive"] = ""

                go_back = False
                # Check if the URL is a playlist or video in a playlist
                while True:
                    if go_back is True:
                        break
                    if utility.url_is_only_playlist(
                        url
                    ) or utility.url_is_video_in_playlist(url):
                        if utility.url_is_only_playlist(url):
                            answer = InquirerMenu.url_is_playlist_select.execute()
                        else:
                            answer = (
                                InquirerMenu.url_is_video_in_playlist_select.execute()
                            )
                        if answer == "all":
                            pass
                        elif answer == "index":
                            while True:
                                start_index = (
                                    InquirerMenu.get_playlist_start_index.execute()
                                )
                                end_index = (
                                    InquirerMenu.get_playlist_end_index.execute()
                                )
                                if start_index > end_index:
                                    print(
                                        "The end index must be greater than or equal to the start index."
                                    )
                                    continue
                                command_params["--playlist-start"] = start_index
                                command_params["--playlist-end"] = end_index
                                break
                        elif answer == "date":
                            while True:
                                after_date = InquirerMenu.get_after_date.execute()
                                before_date = InquirerMenu.get_before_date.execute()

                                after_date_obj = datetime.strptime(after_date, "%Y%m%d")
                                before_date_obj = datetime.strptime(
                                    before_date, "%Y%m%d"
                                )

                                if after_date_obj > before_date_obj:
                                    print(
                                        "The before date must be greater than or equal to the after date."
                                    )
                                    continue
                                command_params["--dateafter"] = after_date
                                command_params["--datebefore"] = before_date
                                break
                        elif answer == "video":
                            command_params["--no-playlist"] = ""
                        elif answer == ChoiceEnum.BACK.value:
                            break
                        elif answer == ChoiceEnum.MENU.value:
                            return

                        question = InquirerMenu.reverse_order_question.execute()
                        if question is True:
                            command_params["--playlist-reverse"] = ""
                        elif question is False:
                            command_params["--no-playlist-reverse"] = ""
