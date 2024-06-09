import json
from yt_dlp.utils import DateRange as YDLDateRange

from lib.utility import logger, determine_url_type
from lib.template_constants import _TEMPLATE_FIELDS, _DEFAULT_TEMPLATES


class Settings:
    def __init__(self):

        # Template fields and default templates
        # Template fields are used to provide a list of available fields that can be used in the output template.
        # Default templates are used to provide default output templates for single videos, playlists, and channels.
        self.TEMPLATE_FIELDS = _TEMPLATE_FIELDS
        self.DEFAULT_TEMPLATES = _DEFAULT_TEMPLATES

        # "System" settings
        self.ffmpeg_is_installed = False
        self.ffmpeg_path = None

        # General settings
        self._url: str = None
        self.persistent: PersistentSettings = PersistentSettings()

        # The following attributes are set by the program and are not user-defined.
        self.url_is_set: bool = False
        self.url_is_playlist: bool = False
        self.url_is_video_in_playlist: bool = False
        self.url_is_channel: bool = False
        self.url_is_video: bool = False
        self.extracted_info: dict = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
        self.url_is_set = value is not None
        url_type = determine_url_type(value)
        self.url_is_playlist = url_type == "playlist"
        self.url_is_video_in_playlist = url_type == "video_in_playlist"
        self.url_is_channel = url_type == "channel"
        self.url_is_video = url_type == "video"

    @property
    def expected_downloads(self):
        """
        Returns the expected number of downloads based on the provided settings.

        Returns:
            int or None: The expected number of downloads. If the number can be determined, it returns an integer. If the number cannot be determined, it returns None.
        """
        # If the URL is not a playlist or channel, or if the URL is a video in a playlist where no_playlist is set to True, return 1.
        if not (self.url_is_playlist or self.url_is_channel) or (
            self.url_is_video_in_playlist and self.playlist_options.no_playlist
        ):
            return 1
        # If the URL is a playlist and the playlist index range is set, return the number of videos in the index range.
        if (self.url_is_playlist and self.playlist_options.index_range.get_range) or (
            self.url_is_channel and self.channel_options.index_range.get_range
        ):
            if self.url_is_playlist:
                start, stop = map(
                    int, self.playlist_options.index_range.get_range.split(":")
                )
            elif self.url_is_channel:
                start, stop = map(
                    int, self.channel_options.index_range.get_range.split(":")
                )
            return stop - start + 1
        # If the URL is a playlist or channel and the date range is set, return None as we can't determine the number of videos.
        if (
            self.url_is_playlist and self.playlist_options.date_range.get_date_range
        ) or (self.url_is_channel and self.channel_options.date_range.get_date_range):
            return None
        # If the URL is a playlist or channel, it will have an "entries" key in the extracted_info dictionary, where each entry is a video.
        if "entries" in self.extracted_info:
            return len(self.extracted_info["entries"])
        # If we can't determine the number of expected downloads, return None.
        return None


class PersistentSettings:
    """
    Represents persistent settings that are saved and loaded from a file.

    Attributes:
        download_folder (str): The folder to download videos to. Acts as the `--output` option in yt-dlp.
        use_archive_file (bool): Flag indicating whether to use an archive file to keep track of downloaded videos. Acts as the `--download-archive` option in yt-dlp.
        archive_file (str): The archive file to keep track of downloaded videos. Acts as the `--download-archive` option in yt-dlp.
        download_mode (str): A preset of settings to apply to the program (e.g., download or archive). Not used in yt-dlp.
        download_options (DownloadOptions): The download options.
        playlist_options (PlaylistOptions): The playlist options.
        channel_options (ChannelOptions): The channel options.
    """

    def __init__(self) -> None:
        self._download_folder: str = None
        self.use_archive_file: bool = True
        self.archive_file: str = None

        self.download_mode: str = "download"

        # sub-class settings
        self.download_options: DownloadOptions = DownloadOptions()
        self.playlist_options: PlaylistOptions = PlaylistOptions()
        self.channel_options: ChannelOptions = ChannelOptions()

    @property
    def download_folder(self):
        return self._download_folder

    @download_folder.setter
    def download_folder(self, value):
        self._download_folder = value
        self.download_folder_is_set = value is not None


class IndexRange:
    """
    Represents an index range.

    An index range consists of a start and stop value. This class provides
    methods to get the index range as a string. Acts as the `--playlist-items` option in yt-dlp.

    Attributes:
        start (str): The start value of the index range. Starts off as None. Acts as the `START:` range for the `--playlist-items` option in yt-dlp.
        stop (str): The stop value of the index range. Starts off as None. Acts as the `:STOP` range for the `--playlist-items` option in yt-dlp.

    Properties:
        get_range (str or None): The index range as a string, or None if either start
        or stop is not defined. Acts as the `START:STOP` range for the `--playlist-items` option in yt-dlp.
    """

    def __init__(self):
        self.start: str = None
        self.stop: str = None

    @property
    def get_range(self) -> str | None:
        """
        Returns the index range as a string.

        If both start and stop are defined, the index range is returned
        as a string in the format "{start}:{stop}". If either start
        or stop is not defined, None is returned. This option acts as the `--playlist-items START:STOP` option in yt-dlp.

        Returns:
            str or None: The index range as a string, or None if either start
            or stop is not defined.
        """
        return f"{self.start}:{self.stop}" if self.start and self.stop else None


class DateRange:
    """
    Represents a date range.

    A date range consists of an after date and a before date. This class provides
    methods to get the date range as a yt_dlp.utils.DateRange object. Acts as the `--dateafter` and `--datebefore` options in yt-dlp.

    Attributes:
        after_date (str): The after date of the date range. Acts as the `--dateafter` option in yt-dlp.
        before_date (str): The before date of the date range. Acts as the `--datebefore` option in yt-dlp.
    """

    def __init__(self):
        self.after_date: str = None
        self.before_date: str = None

    @property
    def get_date_range(self):
        """
        Returns a DateRange object representing the date range between `after_date` and `before_date`.

        If both `after_date` and `before_date` are provided, a DateRange object is created with `after_date` as the start date and `before_date` as the end date.
        If either `after_date` or `before_date` is missing, None is returned. This option acts as the combination of the `--dateafter` and `--datebefore` options in yt-dlp.

        Returns:
            DateRange or None: A DateRange object representing the date range, or None if either `after_date` or `before_date` is missing.
        """
        return (
            YDLDateRange(after=self.after_date, before=self.before_date)
            if self.after_date and self.before_date
            else None
        )


class DownloadOptions:
    """
    Represents various download-related options.

    Attributes:
        download_sections (list[str]): The sections to download. Availability heavily dependent on a lot of factors. Acts as the `--download-sections` option in yt-dlp.
        stream_types (list[str]): The types of streams to download (e.g., video, audio). Doesn't do anything on its own, but is used to filter which streams to download and which format options to show.
        stream_select_mode (str): The mode for selecting streams (e.g., Guided, Advanced). Also doesn't do anything on its own, but is used to determine which options the user has to select streams. i.e., if Guided mode is selected, the user can only select from a list of built-in format specifiers.
        stream_formats (list[str]): The formats of streams to download. The ID can be the literal ID of the stream, or a built-in format specifier (e.g., "bestvideo[ext=mp4]", "bestaudio[ext=m4a]"). Acts as the `--format` option in yt-dlp.
        output_template (str): The template for the output file names. Acts as the `--output` option in yt-dlp.
        combine_streams (bool): Whether to combine video and audio streams. Other settings may affect/override this setting. If True, acts as including a `+` between the video and audio formats in the `--format` option in yt-dlp, otherwise, acts as including a `,` between the video and audio formats in the `--format` option in yt-dlp.
    """

    def __init__(self):
        self.download_sections: list[str] = None
        self.stream_types: list[str] = ["video", "audio"]
        self.stream_select_mode: str = "Guided"
        self.stream_formats: list[str] = [
            "bestvideo[ext=mp4]",
            "bestaudio[ext=m4a]",
        ]
        self.output_template: str = _DEFAULT_TEMPLATES["default"]
        self.combine_streams: bool = True


class PlaylistAndChannelBaseOptions:
    """
    Represents the base options for a playlist or channel.

    Attributes:
        index_range (IndexRange): The range of indices to consider. Acts as the `--playlist-items` option in yt-dlp.
        date_range (DateRange): The range of dates to consider. Acts as the `--dateafter` and `--datebefore` options in yt-dlp.
        playlist_random (bool): Flag indicating whether to download the playlist in a random order. Acts as the `--playlist-random` option in yt-dlp.
        playlist_reverse (bool): Flag indicating whether to download the playlist in reverse order. Acts as the `--playlist-reverse` option in yt-dlp.
        lazy_playlist (bool): Flag indicating whether to download videos in the playlist without downloading the playlist index. Acts as the `--lazy-playlist` option in yt-dlp.
    """

    def __init__(self):
        self.index_range: IndexRange = IndexRange()
        self.date_range: DateRange = DateRange()
        self.playlist_random: bool = False
        self.playlist_reverse: bool = False
        self.lazy_playlist: bool = False


class PlaylistOptions(PlaylistAndChannelBaseOptions):
    """
    Represents various playlist-related options.

    Attributes:
        Inherits all attributes from PlaylistAndChannelBaseOptions.
        no_playlist (bool): Flag indicating whether to download the playlist index. Acts as the `--[yes|no]-playlist` option in yt-dlp.
    """

    def __init__(self):
        self.no_playlist: bool = False


class ChannelOptions(PlaylistAndChannelBaseOptions):
    """
    Represents various channel-related options.

    Attributes:
        Inherits all attributes from PlaylistAndChannelBaseOptions.
    """

    def __init__(self):
        # All options for playlists are also available for channels in yt-dlp
        # except for the `--[yes|no]-playlist` options.
        pass


class SettingsManager:
    """
    The SettingsManager class provides methods to save, load, reset, and sanitize settings.

    It allows saving settings to a file, loading settings from a file, loading default settings,
    resetting settings to default values, and sanitizing input data to ensure correct types and recognized settings.

    Note:
        This class does not perform any error handling and expects the calling code to handle any exceptions that may occur.

    Usage:
        ```python
        SettingsManager.save_settings(settings, "settings.json")
        settings = SettingsManager.load_settings("settings.json")
        settings = SettingsManager.load_default_settings()
        settings = SettingsManager.reset_settings(settings)
        data = SettingsManager.sanitize_settings(data)
        ```
    """

    # TODO: Either extend SettingsManager to include output templates, or create a separate feature for output templates.

    @staticmethod
    def save_settings(from_object: Settings, to_file: str):
        """
        Low-level method to save settings to a file.

        Converts the settings object to a dictionary and dumps it to a JSON file.
        Before saving, it sanitizes the settings to ensure that the keys are recognized settings and the values have the correct type.
        Only the persistent settings are saved.

        Args:
            from_object (Settings): The settings object to save.
            to_file (str): The file to save the settings to.
        """
        sanitized_settings = SettingsManager.sanitize_settings(
            vars(from_object.persistent)
        )
        with open(to_file, "w") as f:
            json.dump(sanitized_settings, f, indent=4)

    @staticmethod
    def load_settings(from_file: str) -> Settings:
        """
        Low-level method to load settings from a file.

        A JSON file from a dumped PersistentSettings object is expected.
        The method will attempt to check and sanitize the JSON data before applying it to the settings object.

        Args:
            from_file (str): The file to load the settings from.

        Returns:
            Settings: The settings object with values loaded from the file.
        """
        with open(from_file, "r") as f:
            settings = Settings()
            settings.persistent.__dict__.update(
                SettingsManager.sanitize_settings(json.load(f))
            )
            return settings

    @staticmethod
    def load_default_settings() -> Settings:
        """
        Low-level method to load default settings.

        Returns:
            Settings: The settings object with default values.
        """
        return Settings()

    @staticmethod
    def sanitize_settings(data: dict) -> Settings:
        """
        Sanitizes the input data dictionary by checking if the keys are recognized settings.
        If a key is not recognized, it ignores the setting.
        If a key is recognized, it checks if the value has the correct type.
        If the value has an incorrect type, it uses the default value for that setting.
        Returns the sanitized data dictionary.

        note:
            This method is used internally by the SettingsManager class to sanitize settings data before applying it to the settings object.

        Args:
            data (dict): The input data dictionary containing the settings.

        Returns:
            dict: The sanitized data dictionary containing the settings.

        """
        settings = Settings()
        settings_vars = vars(settings.persistent)
        sanitized_data = {}
        for key in data.keys():
            if key not in settings_vars:
                logger.warning(
                    f"The setting {key} is not recognized. Ignoring this setting."
                )
                continue
            if not isinstance(data[key], type(settings_vars[key])):
                logger.warning(
                    f"Incorrect type for key {key} in JSON config. Expected {type(settings_vars[key])}, got {type(data[key])}. Using default value."
                )
                sanitized_data[key] = settings_vars[key]
            else:
                sanitized_data[key] = data[key]
        return sanitized_data
