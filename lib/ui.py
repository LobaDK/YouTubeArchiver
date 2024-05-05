from tkinter import Tk, Button
from tkinter.filedialog import askdirectory, askopenfilename
from tkcalendar import Calendar
from datetime import date
from lib.utility import ChoiceEnum
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import re


class InquirerMenu:
    def validate_youtube_url(url: str) -> bool:
        pattern = r"^https://(www\.youtube\.com/watch\?v=.{11}(&.+)?|www\.youtube\.com/playlist\?list=.+(&.+)?|youtu\.be/.+(&.+)?|music\.youtube\.com/watch\?v=.{11}(&.+)?|m\.youtube\.com/watch\?v=.{11}(&.+)?)$"
        return bool(re.match(pattern, url))

    def validate_date(date: str) -> bool:
        pattern = r"^\d{4}-\d{2}-\d{2}"
        if bool(
            date == ""
            or date.lower() in ["yesterday", "today"]
            or re.match(pattern, date)
        ):
            return True
        return False

    main_menu_options = inquirer.select(
        message="Select an option",
        choices=[
            Choice(value="D", name="Download videos"),
            Choice(value="A", name="Archive videos"),
            Choice(value="UD", name="Update yt-dlp"),
            Choice(value="UA", name="Update YouTube Archiver"),
            Choice(value="E", name="Exit"),
        ],
        default="D",
        instruction="Use the arrow keys to navigate, press Enter to select",
    )

    ffmpeg_download_question = inquirer.confirm(
        message="Do you want to download ffmpeg now?",
        default=True,
        instruction="It is not required, but it is highly recommended to have it installed. ",
    )

    continue_without_ffmpeg_question = inquirer.confirm(
        message="Do you want to continue without ffmpeg?",
        default=False,
    )

    youtube_url_input = inquirer.text(
        message="Enter the URL of the video or playlist to download/archive:",
        validate=validate_youtube_url,
    )

    youtube_url_select = inquirer.select(
        message="Please select an option:",
        choices=[
            Choice(value=ChoiceEnum.SELECT.value, name="Select a URL"),
            Choice(value=ChoiceEnum.MENU.value, name="Menu"),
        ],
    )

    download_folder_select = inquirer.select(
        message="Please select an option:",
        choices=[
            Choice(value=ChoiceEnum.SELECT.value, name="Select a folder"),
            Choice(value=ChoiceEnum.BACK.value, name="Back"),
            Choice(value=ChoiceEnum.MENU.value, name="Menu"),
        ],
    )

    use_archive_file_question = inquirer.confirm(
        message="Do you want to use an archive file?",
        default=True,
    )

    archive_file_select = inquirer.select(
        message="Please select an option:",
        choices=[
            Choice(value=ChoiceEnum.SELECT.value, name="Select an archive file"),
            Choice(value=ChoiceEnum.BACK.value, name="Back"),
            Choice(value=ChoiceEnum.MENU.value, name="Menu"),
        ],
    )

    url_is_playlist_select = inquirer.select(
        message="The URL is a playlist. Please select which you'd like to download:",
        choices=[
            Choice(value="all", name="Download all videos in the playlist"),
            Choice(value="index", name="Download a specific index in the playlist"),
            Choice(
                value="date", name="Download videos uploaded on a specific date range"
            ),
            Choice(value=ChoiceEnum.BACK.value, name="Back"),
            Choice(value=ChoiceEnum.MENU.value, name="Menu"),
        ],
    )

    url_is_video_in_playlist_select = inquirer.select(
        message="The URL is a playlist. Please select which you'd like to download:",
        choices=[
            Choice(value="all", name="Download all videos in the playlist"),
            Choice(value="index", name="Download a specific index in the playlist"),
            Choice(
                value="date", name="Download videos uploaded on a specific date range"
            ),
            Choice(value="video", name="Download the single video"),
            Choice(value=ChoiceEnum.BACK.value, name="Back"),
            Choice(value=ChoiceEnum.MENU.value, name="Menu"),
        ],
    )

    get_playlist_start_index = inquirer.text(
        message="Enter the start index of the playlist:",
        validate=lambda x: x.isdigit(),
    )

    get_playlist_end_index = inquirer.text(
        message="Enter the end index of the playlist:",
        validate=lambda x: x.isdigit(),
    )

    get_after_date = inquirer.text(
        message="Enter the start date (YYYY-MM-DD):",
        validate=validate_date,
        instruction="Press enter without typing anything to bring up the calendar. Type 'yesterday' or 'today' to select the respective date.",
    )

    get_before_date = inquirer.text(
        message="Enter the end date (YYYY-MM-DD):",
        validate=validate_date,
        instruction="Press enter without typing anything to bring up the calendar. Type 'yesterday' or 'today' to select the respective date.",
    )

    reverse_order_question = inquirer.confirm(
        message="Do you want to download the videos in reverse order?",
        default=False,
        instruction="This wil NOT reverse the order of the playlist itself, only the download order.",
    )

    media_download_checkbox = inquirer.checkbox(
        message="Select the media types you want to download:",
        choices=[
            Choice(value="audio", name="Audio"),
            Choice(value="video", name="Video"),
        ],
    )


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


def select_date():
    """
    Opens a calendar dialog box to select a date and returns the selected date.

    Returns:
        str: The selected date in the format YYYY-MM-DD.
    """

    def confirm_selection():
        selected_date[0] = cal.selection_get()
        root.destroy()

    root = Tk()
    root.title("Select a date")
    cal = Calendar(root, selectmode="day", date_pattern="y-mm-dd")
    cal.pack()

    selected_date = [None]  # Use a mutable container to store the selected date
    confirm_button = Button(root, text="Confirm", command=confirm_selection)
    confirm_button.pack()

    root.mainloop()
    selected_date: date = selected_date[0]
    return selected_date.strftime("%Y%m%d")
