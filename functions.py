import requests
import glob
from tqdm import tqdm
from sys import platform
import shutil
import os
import time
import subprocess
from pathlib import Path
import sys

def clear():
    if platform == 'win32' or platform == 'cygwin': #used to clear the screen on Windows
        os.system('cls')
    elif platform == 'linux' or platform == 'darwin': #used to clear the screen on Linux and Mac
        os.system('clear')

def CheckYTDL(ytdl): #checks if the set youtube downloader is present
    if platform == 'Linux' or platform == 'darwin':
        if os.path.exists(ytdl): #checks if a file with the downloader name exists in the same directory as the python script
            return shutil.which(ytdl) is not None #returns True if the file is an executable
        else:
            return shutil.which(ytdl) is not None #returns true if the downloader can be launched, either from PATH or the same directory
    else:
        return shutil.which(ytdl) is not None #returns true if the downloader can be launched, either from PATH or the same directory

def CheckFFmpeg(): #checks if ffmpeg is present
    return shutil.which('ffmpeg') is not None

def notvalid():
    print('\nInput not valid, please try again')

def downloadytdl(URL, file): #downloader function for the youtube downloader
    chunk_size = 1024 #sets chunk size for the stream
    r = requests.get(URL, stream=True, timeout=10)
    total_size = int(r.headers['content-length']) #sets total size to that of the content length from it's headers
    try:
        with open(file, 'wb') as f:
            for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size), desc='Downloading', total=total_size/chunk_size, unit='KB'): #display progress bar as it's downloaded
                f.write(data)
        print('\nDownload complete!')
        time.sleep(1.5)
    except KeyboardInterrupt: #catch if the user uses the interrupt key, allowing for cleanup
        cleanupfiles(file)
    except requests.exceptions.Timeout: #catch if the connection to the server timed out
        print('\nServer did not respond within 10 seconds, and the download has therefore stopped.')
        cleanupfiles(file)
    else:
        return

def downloadffmpeg(URL, file): #downloader function for ffmpeg
    chunk_size = 1024 #sets chunk size for the stream
    r = requests.get(URL, stream=True, timeout=10)
    total_size = int(r.headers['content-length']) #sets total size to that of the content length from it's headers
    try:
        with open(file, 'wb') as f:
            for data in  tqdm(iterable=r.iter_content(chunk_size=chunk_size), desc='Downloading', total=total_size/chunk_size, unit='KB'): #display progress bar as it's downloaded
                f.write(data)
        print('Download complete!')
        time.sleep(1.5)
    except KeyboardInterrupt: #catch if the user uses the interrupt key, allowing for cleanup
        cleanupfiles(file)
    except requests.exceptions.Timeout: #catch if the connection to the server timed out
        print('\nServer did not respond within 10 seconds, and the download has therefore stopped.')
        cleanupfiles(file)
    else:
        return

def ConvertToMP3(dest):
    files = glob.glob(os.path.join(dest,'*.m4a'))
    try:
        os.makedirs(dest + ' MP3')
    except:
        pass
    for file in files:
        outputfile = Path(file).stem + '.mp3'
        cmd = ['ffmpeg', '-n', '-i', file, '-b:a', '128k', os.path.join(dest + ' MP3', outputfile)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def cleanupfiles(file):
    print('Cleaning up...')
    time.sleep(1)
    try:
        os.remove(file)
    except:
        print('Trying to remove files in use, waiting...')
        time.sleep(5)
        try:
            os.remove(file)
        except:
            print('Failed to delete partially downloaded file!')
            time.sleep(2)
            sys.exit(0)
        else:
            print('Done!')
            sys.exit(0)
    else:
        print('Done!')
        sys.exit(0)