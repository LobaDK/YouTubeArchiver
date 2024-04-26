import sys
import os
import time
import shutil


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
    return any([shutil.which("ffmpeg"), shutil.which("bin/ffmpeg")])
