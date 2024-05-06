from InquirerPy.base.control import Choice
from typing import Any, Generator
from yt_dlp import YoutubeDL, DownloadError
from lib.utility import logger


def convert_bytes_to_human_readable(size: int) -> str:
    """
    Converts a byte size to a human-readable format.

    Args:
        size (int): The size in bytes.

    Returns:
        str: The human-readable size.
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.2f}{unit}"


def stream_menu_transformer(choices: str | list[str]) -> str:
    """
    Transforms the stream menu choices into a string.

    Args:
        choices (str | list[str]): The choices to transform.

    Returns:
        str: The transformed string.
    """
    transformed_string = "Selected streams: "
    for choice in choices:
        transformed_string += f"{choice.split("|")[0].strip()}"
        if choice != choices[-1]:
            transformed_string += ", "
    return transformed_string


def create_dynamic_stream_menu(
    streams: list[dict[str, Any]]
) -> Generator[Choice, None, None]:
    """
    Creates a dynamic stream menu based on the provided list of streams.

    Args:
        streams (List[dict[str, Any]]): A list of dictionaries representing the streams.

    Yields:
        Generator[Choice, None, None]: A generator that yields Choice objects representing the stream menu options.
    """
    yield Choice(value="all", name="All streams")
    for stream in streams:
        stream_string = convert_stream_to_string(stream)
        yield Choice(value=stream["format_id"], name=stream_string)


def convert_stream_to_string(stream: dict[str, Any]) -> str:
    """
    Converts a stream dictionary to a formatted string.

    Args:
        stream (dict[str, Any]): The stream dictionary containing information about the stream.

    Returns:
        str: The formatted string representation of the stream.

    """
    # Show the format ID, extension, resolution, fps (if available), file size, codec (if both audio and video are present, show both) and bitrate (if both audio and video are present, show both)
    format_id = stream.get("format_id", "N/A") or "N/A"
    extension = stream.get("ext", "N/A") or "N/A"
    resolution = stream.get("resolution", "N/A") or "N/A"
    fps = stream.get("fps", "N/A") or "N/A"
    file_size = stream.get("filesize", "N/A") or "N/A"
    acodec = stream.get("acodec", "N/A") or "N/A"
    vcodec = stream.get("vcodec", "N/A") or "N/A"
    abr = stream.get("abr", "N/A") or "N/A"
    vbr = stream.get("vbr", "N/A") or "N/A"

    if isinstance(file_size, int):
        file_size = convert_bytes_to_human_readable(file_size)

    stream_string = f"{format_id:<7} | {extension:<4} | {resolution:<10} | {fps:<5} | {file_size:<8} | {acodec:<10} | {vcodec:<14} | {abr:<7} | {vbr:<7}"
    return stream_string


def get_video_and_audio_streams(
    info: dict[str, list[dict[str, Any]]],
    stream_types: list[str],
) -> list[dict[str, Any]]:
    """
    Retrieves the video and audio streams from the given info dictionary.

    Args:
        info (dict[str, list[dict[str, Any]]]): The dictionary containing information about the video streams.

    Returns:
        list[dict[str, Any]]: A list of dictionaries representing the video and audio streams.

    """
    streams = []
    for stream in info["formats"]:
        if (stream.get("acodec") != "none" and "audio" in stream_types) or (stream.get("vcodec") != "none" and "video" in stream_types):
            logger.debug(f"Stream found: {stream['format_id']}")
            streams.append(stream)
    return streams


def get_video_info(url: str) -> dict | None:
    """
    Retrieves information about a video from the given URL.

    Args:
        url (str): The URL of the video.

    Returns:
        dict | None: A dictionary containing the video information, or None if an error occurred.
    """
    with YoutubeDL(
        {
            "logger": logger,
        }
    ) as ytdlp:
        try:
            info = ytdlp.extract_info(url, download=False)
            info = ytdlp.sanitize_info(info)
            return info
        except DownloadError as e:
            logger.error(e)
            return None


def url_is_valid(url: str):
    logger.debug(f"User entered URL: {url}")
    print("\nTesting URL. Press Ctrl+C to skip.")
    try:
        with YoutubeDL(
            {
                "logger": logger,
                "playlist_items": "1",
                "lazy_playlist": True,
                "noplaylist": True,
            }
        ) as ytdlp:
            ytdlp.extract_info(url, download=False)
            logger.info(f"Test complete: {url}")
            return True
    except KeyboardInterrupt:
        logger.debug("User skipped URL testing.")
        return True
    except DownloadError as e:
        logger.info(e)
        return False
