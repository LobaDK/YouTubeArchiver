from enum import Enum
from pydantic import BaseModel, ConfigDict
from textwrap import dedent
from yt_dlp import YoutubeDL
from yt_dlp.utils import DateRange
from datetime import datetime, timedelta
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from typing import Generator

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


class Menu:
    def __init__(self, menu_param: MenuParam):
        self._menu_param = menu_param
        self._logger = logger
        self._download_type = (
            "download"
            if menu_param.download_type == DownloadType.DOWNLOAD
            else "archive"
        )
        self._settings = menu_param.Settings

    def set_appropriate_settings(self):
        """
        Sets the appropriate settings based on the download type and other settings.
        """
        if self._settings.url:
            self._settings.url_is_playlist = utility.url_is_only_playlist(
                self._settings.url
            )
            self._settings.url_is_video_in_playlist = utility.url_is_video_in_playlist(
                self._settings.url
            )
            self._settings.url_is_channel = utility.url_is_channel(self._settings.url)

        if self._menu_param.download_type == DownloadType.ARCHIVE:
            self._settings.archive_options = {
                "writedescription": True,
                "writeannotations": True,
                "writeinfojson": True,
                "writethumbnail": True,
                "writeurllink": True,
                "writewebloclink": True,
                "writedesktoplink": True,
                "writesubtitles": True,
                "allsubtitles": True,
                "overwrites": False,
            }
            if self._settings.url_is_channel:
                self._settings.output_template = "%(uploader)s/%(upload_date)s - %(title)s/%(title)s [%(id)s].%(ext)s"
            elif self._settings.url_is_playlist:
                if self._settings.ignore_playlist:
                    self._settings.output_template = "%(title)s.%(ext)s"
                else:
                    self._settings.output_template = "%(playlist_title)s/%(uploader)s/%(upload_date)s - %(title)s/%(upload_date)s [%(id)s].%(ext)s"

        else:
            self._settings.output_template = "%(title)s.%(ext)s"

    def check_required_settings(self) -> bool:
        """
        Checks if the required settings are set.

        Returns:
            bool: True if the required settings are set, False otherwise.
        """
        if not self._settings.url:
            return False
        if not self._settings.download_folder:
            return False
        if self._settings.use_archive_file and not self._settings.archive_file:
            return False
        if self._settings.url_is_playlist and not self._settings.playlist_options:
            return False
        if self._settings.url_is_channel and not self._settings.channel_options:
            return False
        if not self._settings.stream_types:
            return False
        if not self._settings.stream_select_mode:
            return False
        if not self._settings.stream_formats:
            return False
        if not self._settings.output_template:
            return False
        if self._menu_param.download_type == DownloadType.ARCHIVE:
            if not self._settings.archive_options:
                return False
        return True

    def main_menu_constructor(self) -> Generator[Choice, None, None]:
        """
        Constructs the main menu for the YouTubeArchiver application.

        Yields:
            List[Choice]: A list of Choice objects representing the main menu options.
        """
        yield [
            Choice(
                value="select_url",
                name=f"Select URL: {'*' if not self._settings.url else self._settings.url}",
            )
        ]
        if self._settings.url:
            yield [
                Separator(),
                Choice(
                    value="select_folder",
                    name=f"Select Folder: {'*' if not self._settings.download_folder else self._settings.download_folder}",
                ),
                Separator(),
                Choice(
                    value="use_archive_file",
                    name=f"Use Archive File: {menu_components.format_boolean(self._settings.use_archive_file)}",
                ),
            ]
            if self._settings.use_archive_file:
                yield [
                    Choice(
                        value="archive_file",
                        name=f"Archive File: {'*' if not self._settings.archive_file else self._settings.archive_file}",
                    ),
                ]
            yield [Separator()]
            if (
                self._settings.url_is_playlist
                or self._settings.url_is_video_in_playlist
            ):
                yield [
                    Choice(
                        value="playlist_options",
                        name=f"Playlist Options: {self._settings.playlist_options}",
                    ),
                ]
            if self._settings.url_is_channel:
                yield [
                    Choice(
                        value="channel_options",
                        name=f"Channel Options: {self._settings.channel_options}",
                    ),
                ]
            if (
                not (  # If the URL is not *only* a playlist, a video in a playlist, or a channel
                    self._settings.url_is_playlist
                    and not self._settings.url_is_video_in_playlist
                    and not self._settings.url_is_channel
                )
                or self._settings.expected_download_count
                == 1  # If we're expecting to download only one video
            ):
                yield [
                    Choice(
                        value="download_sections",
                        name=f"Download Sections of the video: {self._settings.download_sections if self._settings.download_sections else 'None selected'}",
                    ),
                    Separator(),
                ]
            yield [
                Choice(
                    value="stream_types",
                    name=f"Stream Types: {menu_components.format_stream_types(self._settings.stream_types) if self._settings.stream_types else '*'}",
                ),
                Choice(
                    value="stream_select_mode",
                    name=f"Stream Select Mode: {self._settings.stream_select_mode.capitalize()}",
                ),
                Choice(
                    value="combine_streams",
                    name=f"Combine Streams: {menu_components.format_boolean(self._settings.combine_streams)}",
                ),
                Choice(
                    value="stream_select_formats",
                    name=f"Stream Formats: {menu_components.format_stream_formats(self._settings.stream_formats, self._settings.combine_streams) if self._settings.stream_formats else '*'}",
                ),
                Separator(),
                Choice(
                    value="output_template",
                    name=f"Output Template: {self._settings.output_template}",
                ),
            ]
            if self._menu_param.download_type == DownloadType.ARCHIVE:
                yield [
                    Choice(
                        value="archive_options",
                        name=f"Archive Options: {self._settings.archive_options}",
                    ),
                ]
            if self.check_required_settings():
                yield [
                    Choice(
                        value="download",
                        name=f"Start {self._download_type.capitalize()}",
                    ),
                ]

    def get_default_choice(self, choices: list[Choice]) -> str:
        """
        Returns the default choice from the given list of choices.

        The default choice is determined by finding the first choice that contains
        an asterisk (*) in its name. If no such choice is found, the first choice in
        the list is considered the default choice.

        Args:
            choices (list[Choice]): A list of Choice objects representing the available choices.

        Returns:
            str: The value of the default choice.

        """
        for choice in choices:
            if isinstance(choice, Separator):
                continue
            if "*" in choice.name:
                return choice.value
        return choices[0].value

    def main_menu(self):
        logger.debug(
            f"download_type: {self._download_type}, is_ffmpeg_installed: {self._settings.ffmpeg_is_installed}"
        )
        main_menu_actions = {
            "select_url": lambda: setattr(
                self._settings, "url", menu_components.select_url(self._settings.url)
            ),
            "select_folder": lambda: setattr(
                self._settings, "download_folder", menu_components.select_folder()
            ),
            "use_archive_file": lambda: setattr(
                self._settings, "use_archive_file", not self._settings.use_archive_file
            ),
            "archive_file": lambda: setattr(
                self._settings, "archive_file", menu_components.select_archive_file()
            ),
            "playlist_options": lambda: setattr(
                self._settings,
                "playlist_options",
                menu_components.get_playlist_options(),
            ),
            "channel_options": lambda: setattr(
                self._settings, "channel_options", menu_components.get_channel_options()
            ),
            "download_sections": lambda: setattr(
                self._settings,
                "download_sections",
                menu_components.get_download_sections(),
            ),
            "stream_types": lambda: setattr(
                self._settings, "stream_types", menu_components.get_stream_types()
            ),
            "combine_streams": lambda: setattr(
                self._settings, "combine_streams", not self._settings.combine_streams
            ),
            "stream_select_mode": lambda: setattr(
                self._settings,
                "stream_select_mode",
                menu_components.get_stream_select_mode(),
            ),
            "output_template": lambda: setattr(
                self._settings,
                "output_template",
                menu_components.get_output_template(),
            ),
            "archive_options": lambda: setattr(
                self._settings,
                "archive_options",
                menu_components.get_archive_options(),
            ),
            "download": lambda: self.menu(self._menu_param),
        }
        while True:
            self.set_appropriate_settings()
            utility.clear()
            main_menu_choices = []
            for choices in self.main_menu_constructor():
                main_menu_choices.extend(choices)
            print(f"Download type: {self._download_type.capitalize()}\n")
            main_menu_choice = None  # Reset the main menu choice each time the user returns to the main menu
            main_menu_choice = inquirer.select(
                message=f"{'Please start by selecting a URL' if not self._settings.url else ''}",
                choices=main_menu_choices,
                default=self.get_default_choice(main_menu_choices),
                pointer=">",
                instruction="Options marked with a * are required and haven't been set yet.",
                long_instruction="Use the arrow keys to navigate, and Enter to select. Press CTRL+Z to return to the start menu.",
                mandatory=False,
            ).execute()

            if main_menu_choice in main_menu_actions:
                main_menu_actions[main_menu_choice]()
            elif main_menu_choice is None:
                return

    def menu(menu_param: MenuParam):
        """
        Main menu for the application.

        Args:
            MenuParam (MenuParam): The parameters for the menu.
        """
        download_type = (
            "download"
            if menu_param.download_type == DownloadType.DOWNLOAD
            else "archive"
        )
        settings = menu_param.Settings
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
            command_params["ffmpeg_location"] = settings.ffmpeg_location

        go_back = False

        # Loop to get the URL of the video or playlist to download
        while True:
            url = InquirerMenu.youtube_url_input().execute()
            if not menu_components.url_is_valid(url):
                answer = InquirerMenu.youtube_url_select().execute()
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
                    answer = InquirerMenu.download_folder_select().execute()
                    if answer == ChoiceEnum.SELECT.value:
                        logger.debug("User chose to select a folder.")
                        continue  # Ask for the folder again
                    elif answer == ChoiceEnum.BACK.value:
                        logger.debug("User chose to go back.")
                        break  # Go back to the URL input
                    elif answer == ChoiceEnum.MENU.value:
                        logger.debug("User chose to return to the main menu.")
                        return

                command_params["paths"] = {"home": folder}

                # Loop to get the desired archive file location
                print(
                    f"\nyt-dlp supports using an archive file to keep track of {download_type + ('ed' if menu_param.download_type == DownloadType.DOWNLOAD else 'd')} videos. It defaults to 'archive.txt'."
                )
                while True:
                    answer = InquirerMenu.use_archive_file_question().execute()
                    if answer is True:
                        logger.debug("User chose to use an archive file.")
                        print("\nPlease select the archive file: ")
                        archive_file = ui.select_file(
                            filetypes=[("Text files", "*.txt")]
                        )
                        if not archive_file:
                            logger.debug("No archive file selected.")
                            answer = InquirerMenu.archive_file_select().execute()
                            if answer == ChoiceEnum.SELECT.value:
                                continue  # Ask for the archive file again
                            elif answer == ChoiceEnum.BACK.value:
                                logger.debug("User chose to go back.")
                                break  # Go back to the folder selection
                            elif answer == ChoiceEnum.MENU.value:
                                logger.debug("User chose to return to the main menu.")
                                return  # Return to the main menu
                        logger.debug(f"Archive file selected: {archive_file}")
                        command_params["download_archive"] = archive_file

                    # Check if the URL is a playlist or video in a playlist
                    while True:
                        if go_back is True:
                            break
                        if utility.url_is_only_playlist(
                            url
                        ) or utility.url_is_video_in_playlist(url):
                            settings.is_playlist = True
                            print("\n")
                            if utility.url_is_only_playlist(url):
                                answer = InquirerMenu.url_is_playlist_select().execute()
                            else:
                                answer = (
                                    InquirerMenu.url_is_video_in_playlist_select().execute()
                                )
                            if answer == "all":
                                pass
                            elif answer == "index":
                                while True:
                                    start_index = (
                                        InquirerMenu.get_playlist_start_index().execute()
                                    )
                                    end_index = (
                                        InquirerMenu.get_playlist_end_index().execute()
                                    )
                                    if start_index > end_index:
                                        print(
                                            "The end index must be greater than or equal to the start index."
                                        )
                                        continue
                                    command_params["playliststart"] = start_index
                                    command_params["playlistend"] = end_index
                                    break
                            elif answer == "date":
                                while True:
                                    after_date: str = (
                                        InquirerMenu.get_after_date().execute()
                                    )
                                    after_date = after_date.lower()
                                    if after_date == "":
                                        after_date = ui.select_date()
                                    elif after_date in ["today", "yesterday"]:
                                        after_date = datetime.now() - timedelta(
                                            days=1 if after_date == "yesterday" else 0
                                        )
                                        after_date = after_date.strftime("%Y%m%d")

                                    before_date: str = (
                                        InquirerMenu.get_before_date().execute()
                                    )
                                    before_date = before_date.lower()
                                    if before_date == "":
                                        before_date = ui.select_date()
                                    elif before_date in ["today", "yesterday"]:
                                        before_date = datetime.now() - timedelta(
                                            days=1 if before_date == "yesterday" else 0
                                        )
                                        before_date = before_date.strftime("%Y%m%d")

                                    after_date = after_date.replace("-", "")
                                    before_date = before_date.replace("-", "")

                                    try:
                                        date_range = DateRange(after_date, before_date)
                                    except ValueError as e:
                                        print(str(e))
                                        continue

                                    command_params["daterange"] = date_range
                                    break
                            elif answer == "video":
                                command_params["no-playlist"] = True
                            elif answer == ChoiceEnum.BACK.value:
                                break
                            elif answer == ChoiceEnum.MENU.value:
                                return

                            question = InquirerMenu.reverse_order_question().execute()
                            if question is True:
                                command_params["playlistreverse"] = True

                        print("\n")
                        stream_types: list[str] = (
                            InquirerMenu.stream_type_checkbox().execute()
                        )

                        print("\n")
                        stream_select_mode = InquirerMenu.stream_select_mode(
                            "audio" in stream_types, "video" in stream_types
                        ).execute()
                        if stream_select_mode == "manual":
                            info = menu_components.get_video_info(url)
                            streams = menu_components.get_video_and_audio_streams(
                                info, stream_types
                            )
                            utility.clear()
                            answer = inquirer.checkbox(
                                message="Select the streams you want to download:",
                                choices=menu_components.create_dynamic_stream_menu(
                                    streams
                                ),
                                transformer=menu_components.stream_menu_transformer,
                                instruction="\n      [ID]     [ext]     [res]      [FPS]    [size]     [acodec]       [vcodec]     [abrate]   [vbrate]",
                                long_instruction="Press Space to select/deselect a stream, and Enter to continue.",
                                validate=lambda x: len(x) > 0,
                                invalid_message="Please select at least one stream.",
                                pointer=">",
                                enabled_symbol="[x]",
                                disabled_symbol="[ ]",
                            ).execute()

                        if menu_param.download_type == DownloadType.ARCHIVE:
                            command_params["writedescription"] = True
                            command_params["writeannotations"] = True
                            command_params["writeinfojson"] = True
                            command_params["writethumbnail"] = True
                            command_params["writeurllink"] = True
                            command_params["writewebloclink"] = True
                            command_params["writedesktoplink"] = True
                            command_params["writesubtitles"] = True
                            command_params["allsubtitles"] = True
                            command_params["overwrites"] = False
                            if settings.is_playlist:
                                if not command_params.get("no-playlist"):
                                    command_params["outtmpl"] = (
                                        "%(playlist_title)s/%(uploader)s/%(upload_date)s - %(title)s/%(upload_date)s [%(id)s].%(ext)s"
                                    )
                                else:
                                    command_params["outtmpl"] = (
                                        "%(uploader)s/%(upload_date)s - %(title)s/%(upload_date)s [%(id)s].%(ext)s"
                                    )
                            else:
                                command_params["outtmpl"] = (
                                    "%(title)s - %(uploader)s - %(upload_date)s/%(uploader)s - %(upload_date)s [%(id)s].%(ext)s"
                                )

                        with YoutubeDL(command_params) as ytdlp:
                            ytdlp.download([url])

                        input("Press Enter to continue...")
