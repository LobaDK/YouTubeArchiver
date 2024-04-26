import misc


class Settings:
    try:
        ffmpeg_is_installed = misc.ffmpeg_is_installed()
    except Exception:
        ffmpeg_is_installed = False
    logger = None
    download_type = None
