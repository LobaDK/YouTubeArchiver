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

    def main_menu_options():
        return inquirer.select(
            message="Please select an option:",
            choices=[
                Choice(value="D", name="Download"),
                Choice(value="A", name="Archive"),
                Choice(value="UD", name="Update yt-dlp"),
                Choice(value="UA", name="Update YouTube Archiver"),
                Choice(value="E", name="Exit"),
            ],
            pointer=">",
        )

    def ffmpeg_download_question():
        return inquirer.confirm(
            message="Do you want to download ffmpeg?",
            default=True,
        )

    def continue_without_ffmpeg_question():
        return inquirer.confirm(
            message="Do you want to continue without ffmpeg?",
            default=False,
        )

    def youtube_url_input():
        return inquirer.text(
            message="Enter a YouTube URL:",
            validate=InquirerMenu.validate_youtube_url,
        )

    def youtube_url_select():
        return inquirer.select(
            message="Please select an option:",
            choices=[
                Choice(value=ChoiceEnum.SELECT.value, name="Select a URL"),
                Choice(value=ChoiceEnum.BACK.value, name="Back"),
            ],
            pointer=">",
        )

    def download_folder_select():
        return inquirer.select(
            message="Please select an option:",
            choices=[
                Choice(value=ChoiceEnum.SELECT.value, name="Select a folder"),
                Choice(value=ChoiceEnum.BACK.value, name="Back"),
                Choice(value=ChoiceEnum.MENU.value, name="Menu"),
            ],
            pointer=">",
        )

    def use_archive_file_question():
        return inquirer.confirm(
            message="Do you want to use an archive file?",
            default=True,
        )

    def archive_file_select():
        return inquirer.select(
            message="Please select an option:",
            choices=[
                Choice(value=ChoiceEnum.SELECT.value, name="Select an archive file"),
                Choice(value=ChoiceEnum.BACK.value, name="Back"),
                Choice(value=ChoiceEnum.MENU.value, name="Menu"),
            ],
            pointer=">",
        )

    def url_is_playlist_select(url_is_video_in_playlist: bool):
        choices = [
            Choice(value="all", name="Download all videos in the playlist"),
            Choice(value="index", name="Download a specific index in the playlist"),
            Choice(
                value="date", name="Download videos uploaded on a specific date range"
            ),
            Choice(value=ChoiceEnum.BACK.value, name="Back"),
            Choice(value=ChoiceEnum.MENU.value, name="Menu"),
        ]

        if url_is_video_in_playlist:
            choices.insert(3, Choice(value="video", name="Download the single video"))

        return inquirer.select(
            message="The URL is a playlist. Please select which you'd like to download:",
            choices=choices,
            pointer=">",
        )

    def get_playlist_start_index():
        return inquirer.text(
            message="Enter the start index of the playlist:",
            validate=lambda x: x.isdigit(),
        )

    def get_playlist_end_index():
        return inquirer.text(
            message="Enter the end index of the playlist:",
            validate=lambda x: x.isdigit(),
        )

    def get_after_date():
        return inquirer.text(
            message="Enter the start date (YYYY-MM-DD):",
            validate=InquirerMenu.validate_date,
            instruction="Press enter without typing anything to bring up the calendar. Type 'yesterday' or 'today' to select the respective date.",
        )

    def get_before_date():
        return inquirer.text(
            message="Enter the end date (YYYY-MM-DD):",
            validate=InquirerMenu.validate_date,
            instruction="Press enter without typing anything to bring up the calendar. Type 'yesterday' or 'today' to select the respective date.",
        )

    def reverse_order_question():
        return inquirer.confirm(
            message="Do you want to download the videos in reverse order?",
            default=False,
        )

    def stream_type_checkbox():
        return inquirer.checkbox(
            message="Select the stream types to download:",
            choices=[
                Choice(value="audio", name="Audio", enabled=True),
                Choice(value="video", name="Video", enabled=True),
            ],
            pointer=">",
            enabled_symbol="[x]",
            disabled_symbol="[ ]",
            validate=lambda x: len(x) > 0,
            invalid_message="Please select at least one stream type.",
        )

    def stream_select_mode(is_audio_selected: bool, is_video_selected: bool):
        choices = []
        if is_audio_selected and not is_video_selected:
            choices.append(
                Choice(value="bestaudio", name="Select best auto-detected audio stream")
            )
            choices.append(
                Choice(
                    value="worstaudio", name="Select worst auto-detected audio stream"
                )
            )
        elif is_video_selected and not is_audio_selected:
            choices.append(
                Choice(value="bestvideo", name="Select best auto-detected video stream")
            )
            choices.append(
                Choice(
                    value="worstvideo", name="Select worst auto-detected video stream"
                )
            )
        else:
            choices.append(
                Choice(
                    value="bestva",
                    name="Select best auto-detected video and audio. (Default - Highest quality)",
                )
            )
            choices.append(
                Choice(
                    value="worstva",
                    name="Select worst auto-detected video and audio.",
                )
            )
            choices.append(
                Choice(
                    value="best",
                    name="Select best auto-detected stream with pre-merged audio",
                )
            )
            choices.append(
                Choice(
                    value="worst",
                    name="Select worst auto-detected stream with pre-merged audio",
                )
            )

        choices.append(
            Choice(
                value="manual",
                name="Select streams manually (Advanced - Automatic merging is disabled)",
            )
        )

        return inquirer.select(
            message="Please select an option:",
            choices=choices,
            pointer=">",
        )

    def stream_combine_question():
        return inquirer.select(
            message="Select an option:",
            choices=[
                Choice(value="merge", name="Merge audio and video"),
                Choice(
                    value="mergeandkeep",
                    name="Merge audio and video, keep separate files",
                ),
                Choice(value="separate", name="Keep audio and video separate"),
            ],
            pointer=">",
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
