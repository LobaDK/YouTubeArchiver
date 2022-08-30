import os
import shutil
import subprocess
import sys
import time
from sys import platform
from zipfile import ZipFile

from functions import YTA


class check:

    def ytdlcheck(selfpath, ytdl, ytdlprint):
        errordetection = 0
        #check if the youtube downloader is present
        while True:
            checkYT = YTA.CheckYTDL(ytdl)
            if not checkYT:
                while True:
                    print(f'{ytdlprint} not found, please download it first')
                    downloadYoutubeDL = input('\nWould you like the program to download it for you? (REQUIRED) Y/N: ').upper()
                    if downloadYoutubeDL == 'Y':
                        if platform == 'win32' or platform == 'cygwin': #download if Windows or Cygwin
                            URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'
                            filename = ytdl + '.exe'
                            YTA.downloadytdl(URL, filename)
                            break

                        elif platform == 'linux': #download if linux
                            URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp'
                            filename = ytdl
                            YTA.downloadytdl(URL, filename)
                            os.chmod(os.path.join(selfpath,ytdl), 0o700)
                            break
                            
                        elif platform == 'darwin': #download if MacOS
                            URL = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos'
                            filename = ytdl
                            YTA.downloadytdl(URL, filename)
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
                        YTA.notvalid()
                        time.sleep(2)
                        YTA.clear()

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
        return ytdl

    def ffmpegcheck():
        errordetection = 0
        #check if ffmpeg is present
        while True:
            checkFF = YTA.CheckFFmpeg()
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
                                YTA.downloadffmpeg(URL, file)
                                print('\nExtracting...')
                                cmd = ['bin/7zr.exe', 'e', file, 'ffmpeg.exe', '-r']
                                try:
                                    subprocess.run(cmd)
                                    os.remove(file)
                                except KeyboardInterrupt:
                                    YTA.cleanupfiles(file)
                                else:
                                    print('\nExtraction done!')
                                    time.sleep(2)
                                    break
                            elif platform == 'darwin':
                                URL = 'https://evermeet.cx/ffmpeg/getrelease/zip'
                                file = 'ffmpeg.zip'
                                YTA.downloadffmpeg(URL, file)
                            
                                print('\nExtracting...')
                                try:
                                    unzip = ZipFile(file)
                                    unzip.extract(member='ffmpeg')
                                    os.remove(file)
                                except KeyboardInterrupt:
                                    YTA.cleanupfiles(file)
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
                            YTA.notvalid()
                            time.sleep(2)
                            YTA.clear()
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
