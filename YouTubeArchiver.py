import os
import subprocess
import sys
import time
from pathlib import Path
from subprocess import CalledProcessError

from checks import check
from functions import YTA

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
returnmode = ""
while True:
    badexit = False
    returntomenu = True
    YTA.clear()
    print(f'Using {ytdl}')
    print('Please select an option')
    print('\n[D]ownload')
    print('\n[A]rchive')
    print('\n[E]xit')
    mmchoice = input('\n: ').upper()
    if mmchoice == 'D':
        YTA.clear()
        while True: #used to allow the user to return to the URL section after a download
            if returnmode == 'M':
                break
            dURL = input('\nURL of video(s) to download: ')
            if not dURL or dURL.isspace() or not dURL.startswith('http'):
                YTA.notvalid()
                time.sleep(2)
                continue

            while True:
                if returntomenu:
                    print('\nRemember you can drag and drop a folder into this to automatically fill out the input. Custom folder name has been removed, so please specify the exact folder you wish to download to.\nIf the folder does not already exist, it will be created, including any folders before it.')
                    dest = input('\nFolder to download to: ')
                    if not dest or dest.isspace():
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    dest = dest.strip("\"' \t") #strips input of starting and trailing double and single quotes, as well as space and tab
                    path = Path(dest)

                while True:
                    if not returntomenu:
                        break
                    print(f'\nIn order to prevent downloading of the same file, {ytdlprint} stores each downloaded ID in a file.\nThis file is either named "archive.txt" or a user-specified name, located in the destination folder.\nIf you have used the old batch-script version of this program, and would like to keep using the previous archives, please move or copy them into their respective folders')
                    custom = input('\nWould you like to use a custom archive filename? Y/N: ').upper()
                    if custom == 'Y':
                        print('\nPlease do not include the .txt at the end, as it is automatically added\n')
                        archivelist = input('Archive name: ')
                        break
                    elif custom == 'N':
                        archivelist = 'archive'
                        break
                    else:
                        YTA.notvalid()
                        time.sleep(2)
                        continue

                if "&list=" in dURL:
                    while True:
                        URLplaylist = input('\nURL is link to a playlist, do you wish to download the [E]ntire playlist, a [C]ustom range, or [S]ingle video? E/C/S: ').upper()
                        if URLplaylist == 'E':
                            cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata']
                            while True:
                                playlistoptions = input('\nDownload in [R]andom order, [S]kip playlist indexing and start download immediately, or [N]either? R/S/N: ').upper()
                                if playlistoptions == 'R':
                                    playlistcustom = '--playlist-random'
                                    cmd.insert(0, playlistcustom)
                                    break
                                elif playlistoptions == 'S':
                                    playlistcustom = '--lazy-playlist'
                                    cmd.insert(0, playlistcustom)
                                    break
                                elif playlistoptions == 'N':
                                    break
                                else:
                                    YTA.notvalid()
                                    time.sleep(2)
                                    continue
                            break
                        elif URLplaylist == 'C':
                            try:
                                playlistindexstart = int(input("\nPlease write the start index, e.g. 2nd video in playlist would be '2': "))
                            except ValueError:
                                YTA.notvalid()
                                time.sleep(2)
                                continue
                            try:
                                playlistindexend = int(input("\nPlease write the end index, e.g. 8th video in playlist would be '8': "))
                            except ValueError:
                                YTA.notvalid()
                                time.sleep(2)
                                continue
                            if playlistindexend <= playlistindexstart:
                                YTA.notvalid()
                                time.sleep(2)
                                continue
                            cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','-I', str(playlistindexstart) + ':' + str(playlistindexend)]
                            break
                        elif URLplaylist == 'S':
                            cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','--no-playlist']
                            break
                        else:
                            YTA.notvalid()
                            time.sleep(2)
                            continue
                else:
                    cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata']

                while True:
                    if not returntomenu:
                        break
                    test = input('\nWould you like to run a test first? Y/N: ').upper()
                    if test == 'Y':
                        output = dest + os.sep + '%(title)s.%(ext)s'
                        path.mkdir(parents=True, exist_ok=True)
                        print('\nTesting the 5 (if there are 5) first videos...\n')
                        cmd = [ytdl,'--abort-on-error','-s','--add-metadata','--get-title','--get-filename','--get-format','--playlist-start','1','--playlist-end','5','-f','bestvideo[ext=mp4]+bestaudio[ext=m4a]',dURL,'-o',output]
                        try:
                            subprocess.run(cmd,check=True)
                        except CalledProcessError:
                            print('\nAn error has been detected in the test. This is likely caused by the input being wrong. Please try again')
                            badexit = True
                            time.sleep(3)
                        except: #catch exception caused if user presses CTRL+C to stop the process
                            pass
                        break
                    if test == 'N':
                        break #break into the next loop
                    else:
                        YTA.notvalid()
                        time.sleep(2)
                        continue

                if badexit == True:
                    break

                output = dest + os.sep + '%(title)s.%(ext)s' #combine user-defined directory with the variable names used in yt-dlp
                path.mkdir(parents=True, exist_ok=True) #create directory if it does not exist, including any missing parents

                while True:
                    downloadmode = input('\nA for only audio, V for only video, and AV for both, with option to separate audio from video. A/V/AV: ').upper()
                    if downloadmode == 'A': #code to download only audio
                        cmd2 = ['-f', 'ba[ext=m4a]', dURL, '-o', output] #ba[ext=m4a] = download best m4a file
                        cmd.extend(cmd2)
                        try:
                            subprocess.run(cmd, check=True)
                        except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
                            pass
                        while True:
                            converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
                            if converttomp3 == 'Y':
                                YTA.converttomp3(dest)
                            elif converttomp3 == 'N':
                                break
                            else:
                                YTA.notvalid()
                                time.sleep(2)
                                continue
                        break

                    elif downloadmode == 'AV': #code to download video and audio together
                        while True:
                            audio_extract = input('\nWould you like to separate the audio from the video(s)? Y/N: ').upper()
                            if audio_extract == 'N':
                                cmd2 = ['-f', 'bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]', dURL, '-o', output] #bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] = get the best mp4 and m4a audio file, and combine them, and if not, get the best already-combined mp4
                            elif audio_extract == 'Y':
                                cmd2 = ['-f', 'bv[ext=mp4],ba[ext=m4a]', dURL, '-o', output] #bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] = get the best mp4 and m4a audio file, and combine them, and if not, get the best already-combined mp4
                            else:
                                YTA.notvalid()
                                time.sleep(2)
                                continue
                            break
                        
                        cmd.extend(cmd2)
                        try:
                            subprocess.run(cmd, check=True)
                        except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
                            pass

                        if audio_extract == 'Y':
                            while True:
                                converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
                                if converttomp3 == 'Y':
                                    YTA.converttomp3(dest)
                                elif converttomp3 == 'N':
                                    break
                                else:
                                    YTA.notvalid()
                                    time.sleep(2)
                                    continue

                    elif downloadmode == 'V':
                        cmd2 = ['-f', 'bv[ext=mp4]', dURL, '-o', output] #bv[ext=mp4] = download best mp4 without audio
                        cmd.extend(cmd2)
                        try:
                            subprocess.run(cmd, check=True)
                        except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
                            pass
                    else:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    break

                while True:
                    returnmode = input('\n[E]xit, return to [M]ain menu or to [I]nput field using previous settings? E/M/I: ').upper()
                    if returnmode == 'E':
                        sys.exit()
                    elif returnmode == 'M':
                        returntomenu = True
                        break
                    elif returnmode == 'I':
                        returntomenu = False
                        break
                    else:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    
                if badexit:
                    break
                if returntomenu:
                    break
                elif not returntomenu:
                    continue
                break
    elif mmchoice == 'A':
        #insert code for archiver
        pass
    elif mmchoice == 'E':
        sys.exit()
    elif mmchoice == 'DAE':
        print('\nhaha very funny')
        time.sleep(2)
        YTA.clear()
        continue
    else:
        YTA.notvalid()
        time.sleep(2)
        continue
