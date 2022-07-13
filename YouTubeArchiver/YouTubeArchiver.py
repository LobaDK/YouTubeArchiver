import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from subprocess import CalledProcessError
from sys import platform
from zipfile import ZipFile

import requests
from tqdm import tqdm

try:
    selfpath = os.path.dirname(os.path.realpath(__file__)) #attempts to get the scripts own directory
except NameError:
    selfpath = os.path.dirname(os.path.abspath(sys.argv[0])) #runs this instead if script is used inside py2exe
ytdl = 'yt-dlp' #sets the downloader used via variable for easier swapping
ytdlprint = 'yt-dlp' #sets the displayed downloader used via variable for easier swapping

def clear():
    if platform == 'win32' or platform == 'cygwin': #used to clear the screen on Windows
        os.system('cls')
    elif platform == 'linux' or platform == 'darwin': #used to clear the screen on Linux and Mac
        os.system('clear')

def CheckYTDL(): #checks if the set youtube downloader is present
    if platform == 'Linux' or platform == 'darwin':
        if os.path.exists(os.path.join(selfpath,ytdl)): #checks if a file with the downloader name exists in the same directory as the python script
            return shutil.which(os.path.join(selfpath,ytdl)) is not None #returns True if the file is an executable
        else:
            return shutil.which(ytdl) is not None #returns true if the downloader can be launched, either from PATH or the same directory
    else:
        return shutil.which(ytdl) is not None #returns true if the downloader can be launched, either from PATH or the same directory

def CheckFFmpeg(): #checks if ffmpeg is present
    return shutil.which('ffmpeg') is not None

def notvalid():
    print('\nInput not valid, please try again')

def downloadytdl(URL, filename): #downloader function for the youtube downloader
    chunk_size = 1024 #sets chunk size for the stream
    r = requests.get(URL, stream=True)
    total_size = int(r.headers['content-length']) #sets total size to that of the content length from it's headers
    try:
        with open(filename, 'wb') as f:
            for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size), desc='Downloading', total=total_size/chunk_size, unit='KB'): #display progress bar as it's downloaded
                f.write(data)
        print('\nDownload complete!')
        time.sleep(1.5)
    except KeyboardInterrupt: #catch if the user uses the interrupt key, allowing for cleanup
        print('Cleaning up...')
        time.sleep(1)
        os.remove(ytdl + '.exe')
        print('Done!')
        sys.exit(0)
    else:
        return True
def downloadffmpeg(URL, localfile): #downloader function for ffmpeg
    chunk_size = 1024 #sets chunk size for the stream
    r = requests.get(URL, stream=True)
    total_size = int(r.headers['content-length']) #sets total size to that of the content length from it's headers
    try:
        with open(localfile, 'wb') as f:
            for data in  tqdm(iterable=r.iter_content(chunk_size=chunk_size), desc='Downloading', total=total_size/chunk_size, unit='KB'): #display progress bar as it's downloaded
                f.write(data)
        print('Download complete!')
        time.sleep(1.5)
    except KeyboardInterrupt: #catch if the user uses the interrupt key, allowing for cleanup
        print('Cleaning up...')
        time.sleep(1)
        os.remove(localfile)
        print('Done!')
        sys.exit(0)
    else:
        return

errordetection = 0
#check if the youtube downloader is present
while True:
    checkYT = CheckYTDL()
    if checkYT == False:
        while True:
            print(f'{ytdlprint} not found, please download it first')
            downloadYoutubeDL = input('\nWould you like the program to download it for you? (REQUIRED) Y/N: ').upper()
            if downloadYoutubeDL == 'Y':
                if platform == 'win32' or platform == 'cygwin': #download if Windows or Cygwin
                    URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'
                    filename = ytdl + '.exe'
                    if downloadytdl(URL, filename):
                        break

                elif platform == 'linux': #download if linux
                    URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp'
                    filename = ytdl
                    if downloadytdl(URL, filename):
                        os.chmod(os.path.join(selfpath,ytdl), 0o700)
                        break
                        
                elif platform == 'darwin': #download if MacOS
                    URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos'
                    filename = ytdl
                    if downloadytdl(URL, filename):
                        break

                else:
                    print('\nError: OS not detected or supported. You will need to download it yourself')
                    time.sleep(5)
                    sys.exit(1)
            elif downloadYoutubeDL == 'N':
                print (f'\n{ytdlprint} is required, the program will now exit...')
                time.sleep(3)
                sys.exit(1)
            else:
                notvalid()
                time.sleep(3)
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
    if checkFF == False:
        while True:
            print('\nFFmpeg not found, please download it first')
            if platform == 'linux':
                print('Linux based system detected. An automated version of this is not yet available, please manually install/download ffmpeg.')
                print('Usually installing ffmpeg through your package manager is sufficient.')
                time.sleep(5)
                sys.exit(1)
            else:
                downloadFFmpeg = input('\nWould you like the program to download it for you? (REQUIRED) Y/N: ').upper()
                if downloadFFmpeg == 'Y':
                    if platform == 'win32' or platform == 'cygwin':
                        URL = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z'
                        localfile = 'ffmpeg.7z'
                        downloadffmpeg(URL, localfile)
                        print('\nExtracting...')
                        cmd = ['bin/7zr.exe', 'e', localfile, 'ffmpeg.exe', '-r']
                        try:
                            subprocess.run(cmd)
                            os.remove(localfile)
                        except KeyboardInterrupt:
                            print('Cleaning up...')
                            time.sleep(1)
                            os.remove(localfile)
                            print('Done!')
                            sys.exit(0)
                        else:
                            print('\nExtraction done')
                            break
                    elif platform == 'darwin':
                        URL = 'https://evermeet.cx/ffmpeg/getrelease/zip'
                        localfile = 'ffmpeg.zip'
                        downloadffmpeg(URL, localfile)
                        
                        print('\nExtracting...')
                        try:
                            unzip = ZipFile(localfile)
                            unzip.extract(member='ffmpeg')
                            os.remove(localfile)
                        except KeyboardInterrupt:
                            print('Cleaning up...')
                            time.sleep(1)
                            os.remove(localfile)
                            print('Done!')
                            sys.exit(0)
                        else:
                            print('\nExtraction done')
                            break
                    else:
                        print('\nError: OS not detected or supported. You will need to download it yourself')
                        time.sleep(5)
                        sys.exit(1)
                elif downloadFFmpeg == 'N':
                    print('\nFfmpeg is required, the program will now exit...')
                    time.sleep(3)
                    sys.exit(1)
                else:
                    notvalid()
                    time.sleep(3)
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
            if returntomenu:
                print('\nRemember you can drag and drop a folder into this to automatically fill out the input. Custom folder name has been removed, so please specify the exact folder you wish to download to.\nIf the folder does not already exist, it will be created, including any folders before it.')
                dest = input('\nFolder to download to: ')
                dest = dest.strip("\"' \t") #strips input of starting and trailing double and single quotes, as well as space and tab
                path = Path(dest)
            while True:
                if returntomenu == False:
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
                    continue
            while True:
                if returntomenu == False:
                    break
                test = input('\nWould you like to run a test first? Y/N: ').upper()
                if test == 'Y':
                    output = dest + os.sep + '%(title)s.%(ext)s'
                    path.mkdir(parents=True, exist_ok=True)
                    print('\nTesting the 5 first videos...\n')
                    cmd = [ytdl,'--abort-on-error','-s','--add-metadata','--get-title','--get-filename','--get-format','--playlist-start','1','--playlist-end','5','-f','bestvideo[ext=mp4]+bestaudio[ext=m4a]',dURL,'-o',output]
                    try:
                        subprocess.run(cmd,check=True)
                    except CalledProcessError:
                        print('\nAn error has been detected in the test. This is likely caused by the input being wrong. Please try again')
                        badexit = True
                        time.sleep(5)
                    except: #catch exception caused if user presses CTRL+C to stop the process
                        pass
                    break
                if test == 'N':
                    break #break into the next loop
                else:
                    notvalid()
            if badexit == True:
                break

            while True:
                downloadmode = input('\nDo you want to only download [A]udio, or both [V]ideo and audio? A/V: ').upper()
                if downloadmode == 'A': #code to download only audio
                    output = dest + os.sep + '%(title)s.%(ext)s'
                    path.mkdir(parents=True, exist_ok=True)
                    cmda = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','-f','bestaudio[ext=m4a]',dURL,'-o',output]
                    try:
                        subprocess.run(cmda,check=True)
                    except CalledProcessError:
                        print(f'\nLooks like {ytdlprint} ran into an error. Please try again')
                        badexit = True
                        time.sleep(4)
                        break
                    except: #catch exception caused if user presses CTRL+C to stop the process
                        pass
                    while True:
                        converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s').upper()
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
                                    continue
                        else:
                            notvalid()
                            continue
                        break
                    break

                if downloadmode == 'V': #insert code to download both video and audio, as well as option to extract audio from video(s)
                    pass
            if converttomp3 == 'Y':
                            #insert code to convert with ffmpeg
                            pass
            if badexit:
                break
            if returntomenu:
                break
            if returntomenu == False:
                continue
    elif mmchoice == 'A':
        #insert code for archiver
        pass
    elif mmchoice == 'E':
        sys.exit()
    elif mmchoice == 'DAE':
        print('\nhaha very funny')
        time.sleep(3)
        clear()
        continue
    else:
        notvalid()
        time.sleep(2)
