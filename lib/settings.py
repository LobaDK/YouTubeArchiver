class Settings:
    def __init__(self):
        from lib import menu, utility  # noqa
        import logging  # noqa

        try:
            self.ffmpeg_is_installed, self.ffmpeg_location = (
                utility.ffmpeg_is_installed()
            )
        except Exception:
            self.ffmpeg_is_installed = False
        self.logger = None  # type: logging.Logger
        self.download_type = None  # type: menu.DownloadType
        self.url = None  # type: str
        self.download_folder = None  # type: str
        self.use_archive_file = True  # type: bool
        self.archive_file = None  # type: str
        self.url_is_playlist = False  # type: bool
        self.url_is_video_in_playlist = False  # type: bool
        self.url_is_channel = False  # type: bool
        self.playlist_options = None  # type: dict[str, str]
        self.channel_options = None  # type: dict[str, str]
        self.expected_download_count = 0  # type: int
        self.download_sections = None  # type: list[str]
        self.stream_types = ["video", "audio"]  # type: list[str]
        self.stream_select_mode = "Automatic"  # type: str
        self.stream_formats = [
            "bestvideo[ext=mp4]",
            "bestaudio[ext=m4a]",
        ]  # type: list[str]
        self.output_template = None  # type: str
        self.archive_options = None  # type: dict[str, str]
        self.combine_streams = True  # type: bool
        self.ignore_playlist = False  # type: bool
