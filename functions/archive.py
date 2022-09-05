import sys
import time

from functions.functions import YTA
from functions.mainfunc import mainfunc


class Archive():

    def archive(ytdl, ytdlprint):
        while True:    
            returntomenu = True

            dURL = mainfunc.SelectURL()

            if returntomenu:
                path, dest = mainfunc.SelectFolder()

            if returntomenu:
                archivelist = mainfunc.SelectArchive(ytdlprint)

            mainfunc.ArchiveType(dURL)

            if "&list=" in dURL:
                cmd = mainfunc.YouTubePlaylist(ytdl, dest, archivelist)
                
            else:
                cmd = mainfunc.NoYouTubePlaylist(ytdl, dest, archivelist)

            if returntomenu:
                testprompt = mainfunc.Test(ytdl, dest, path, dURL)
                if testprompt == 'N':
                    return
            

            output = mainfunc.CreateDirectoryAndOutput(dest, path)
            
            mainfunc.DownloadMode(dURL, output, cmd, dest)
            
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
