from enum import Enum
from pydantic import BaseModel, ConfigDict
from textwrap import dedent
from yt_dlp import YoutubeDL
from yt_dlp.utils import DateRange
from datetime import datetime, timedelta
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

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


keybindings = {
    "skip": [{"key": "c-z"}, {"key": "b"}, {"key": "backspace"}],
}


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

    def set_download_mode_settings(self):
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

    def main_menu_constructor(self) -> list[Choice]:
        """
        Dynamically constructs the main menu for the application based on the current settings.

        Returns:
            list[Choice]: A list of Choice objects representing the main menu options.
        """
        choices = []
        choices.append(
            Choice(
                value="select_url",
                name=f"Select URL: {'*' if not self._settings.url else self._settings.url}",
            )
        )
        if (
            self._settings.url
        ):  # Only show the rest of the options if a URL has been selected
            choices.append(
                Separator()
            )  # Add a separator between the URL and folder selection
            choices.append(
                Choice(
                    value="select_folder",
                    name=f"Select Folder: {'*' if not self._settings.download_folder else self._settings.download_folder}",
                )
            )
            choices.append(
                Separator()
            )  # Add a separator between the folder and archive file selection
            choices.append(
                Choice(
                    value="use_archive_file",
                    name=f"Use Archive File: {menu_components.format_boolean(self._settings.use_archive_file)}",
                )
            )
            if (
                self._settings.use_archive_file
            ):  # Only show the archive file option if the user wants to use an archive file
                choices.append(
                    Choice(
                        value="archive_file",
                        name=f"Archive File: {'*' if not self._settings.archive_file else self._settings.archive_file}",
                    )
                )
            choices.append(
                Separator()
            )  # Add a separator between the archive file and playlist options
            if (
                self._settings.url_is_playlist
                or self._settings.url_is_video_in_playlist
            ):
                choices.append(
                    Choice(
                        value="playlist_options",
                        name=f"Playlist Options: {self._settings.playlist_options}",
                    )
                )
            if self._settings.url_is_channel:
                choices.append(
                    Choice(
                        value="channel_options",
                        name=f"Channel Options: {self._settings.channel_options}",
                    )
                )
            choices.append(Separator())
            choices.append(
                Choice(
                    value="download_options",
                    name="Download Options:",  # TODO: Display a * if not all required sub-menu settings are set. This will require a function to check if all required settings are set.
                )
            )
            if self._menu_param.download_type == DownloadType.ARCHIVE:
                choices.append(
                    Choice(
                        value="archive_options",
                        name=f"Archive Options: {self._settings.archive_options}",
                    )
                )
            if self.check_required_settings():
                choices.append(
                    Choice(
                        value="start_download",
                        name=f"start {self._download_type.capitalize()}",
                    )
                )
        return [choices]

    def get_default_choice(self, choices: list[Choice]) -> str:
        """
        Returns the default choice from the given list of choices.

        The default choice is determined by the following rules:
        - The first choice containing "*" is returned.
        - If no choice contains "*", and all required settings are set, the "start download" choice is returned.
        - If no choice contains "*", and not all required settings are set, the first choice is returned.

        Args:
            choices (list[Choice]): The list of choices to select from.

        Returns:
            str: The default choice.

        """
        for choice in choices:
            if isinstance(choice, Choice):
                if "*" in choice.name:
                    return choice.value
        if self.check_required_settings():
            return "start_download"
        return choices[0].value

    def download_options_menu(self):
        """
        Menu for setting download options.
        """
        download_options_actions = {
            "stream_types": lambda: setattr(
                self._settings,
                "stream_types",
                menu_components.get_stream_types(),
            ),
            "stream_select_mode": lambda: setattr(
                self._settings,
                "stream_select_mode",
                menu_components.get_stream_select_mode(),
            ),
            "combine_streams": lambda: setattr(
                self._settings,
                "combine_streams",
                not self._settings.combine_streams,
            ),
            "stream_select_formats": lambda: setattr(
                self._settings,
                "stream_formats",
                menu_components.get_stream_formats(
                    self._settings.stream_types, self._settings.combine_streams
                ),
            ),
            "output_template": lambda: setattr(
                self._settings,
                "output_template",
                menu_components.get_output_template(self._settings.output_template),
            ),
        }
        while True:
            utility.clear()
            download_options_choices = []
            for choices in self.main_menu_constructor():
                download_options_choices.extend(choices)
            download_options_choice = inquirer.select(
                message="Select an option to configure:",
                choices=download_options_choices,
                default=self.get_default_choice(download_options_choices),
                pointer=">",
                long_instruction="Use the arrow keys to navigate, and Enter to select. Press CTRL+Z or 'B' to return to the main menu.",
                keybindings=keybindings,
            ).execute()

            if download_options_choice in download_options_actions:
                download_options_actions[download_options_choice]()
            elif download_options_choice is None:
                return

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
            "download_options": lambda: self.download_options_menu(),
            "archive_options": lambda: setattr(
                self._settings,
                "archive_options",
                menu_components.get_archive_options(),
            ),
            "download": lambda: self.download(),
        }
        self.set_download_mode_settings()
        while True:
            utility.clear()
            main_menu_choices = []
            for choices in self.main_menu_constructor():
                main_menu_choices.extend(choices)
            print(f"Download type: {self._download_type.capitalize()}\n")
            main_menu_choice = inquirer.select(
                message=f"{'Please start by selecting a URL:' if not self._settings.url else 'Options marked with a * are required and have not been set yet.'}",
                choices=main_menu_choices,
                default=self.get_default_choice(main_menu_choices),
                pointer=">",
                long_instruction="Use the arrow keys to navigate, and Enter to select. Press CTRL+Z or 'B' to return to the main menu.",
                mandatory=False,
                keybindings=keybindings,
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
