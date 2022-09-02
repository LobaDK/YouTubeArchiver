from functions.functions import YTA
import time
from pathlib import Path

class mainfunc:
    def selecturl():
        YTA.clear()
        while True: #used to allow the user to return to the URL section after a download
            dURL = input('\nURL of video(s) to download: ')
            if not dURL or dURL.isspace() or not dURL.startswith('http'):
                YTA.notvalid()
                time.sleep(2)
                continue
            return dURL

    def selectfolder():
        while True:
            print('\nRemember you can drag and drop a folder into this to automatically fill out the input. Custom folder name has been removed, so please specify the exact folder you wish to download to.\nIf the folder does not already exist, it will be created, including any folders before it.')
            dest = input('\nFolder to download to: ')
            if not dest or dest.isspace():
                YTA.notvalid()
                time.sleep(2)
                continue
            dest = dest.strip("\"' \t") #strips input of starting and trailing double and single quotes, as well as space and tab
            path = Path(dest)
            return path

    def selectarchive(ytdlprint):
            while True:
                print(f'\nIn order to prevent downloading of the same file, {ytdlprint} stores each downloaded ID in a file.\nThis file is either named "archive.txt" or a user-specified name, located in the destination folder.\nIf you have used the old batch-script version of this program, and would like to keep using the previous archives, please move or copy them into their respective folders')
                custom = input('\nWould you like to use a custom archive filename? Y/N: ').upper()
                if custom == 'Y':
                    print('\nPlease do not include the .txt at the end, as it is automatically added\n')
                    archivelist = input('Archive name: ')
                elif custom == 'N':
                    archivelist = 'archive'
                else:
                    YTA.notvalid()
                    time.sleep(2)
                    continue
                return archivelist