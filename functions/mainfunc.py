import os
import subprocess
import time
import threading
from pathlib import Path
from subprocess import CalledProcessError

from functions.functions import YTA


class mainfunc:
    def SelectURL():
        YTA.clear()
        while True: #used to allow the user to return to the URL section after a download
            dURL = input('\nURL of video(s) to download: ')
            if not dURL or dURL.isspace() or not dURL.startswith('http'):
                YTA.notvalid()
                time.sleep(2)
                continue
            return dURL

    def SelectFolder():
        while True:
            print('\nRemember you can drag and drop a folder into this to automatically fill out the input. Custom folder name has been removed, so please specify the exact folder you wish to download to.\nIf the folder does not already exist, it will be created, including any folders before it.')
            dest = input('\nFolder to download to: ')
            if not dest or dest.isspace():
                YTA.notvalid()
                time.sleep(2)
                continue
            dest = dest.strip("\"' \t") #strips input of starting and trailing double and single quotes, as well as space and tab
            path = Path(dest)
            return path, dest

    def SelectArchive(ytdlprint):
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

    def YouTubePlaylist(ytdl, dest, archivelist, link_type, dURL):
        while True:
            if link_type == 'playlist':
                if '&list=' in dURL:
                    URLplaylist = input('\nURL is link to a playlist, do you wish to download the [E]ntire playlist, a [C]ustom range, or [S]ingle video? E/C/S: ').upper()
                elif 'playlist?list=' in dURL:
                    URLplaylist = input('\nURL is link to a playlist, do you wish to download the [E]ntire playlist, or [C]ustom range? E/C: ').upper()
            else:
                URLplaylist = input('\nURL is link to a channel, do you wish to download the [E]ntire channel, or [C]ustom range? E/C: ').upper()
            if URLplaylist == 'E':
                cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata', '--yes-playlist']
                while True:
                    if link_type == 'playlist':
                        playlistoptions = input('\nDownload in [R]andom order, R[E]verse order, [S]kip playlist indexing and start download immediately, or [N]one? R/E/S/N: ').upper()
                    else:
                        playlistoptions = input('\nDownload in [R]andom order, R[E]verse order, [S]kip channel indexing and start download immediately, or [N]one? R/E/S/N: ').upper()
                    if playlistoptions == 'R':
                        playlistcustom = '--playlist-random'
                        cmd.append(playlistcustom)
                        break
                    elif playlistoptions == 'E':
                        playlistcustom = '--playlist-reverse'
                        cmd.append(playlistcustom)
                        break
                    elif playlistoptions == 'S':
                        playlistcustom = '--lazy-playlist'
                        cmd.append(playlistcustom)
                        break
                    elif playlistoptions == 'N':
                        break
                    else:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                return cmd
            elif URLplaylist == 'C':
                cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata', '--yes-playlist']
                
                while True:
                    reverseorder = input('\nReverse playlist order? Y/N: ').upper()
                    if reverseorder == 'Y':
                        break
                    elif reverseorder == 'N':
                        break
                    else:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                
                while True:
                    try:
                        if reverseorder == 'Y':
                            playlistindexstart = int(input("\nPlease write the start index, e.g. 2nd last video in playlist would be '2': "))
                        else:
                            playlistindexstart = int(input("\nPlease write the start index, e.g. 2nd video in playlist would be '2': "))
                    except ValueError:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    try:
                        if reverseorder == 'Y':
                            playlistindexend = int(input("\nPlease write the end index, e.g. 8th last video in playlist would be '8': "))
                        else:
                            playlistindexend = int(input("\nPlease write the end index, e.g. 8th video in playlist would be '8': "))
                    except ValueError:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    if playlistindexstart <= 0 or playlistindexend <= 0:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    elif playlistindexend <= playlistindexstart:
                        YTA.notvalid()
                        time.sleep(2)
                        continue
                    elif reverseorder == 'Y':
                        playlistindexstart = '-' + str(playlistindexstart)
                        playlistindexend = '-' + str(playlistindexend)
                        playlistindex = f'{playlistindexstart}:{playlistindexend}:-1'
                    else:
                        playlistindex = f'{str(playlistindexstart)}:{str(playlistindexend)}'
                    
                    cmd.extend(['-I', playlistindex])
                    return cmd
            elif URLplaylist == 'S' and link_type == 'playlist' and not 'playlist?list=' in dURL:
                cmd = [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata','--no-playlist']
                return cmd
            else:
                YTA.notvalid()
                time.sleep(2)
                continue

    def NoYouTubePlaylist(ytdl, dest , archivelist):
        return [ytdl,'--download-archive',dest + os.sep + archivelist + '.txt','-i','--add-metadata', '--compat-options', 'no-live-chat']

    def Test(ytdl, dest, path, dURL):
        while True:
            test = input('\nWould you like to run a test first? Y/N: ').upper()
            if test == 'Y':
                output = dest + os.sep + '%(title)s.%(ext)s'
                path.mkdir(parents=True, exist_ok=True)
                print('\nTesting the 5 (if there are 5) first videos...\n')
                cmd = [ytdl,'--abort-on-error','-s','--add-metadata','--get-title','--get-filename','--get-format','--playlist-start','1','--playlist-end','5','-f','bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',dURL,'-o',output]
                try:
                    subprocess.run(cmd,check=True)
                except CalledProcessError as e:
                    while True:
                        print('\n',e)
                        print('\nAn error has been detected in the test. Please review the errors/warnings. if this keeps happening, please report it on Github and include the text above.')
                        testprompt = input('\nContinue anyways? Y/N: ').upper()
                        if testprompt == 'Y' or testprompt == 'N':
                            return testprompt
                        else:
                            YTA.notvalid()
                            time.sleep(2)
                            continue
                except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
                    return
            if test == 'N':
                return #break into the next loop
            else:
                YTA.notvalid()
                time.sleep(2)
                continue

    def CreateDirectoryAndOutput(dest, path, output_template):
        output = dest + os.sep + output_template #combine user-defined directory with the variable names used in yt-dlp
        path.mkdir(parents=True, exist_ok=True) #create directory if it does not exist, including any missing parents
        return output

    def DownloadMode(dURL, output, cmd, dest, mode):
        while True:
            downloadmode = input('\nA for only audio, V for only video, and AV for both, with option to separate audio from video. A/V/AV: ').upper()
            if downloadmode == 'A': #code to download only audio
                cmd2 = ['-f', 'ba[ext=m4a]', dURL, '-o', output] #ba[ext=m4a] = download best m4a file
                cmd.extend(cmd2)
                try:
                    subprocess.run(cmd, check=True)
                except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
                    pass
                except Exception as e:
                    print(e)
                if mode == 'archive':
                    break
                while True:
                    converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
                    if converttomp3 == 'Y':
                        while True:
                            try:
                                threadcount = int(input('\nPlease specify how many simultaneous conversions you want running: '))
                            except ValueError:
                                YTA.notvalid()
                                time.sleep(2)
                                continue
                            else:
                                if threadcount <= 0:
                                    YTA.notvalid()
                                    time.sleep(2)
                                    continue
                            threads = []
                            print(f'\nConverting m4a to MP3, using {threadcount} thread(s)...')
                            for _ in range(0,threadcount): #create user-defined amount of threads using a for loop
                                thread = threading.Thread(target=YTA.ConvertToMP3, args=(dest,))
                                thread.start()
                                threads.append(thread)
                            for jointhreads in threads:
                                jointhreads.join()
                            break
                        break
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
                print(' '.join(cmd))
                try:
                    subprocess.run(cmd, check=True)
                except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
                    pass
                except Exception as e:
                    print(e)
                if audio_extract == 'Y' and mode == 'download':
                    while True:
                        converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
                        if converttomp3 == 'Y':
                            while True:
                                try:
                                    threadcount = int(input('\nPlease specify how many simultaneous conversions you want running: '))
                                except ValueError:
                                    YTA.notvalid()
                                    time.sleep(2)
                                    continue
                                else:
                                    if threadcount <= 0:
                                        YTA.notvalid()
                                        time.sleep(2)
                                        continue
                                threads = []
                                print(f'\nConverting m4a to MP3, using {threadcount} thread(s)...')
                                for _ in range(0,threadcount): #create user-defined amount of threads using a for loop
                                    thread = threading.Thread(target=YTA.ConvertToMP3, args=(dest,))
                                    thread.start()
                                    threads.append(thread)
                                for jointhreads in threads:
                                    jointhreads.join()
                                break
                            break
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
                except Exception as e:
                    print(e)
            else:
                YTA.notvalid()
                time.sleep(2)
                continue
            break

    def ArchiveType(dURL, ytdl, dest, archivelist):
        while True:
            if 'www.youtube.com/c/' in dURL and '/videos' in dURL:
                link_type = 'channel'
                cmd = mainfunc.YouTubePlaylist(ytdl, dest, archivelist, link_type, dURL)
                return cmd, link_type
            elif '&list=' in dURL or '/playlist?list=' in dURL:
                link_type = 'playlist'
                cmd = mainfunc.YouTubePlaylist(ytdl, dest, archivelist, link_type, dURL)
                return cmd, link_type
            elif 'watch?v=' in dURL and not '&list=' in dURL:
                link_type = 'single'
                cmd = mainfunc.NoYouTubePlaylist(ytdl, dest , archivelist)
                return cmd, link_type
            else:
                print('Could not detect if link is to channel, playlist, direct with playlist, or direct')
                exit(1) #not able to detect the ArchiveType