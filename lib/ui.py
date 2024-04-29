from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename


def select_folder():
    root = Tk()
    root.withdraw()
    folder = askdirectory()
    root.destroy()
    return folder


def select_file():
    root = Tk()
    root.withdraw()
    file = askopenfilename()
    root.destroy()
    return file


def select_archive_file():
    root = Tk()
    root.withdraw()
    filename = askopenfilename(filetypes=[("Text files", "*.txt")])
    root.destroy()
    return filename
