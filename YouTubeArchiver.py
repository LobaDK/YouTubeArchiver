import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from subprocess import CalledProcessError
from sys import platform
from zipfile import ZipFile
from functions import clear, CheckYTDL, CheckFFmpeg, notvalid, downloadytdl, downloadffmpeg, ConvertToMP3, cleanupfiles

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

errordetection = 0
#check if the youtube downloader is present
while True:
    checkYT = CheckYTDL(ytdl)
    if not checkYT:
        while True:
            print(f'{ytdlprint} not found, please download it first')
            downloadYoutubeDL = input('\nWould you like the program to download it for you? (REQUIRED) Y/N: ').upper()
            if downloadYoutubeDL == 'Y':
                if platform == 'win32' or platform == 'cygwin': #download if Windows or Cygwin
                    URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'
                    filename = ytdl + '.exe'
                    downloadytdl(URL, filename)
                    break

                elif platform == 'linux': #download if linux
                    URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp'
                    filename = ytdl
                    downloadytdl(URL, filename)
                    os.chmod(os.path.join(selfpath,ytdl), 0o700)
                    break
                        
                elif platform == 'darwin': #download if MacOS
                    URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos'
                    filename = ytdl
                    downloadytdl(URL, filename)
                    break
                    
                else:
                    print('\nError: OS not detected or supported. You will need to download it yourself')
                    time.sleep(3)
                    sys.exit(1)
            elif downloadYoutubeDL == 'N':
                print (f'\n{ytdlprint} is required, the program will now exit...')
                time.sleep(3)
                sys.exit(1)
            else:
                notvalid()
                time.sleep(2)
                clear()

    elif checkYT:
        break
    else:
        if errordetection == 3: #exit the program with exitcode 1 if it has failed 3 times to detect the downloader
            print('3rd detection error. Exiting...')
            time.sleep(3)
            sys.exit(1)
        print(f'\nError detecting {ytdlprint}. retrying...')
        errordetection += 1
        continue
if platform == 'linux' or platform == 'darwin':
    ytdlpath = shutil.which(ytdl)
    if not ytdlpath:
        ytdl = os.path.join(selfpath,ytdl)
    else:
        ytdl = ytdlpath
    
errordetection = 0
#check if ffmpeg is present
while True:
    checkFF = CheckFFmpeg()
    if not checkFF:
        while True:
            print('\nFFmpeg not found, please download it first')
            if platform == 'linux':
                print('Linux based system detected. An automated version of this is not yet available, please manually install/download ffmpeg.')
                print('Usually installing ffmpeg through your package manager is sufficient.')
                time.sleep(3)
                sys.exit(1)
            else:
                downloadFFmpeg = input('\nWould you like the program to download it for you? (REQUIRED) Y/N: ').upper()
                if downloadFFmpeg == 'Y':
                    if platform == 'win32' or platform == 'cygwin':
                        URL = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z'
                        file = 'ffmpeg.7z'
                        downloadffmpeg(URL, file)
                        print('\nExtracting...')
                        cmd = ['bin/7zr.exe', 'e', file, 'ffmpeg.exe', '-r']
                        try:
                            subprocess.run(cmd)
                            os.remove(file)
                        except KeyboardInterrupt:
                            cleanupfiles(file)
                        else:
                            print('\nExtraction done!')
                            time.sleep(2)
                            break
                    elif platform == 'darwin':
                        URL = 'https://evermeet.cx/ffmpeg/getrelease/zip'
                        file = 'ffmpeg.zip'
                        downloadffmpeg(URL, file)
                        
                        print('\nExtracting...')
                        try:
                            unzip = ZipFile(file)
                            unzip.extract(member='ffmpeg')
                            os.remove(file)
                        except KeyboardInterrupt:
                            cleanupfiles(file)
                        else:
                            print('\nExtraction done')
                            break
                    else:
                        print('\nError: OS not detected or supported. You will need to download it yourself')
                        time.sleep(3)
                        sys.exit(1)
                elif downloadFFmpeg == 'N':
                    print('\nFfmpeg is required, the program will now exit...')
                    time.sleep(3)
                    sys.exit(1)
                else:
                    notvalid()
                    time.sleep(2)
                    clear()
    elif checkFF:
        break
    else:
        if errordetection == 3: #exit the program with exitcode 1 if it has failed 3 times to detect ffmpeg
            print('3rd detection error. Exiting...')
            time.sleep(3)
            sys.exit(1)
        print('\nError detecting FFmpeg. Retrying...')
        errordetection += 1
        continue

#Main menu for the user
while True:
    badexit = False
    returntomenu = True
    clear()
    print(f'Using {ytdl}')
    print('Please select an option')
    print('\n[D]ownload')
    print('\n[A]rchive')
    print('\n[E]xit')
    mmchoice = input('\n: ').upper()
    if mmchoice == 'D':
        clear()
        while True: #used to allow the user to return to the URL section after a download
            dURL = input('\nURL of video(s) to download: ')
            if not dURL or dURL.isspace() or not dURL.startswith('http'):
                notvalid()
                time.sleep(2)
                continue
            if returntomenu:
                print('\nRemember you can drag and drop a folder into this to automatically fill out the input. Custom folder name has been removed, so please specify the exact folder you wish to download to.\nIf the folder does not already exist, it will be created, including any folders before it.')
                dest = input('\nFolder to download to: ')
                if not dest or dest.isspace():
                    notvalid()
                    time.sleep(2)
                    continue
                dest = dest.strip("\"' \t") #strips input of starting and trailing double and single quotes, as well as space and tab
                path = Path(dest)
            while True:
                if not returntomenu:
                    break
                print(f'\nIn order to prevent downloading of the same file, {ytdlprint} stores each downloaded ID in a file.\nThis file is either named "archive.txt" or a user-specified name, located in the destination folder.\nIf you have used the old batch-script version of this program, and would like to keep using the previous archives, please move or copy them into their respective folders')
                custom = input('\nWould you like to use a custom archive file? Y/N: ').upper()
                if custom == 'Y':
                    print('\nPlease do not include the .txt at the end, as it is automatically added\n')
                    archivelist = input('Archive name: ')
                    break
                elif custom == 'N':
                    archivelist = 'archive'
                    break
                else:
                    notvalid()
                    time.sleep(2)
                    continue
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
                    notvalid()
                    time.sleep(2)
                    continue
            if badexit == True:
                break

            while True:
                downloadmode = input('\nDo you want to only download [A]udio, or both [V]ideo and audio? A/V: ').upper()
                if downloadmode == 'A': #code to download only audio
                    output = dest + os.sep + '%(title)s.%(ext)s' #combine user-defined directory with the variable names used in yt-dlp
                    path.mkdir(parents=True, exist_ok=True) #create directory if it does not exist, including any missing parents
                    if "&list=" in dURL:
                        while True:
                            URLplaylist = input('\nURL is link to a playlist, do you wish to download the [E]ntire playlist, a [C]ustom range, or [S]ingle video? E/C/S: ').upper()
                            if URLplaylist == 'E':
                                cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','-f','bestaudio[ext=m4a]',dURL,'-o',output]
                                break
                            elif URLplaylist == 'C':
                                try:
                                    playlistindexstart = int(input("\nPlease write the start index, e.g. 2nd video in playlist would be '2' "))
                                except ValueError:
                                    notvalid()
                                    time.sleep(2)
                                    continue
                                try:
                                    playlistindexend = int(input("\nPlease write the end index, e.g. 8th video in playlist would be '8' "))
                                except ValueError:
                                    notvalid()
                                    time.sleep(2)
                                    continue
                                if playlistindexend <= playlistindexstart:
                                    notvalid()
                                    time.sleep(2)
                                    continue
                                cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','-I', str(playlistindexstart) + ':' + str(playlistindexend), '-f','bestaudio[ext=m4a]',dURL,'-o',output]
                                break
                            elif URLplaylist == 'S':
                                cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','--no-playlist', '-f','bestaudio[ext=m4a]',dURL,'-o',output]
                                break
                            else:
                                notvalid()
                                time.sleep(2)
                                continue
                    else:
                        cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','-f','bestaudio[ext=m4a]',dURL,'-o',output]
                    try:
                        subprocess.run(cmd,check=True)
                    except CalledProcessError:
                        print(f'\nLooks like {ytdlprint} ran into an error. Please try again')
                        badexit = True
                        time.sleep(4)
                        break
                    except: #catch exception caused if user presses CTRL+C to stop the process
                        pass
                    while True:
                        converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
                        if converttomp3 == 'Y':
                            break
                        elif converttomp3 == 'N':
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
                                    notvalid()
                                    time.sleep(2)
                                    continue
                        else:
                            notvalid()
                            time.sleep(2)
                            continue
                        break
                    break

                elif downloadmode == 'V': #insert code to download both video and audio, as well as option to extract audio from video(s)
                    pass
                else:
                    notvalid()
                    time.sleep(2)
                    continue
            if converttomp3 == 'Y':
                #insert code to convert with ffmpeg
                while True:
                    try:
                        threadcount = int(input('\nPlease specify how many simultaneous conversions you want running: '))
                    except ValueError:
                        notvalid()
                        time.sleep(2)
                        continue
                    else:
                        if threadcount <= 0:
                            notvalid()
                            time.sleep(2)
                            continue
                    threads = []
                    print(f'\nConverting m4a to MP3, using {threadcount} thread(s)...')
                    for _ in range(0,threadcount): #create user-defined amount of threads using a for loop
                        thread = threading.Thread(target=ConvertToMP3, args=(dest,))
                        thread.start()
                        threads.append(thread)
                    for jointhreads in threads:
                        jointhreads.join()


                    break
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
        clear()
        continue
    else:
        notvalid()
        time.sleep(2)
        continue
