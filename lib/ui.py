from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename


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
    file = askopenfilename(filetypes=filetypes)
    root.destroy()
    return file
