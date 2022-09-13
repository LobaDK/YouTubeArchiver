import sys
import time

from functions.functions import YTA
from functions.mainfunc import mainfunc


class Archive():

    def archive(ytdl, ytdlprint, returntomenu):
        mode = 'archive'
        while True:    

            dURL = mainfunc.SelectURL()

            if returntomenu:
                path, dest = mainfunc.SelectFolder()

            if returntomenu:
                archivelist = mainfunc.SelectArchive(ytdlprint)

            cmd, link_type = mainfunc.ArchiveType(dURL, ytdl, dest, archivelist)

            cmd.extend(['--write-description', '--write-annotations', '--write-info-json', '--write-thumbnail', '--all-subs', '--sub-format', '"best/ass/srt"', '--embed-subs', '--no-overwrites', '--no-continue', '--sleep-interval', '5', '--max-sleep-interval', '10', '--add-metadata', '--compat-options', 'no-live-chat'])

            if returntomenu:
                testprompt = mainfunc.Test(ytdl, dest, path, dURL)
                if testprompt == 'N':
                    return
            
            if link_type == 'channel':
                output_template = '%(uploader)s/%(uploader)s - %(upload_date)s - %(title)s/%(uploader)s - %(upload_date)s [%(id)s].%(ext)s'
            if link_type == 'playlist':
                if '--no-playlist' in cmd:
                    output_template = '%(uploader)s/%(upload_date)s - %(title)s/%(upload_date)s [%(id)s].%(ext)s'
                else:
                    output_template = '%(playlist_title)s/%(uploader)s/%(upload_date)s - %(title)s/%(upload_date)s [%(id)s].%(ext)s'
            else:
                output_template = '%(title)s - %(uploader)s - %(upload_date)s/%(uploader)s - %(upload_date)s [%(id)s].%(ext)s'

            output = mainfunc.CreateDirectoryAndOutput(dest, path, output_template)
            
            mainfunc.DownloadMode(dURL, output, cmd, dest, mode)
            
            while True:
                returnmode = input('\n[E]xit, return to [M]ain menu or to [I]nput field using previous settings? E/M/I: ').upper()
                if returnmode == 'E':
                    sys.exit()
                elif returnmode == 'M':
                    returntomenu = True
                    return
                elif returnmode == 'I':
                    returntomenu = False
                    break
                else:
                    YTA.notvalid()
                    time.sleep(2)
                    continue

            if not returntomenu:
                continue
