from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename
from lib.utility import Choice


class InquirerMenu:
    youtube_url_input = [
        {
            "type": "input",
            "name": "url",
            "message": "Enter the URL of the video or playlist:",
        }
    ]

    youtube_url_select = [
        {
            "type": "list",
            "name": "url_select",
            "message": "The URL is invalid. Please select an option:",
            "choices": [
                {"name": "Select a URL", "value": Choice.SELECT.value},
                {"name": "Menu", "value": Choice.MENU.value},
            ],
        }
    ]

    download_folder_select = [
        {
            "type": "list",
            "name": "download_folder",
            "message": "Please select an option:",
            "choices": [
                {"name": "Select a folder", "value": Choice.SELECT.value},
                {"name": "Back", "value": Choice.BACK.value},
                {"name": "Menu", "value": Choice.MENU.value},
            ],
        }
    ]

    use_archive_file_question = [
        {
            "type": "confirm",
            "name": "use_archive_file",
            "message": "Do you want to use an archive file?",
            "default": True,
        }
    ]

    archive_file_select = [
        {
            "type": "list",
            "name": "archive_file",
            "message": "Please select an option:",
            "choices": [
                {"name": "Select an archive file", "value": Choice.SELECT.value},
                {"name": "Back", "value": Choice.BACK.value},
                {"name": "Menu", "value": Choice.MENU.value},
            ],
        }
    ]


def select_folder():
    """
    Opens a dialog box to select a folder and returns the selected folder path.

    Returns:
        str: The path of the selected folder.
    """
    root = Tk()
    root.withdraw()
    folder = askdirectory()
    root.destroy()
    return folder


def select_file(filetypes: list[tuple[str, str]] = None) -> str:
    """
    Opens a file dialog to allow the user to select a file.

    Args:
        filetypes (list[tuple[str, str]], optional): A list of file types to filter the displayed files. Each file type is represented as a tuple of the form (file type description, file extension). Defaults to None.

    Returns:
        str: The path of the selected file.

    """
    root = Tk()
    root.withdraw()
    if filetypes is not None:
        file = askopenfilename(filetypes=filetypes)
    else:
        file = askopenfilename()
    root.destroy()
    return file
