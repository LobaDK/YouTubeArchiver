class Settings:
    def __init__(self):
        from lib import menu, utility  # noqa
        import logging  # noqa

        try:
            self.ffmpeg_is_installed = utility.ffmpeg_is_installed()
        except Exception:
            self.ffmpeg_is_installed = False
        self.logger = None  # type: logging.Logger
        self.download_type = None  # type: menu.DownloadType
