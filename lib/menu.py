from enum import Enum
from pydantic import BaseModel
import settings


class DownloadType(Enum):
    DOWNLOAD = "download"
    ARCHIVE = "archive"


class MenuParam(BaseModel):
    settings: settings.Settings
    download_type: DownloadType


def menu(MenuParam: MenuParam):
    pass
