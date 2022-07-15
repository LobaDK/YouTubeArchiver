# Installing
Clone the project or grab the `YouTubeArchiver.py` file as well as the `bin` folder and it's contents. It is required to extract the 7z FFmpeg download.

FFmpeg and (obviously) a YouTube downloader is required, and can be installed either via PATH or by putting them in the same directory as the python script is located.
This has been tested with youtube-dl, yt-dlc and yt-dlp, though is geared towards the latter considering it's the only properly working one it seems.

The script will automatically prompt, and attempt, to download the latest, system-specific binary, of ffmpeg and yt-dlp, if one is not found (with some limitations due to my lack of Python knowledge).

As always, use `pip install -r requirements.txt` to install the necessary modules, if not already installed
