import subprocess
from subprocess import CalledProcessError
import time
import os
import sys

from functions.functions import YTA
from functions.mainfunc import mainfunc

class Download():

    badexit = False
    returntomenu = True

    dURL = mainfunc.selecturl()

    if returntomenu:
        path = mainfunc.selectfolder()

    if returntomenu:
        archivelist = mainfunc.selectarchive(ytdlprint)

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
        except CalledProcessError as e:
            while True:
                print('\n',e)
                print('\nAn error has been detected in the test. Please review the errors/warnings. if this keeps happening, please report it on Github and include the text above.')
                testprompt = input('\nContinue anyways? Y/N: ').upper()
                if testprompt == 'Y':
                    break
                elif testprompt == 'N':
                    return
                else:
                    YTA.notvalid()
                    time.sleep(2)
                    continue
        except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
            pass
        break
    if test == 'N':
        break #break into the next loop
    else:
        YTA.notvalid()
        time.sleep(2)
        continue

    if badexit == True:
    return

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
        except Exception as e:
            print(e)
        while True:
            converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
            if converttomp3 == 'Y':
                YTA.convert(dest)
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
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt: #catch exception caused if user presses CTRL+C to stop the process
            pass
        except Exception as e:
            print(e)
        if audio_extract == 'Y':
            while True:
                converttomp3 = input('\nWould you like to convert the audio files to MP3? Y/N: \nNote: This will immediately start converting any m4a files in the destination folder, to MP3\'s: ').upper()
                if converttomp3 == 'Y':
                    YTA.convert(dest)
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
    return
    if returntomenu:
    return
    elif not returntomenu:
    continue
    break
