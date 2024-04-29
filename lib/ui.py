from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename


def select_folder():
    Tk().withdraw()
    foldername = askdirectory()
    return foldername


def select_file():
    Tk().withdraw()
    filename = askopenfilename()
    return filename


def select_archive_file():
    Tk().withdraw()
    filename = askopenfilename(filetypes=[("Text files", "*.txt")])
    return filename
