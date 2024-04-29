import sys
import os
import time
import shutil
import logging
from pathlib import Path

from .menu import Choice


def create_folder(folder: Path, logger: logging.Logger):
    """
    Create a folder at the specified path.

    Args:
        folder (Path): The path of the folder to create.
        logger (logging.Logger): The logger object for logging messages.

    Returns:
        bool: True if the folder was created successfully, False otherwise.
    """
    try:
        folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created folder: {str(folder)}")
        return True
    except (OSError, PermissionError, NotADirectoryError):
        logger.error(
            "An error occurred while creating the folder. Please refer to the logs if this continues.",
            exc_info=True,
        )
        return False


def get_user_input(prompt: str, default: str = Choice.YES.value, lower: bool = True):
    """
    Prompts the user for input with the given prompt and returns the user's input.
    If the user enters an empty string, the default value is returned instead.

    Args:
        prompt (str): The prompt to display to the user.
        default (str, optional): The default value to return if the user enters an empty string.
            Defaults to Choice.YES.value.
        lower (bool, optional): Whether to convert the user's input to lowercase. Defaults to True.

    Returns:
        str: The user's input or the default value if the user enters an empty string.
    """
    return (input(prompt) or default).lower() if lower else input(prompt) or default


def clear():
    """
    Clears the console screen.

    This function checks the platform and uses the appropriate command to clear the console screen.
    On Windows, it uses the "cls" command, and on other platforms, it uses the "clear" command.

    Note: This function relies on the `os` and `sys` modules.

    Example usage:
    clear()
    """
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def not_valid_input(option: str):
    """
    Prints a message for an invalid input.

    This function prints a message to the console for an invalid input option.

    Args:
        option (str): The invalid input option.

    Example usage:
    not_valid_input("X")
    """
    print(f"Invalid option: {option if option else None}. Please enter a valid option.")
    time.sleep(3)


def ffmpeg_is_installed():
    """
    Check if ffmpeg is installed on the system.

    Returns:
        bool: True if ffmpeg is installed, False otherwise.
    """
    return any(
        [
            shutil.which("ffmpeg") is not None,
            os.path.isfile("bin/ffmpeg"),
            os.path.isfile("bin/ffmpeg.exe"),
        ]
    )
