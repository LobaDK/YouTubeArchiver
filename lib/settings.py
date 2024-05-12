from yt_dlp.utils import DateRange as YDLDateRange

from lib.template_constants import _TEMPLATE_FIELDS, _DEFAULT_TEMPLATES


class Settings:
    def __init__(self):
        # TODO: FEATURE: Add a way to save and load settings from a file.
        # - This will allow user-defined settings to be saved and loaded between sessions.
        # - The settings file will be a JSON file that will be saved in the same directory as the program.
        # - To simplify things, we can provide a settings sub-menu that provides options to save and reset to default settings.
        # - The program will always load the settings file on startup and apply the settings to the program.
        # - Saving settings will write the current settings to the settings file.
        # - Resetting to default settings will delete the settings file and re-initialize the settings object.
        # - We would need a function or class that acts as the settings manager.
        # - The settings manager will handle saving, loading, and resetting settings, to avoid touching the settings class directly.
        # - Either extend this feature to include output templates, or create a separate feature for output templates.

        # Template fields and default templates
        # Template fields are used to provide a list of available fields that can be used in the output template.
        # Default templates are used to provide default output templates for single videos, playlists, and channels.
        self.TEMPLATE_FIELDS = _TEMPLATE_FIELDS
        self.DEFAULT_TEMPLATES = _DEFAULT_TEMPLATES

        # "System" settings
        self.ffmpeg_is_installed = False
        self.download_type: str = None

        # General or most common settings
        self.url: str = None
        self.download_folder: str = None
        self.use_archive_file: bool = True
        self.archive_file: str = None

        # sub-class settings
        self.download_options: DownloadOptions = DownloadOptions()
        self.playlist_options: PlaylistOptions = PlaylistOptions()
        self.channel_options: ChannelOptions = ChannelOptions()

        # The following attributes are set by the program and are not user-defined.
        self.url_is_playlist: bool = False
        self.url_is_video_in_playlist: bool = False
        self.url_is_channel: bool = False
        self.extracted_info: dict = None

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
