from lib import misc, menu  # noqa
import logging  # noqa


class Settings:
    def __init__(self):
        try:
            self.ffmpeg_is_installed = misc.ffmpeg_is_installed()
        except Exception:
            self.ffmpeg_is_installed = False
        self.logger = None  # type: logging.Logger
        self.download_type = None  # type: menu.DownloadType
