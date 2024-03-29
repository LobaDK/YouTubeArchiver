import os
import sys
import time

from functions.checks import check
from functions.download import Download
from functions.archive import Archive
from functions.functions import YTA

try:
    os.chdir(os.path.dirname(__file__))
except:
    os.chdir(os.path.dirname(sys.argv[0]))
try:
    selfpath = os.path.dirname(os.path.realpath(__file__)) #attempts to get the scripts own directory
except NameError:
    selfpath = os.path.dirname(os.path.abspath(sys.argv[0])) #runs this instead if script is used inside py2exe

ytdl = 'yt-dlp' #sets the downloader used via variable for easier swapping
ytdlprint = 'yt-dlp' #sets the displayed downloader used via variable for easier swapping

ytdl = check.ytdlcheck(selfpath, ytdl, ytdlprint)

check.ffmpegcheck()

#Main menu for the user
while True:
    returntomenu = True
    YTA.clear()
    print(f'Using {ytdl}')
    print('Please select an option')
    print('\n[D]ownload')
    print('\n[A]rchive')
    print('\n[E]xit')
    mmchoice = input('\n: ').upper()
    if mmchoice == 'D':
        Download.download(ytdl, ytdlprint, returntomenu)
    elif mmchoice == 'A':
        Archive.archive(ytdl, ytdlprint, returntomenu)
    elif mmchoice == 'E':
        sys.exit()
    elif 'D' and 'A' and 'E' in mmchoice and len(mmchoice) == 3:
        print('\nhaha very funny')
        time.sleep(2)
        YTA.clear()
        continue
    else:
        YTA.notvalid()
        time.sleep(2)
        continue
