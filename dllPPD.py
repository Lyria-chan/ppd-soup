import requests, zipfile, os, re, pykakasi, json, shutil, gdown
import eel
from niconico_dl import NicoNicoVideo
from pytubefix import YouTube
from bs4 import BeautifulSoup

session = requests.Session()
def ppr(str):
    try:
        eel.jsPrint(str)
    except:
        pass
    print(str)


def san_win_name(filename, substitute = '_'):
    invalid_chars = r'[\\/:\*\?"<>|]'
    sanitized_filename = re.sub(invalid_chars, substitute, filename)
    return sanitized_filename

def callPath(path = '', mode = 'python'):
    while True:
        with open(r'assets\path.txt', 'a+') as f:
            if path:
                if path[-1] != "\\":
                    path = path + '\\'
                f.truncate(0)
                f.write(path)
                break
            else:
                f.seek(0)
                path = f.read()
                f.close()
                if not path.strip():
                    callPath(path = r'C:\KHC\PPD\songs')
                else: break

    return path

    
        


def LvDl(chart_id, folder_path = callPath(), iskakasi = True, vquality = 1, v_url = None, folder_title = None):
    global session
    
    # Check if chart to be downloaded is already present in the folder path
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            file_path = os.path.join(folder_path, dirname, "limk.txt")
            
            try:
                # Check if limk.txt matches the chart_id
                with open(file_path, "r") as file:
                    alt_id = file.read().strip()
                    
                    if chart_id.strip() in alt_id:
                        
                        # If chart name starts with '[', delete it and redownload
                        if dirname[0] == '[':
                            while True:
                                try:
                                    # Close the file and delete the directory tree
                                    file.close()
                                    shutil.rmtree(os.path.join(folder_path, dirname))
                                    try:
                                        os.rmdir(os.path.join(folder_path, dirname))
                                    except:
                                        pass
                                    break
                                except PermissionError:
                                    # Prompt user to close file being accessed
                                    input("A file you're trying to access is in use, close it and press enter to continue...")
                            
                            # Inform user about the missing video and attempt to redownload
                            ppr("Missing video found, trying to redownload...")
                        else:
                            # If limk matches chart is already downloaded
                            ppr("Chart is already downloaded!")
                            file.close()
                            return '1'
            except FileNotFoundError:
                # No "limk.txt"
                pass

    
    if not (v_url or folder_title):
        ppr("Starting download! Scraping data from the site...")
        song_url = 'https://projectdxxx.me/score/index/id/' + chart_id
        v_url, folder_title = getLimkAndTitle(session, song_url)
    else:
        ppr(f"Starting download on {folder_title}...")
    # NICONICO IS BROKEN, REMOVE WHEN FIXED
    if 'nicovideo.jp/watch/' in v_url:
        ppr('Niconico download disabled right now, sorry! Skipping...')
        return '0' 
    # downloads the zip
    zip_url = 'https://projectdxxx.me/score-library/download/id/' + chart_id
    folder_title = san_win_name(folder_title)
    folder_title = zipDl(session, zip_url, folder_path, folder_title, iskakasi)

    # downloads the video, returns state of video
    try:
        xflag, folder_title = dlLinkHandler(v_url, folder_path, folder_title, vquality)
    except Exception as e:
        ppr(f"CRITICAL ERROR AT DOWNLOAD HANDLER: {e}")
        # deletes the faulty folder
        shutil.rmtree(os.path.join(folder_path, folder_title))
        return -1
    
    # writes the limk
    file_path = os.path.join(folder_path, folder_title, "limk.txt")
    
    with open(file_path, "w") as file:
        file.write(chart_id)
        file.close()


    ppr('Chart downloaded, proceeding!')
    return xflag
# =============================\================================================
# =============================\================================================
            
    
def getLimkAndTitle(session, url):
    # searches for for yt/nico download video link, should become obsolete
    r = session.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    limk = soup.label.next_sibling.next_sibling['value']
    title = soup.find("h3", class_='panel-title pull-left').get_text().strip()
    return limk, title

# ------------------------------------------------------- #

def zipDl(session, url, folder_path, folder_title, iskakasi):
    # downloads zip file from url and extracts it to folder path
    zip_response = session.get(url)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    open(os.path.join(folder_path, 'folder.zip'), 'wb').write(zip_response.content)
    
    with zipfile.ZipFile(os.path.join(folder_path, 'folder.zip'), 'r') as zip_ref:
        zip_ref.extractall(path=folder_path)
        alt_folder_title = zip_ref.namelist()[0].split("/",1)[0]
        zip_ref.close()
    os.remove(os.path.join(folder_path, 'folder.zip'))
    corrupted = "╖δα╡σ±┼ªéîàÄⁿ¬ëÅ╣âôÅù"
    if any(char in alt_folder_title for char in corrupted):
        if iskakasi:
            folder_title = san_win_name(translateAndCapitalize(folder_title))
            
    else:
        if iskakasi:
            folder_title = san_win_name(translateAndCapitalize(alt_folder_title))
    def altLoop(n, display = ''):
        if n != 0: display = n
        try:
            os.rename(os.path.join(folder_path, alt_folder_title), os.path.join(folder_path, folder_title + " " + str(display)))
            a = f"{folder_title} {str(display)}".strip()
            return a
        except Exception as e:
            # if limk.txt is in the folder
            if os.path.exists(os.path.join(folder_path, folder_title + " " + str(display), "limk.txt")):
                print(e)
                n += 1
                if n<9:
                    return altLoop(n)
                else:
                    a = f"{folder_title}".strip()
                    return a
            else:
                shutil.rmtree(os.path.join(folder_path, folder_title + " " + str(display)).strip())
                os.rename(os.path.join(folder_path, alt_folder_title).strip(), os.path.join(folder_path, folder_title + " " + str(display).strip()))
                a = f"{folder_title} {str(display)}".strip()
                return a
    a = altLoop(0, '')
    return a

        
def dlLinkHandler(v_url, folder_path, folder_title, vquality = 1):
        # now youtube magic, can return the cause other than "NO MOVIE"
    # if that doesn't work, the level gets marked as [NO MOVIE]
    if 'drive.google' in v_url:
        gdriveDl(v_url, folder_path, folder_title)
    elif 'nicovideo.jp/watch/' in v_url:
        # nicoDl(v_url, folder_path, folder_title)
        ppr('Niconico download disabled right now, sorry! Skipping...')
        flag = 'NICO - NO'
        xflag = '5'

    else:
        if 'youtu' not in v_url:
            ppr(f"UNSUPPORTED VIDEO TYPE: {v_url}")
            flag = 'NO'
            xflag = '2'
        else:
            flag = ytDl(v_url, folder_path, folder_title, vquality)
    if flag:
        if flag == "ERROR": 
            flag = 'UNAVAILABLE'
            xflag = '3'
        elif flag == "LOGIN_REQUIRED": 
            flag = 'PRIVATED'
            xflag = '4'
        try:
            os.rmdir(os.path.join(folder_path, f'[{flag} MOVIE] {folder_title}'))
        except: 
            # ppr(f"Folder {folder_title} not found, continuing...")
            pass
        os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[{flag} MOVIE] {folder_title}'))
        return xflag, f'[{flag} MOVIE] {folder_title}'
    return '1', folder_title

    


# def nicoDl(url, folder_path, folder_title):
#     # download for videos on niconico, takes longer than from yt
#     ppr('Zip downloaded, proceeding to niconico download... Warning! This might take a while.')
#     with NicoNicoVideo(url, log=True) as nico:
#         data = nico.get_info()
#         nico.download(os.path.join(folder_path, folder_title, data["video"]["title"] + "movie.mp4"))




def ytDl(url, folder_path, folder_title, vquality = 1):
    # download for videos on youtube, most videos use this
    ppr('Zip downloaded, proceeding to youtube download...')
    if 'youtu.be/' in url:
        url = 'https://www.youtube.com/watch?v=' + url.split("/")[-1]
    yt = YouTube(url)
    # open(r"D:\\KHC\\PPD\\songs\\debug.txt", "w").write(str(yt.streams))
    if yt.vid_info['playabilityStatus']['status'] == 'OK':
        quals = [1080, 720, 480, 360, 240, 144]
        bitrates = [160, 128, 70, 50, 48]
        # 1080p always needs audio merging, tries to find highest quality video with audio (usually 720p)
        for num in range(vquality, 6):
            videos = yt.streams.filter(mime_type= "video/mp4", res = f'{quals[num]}p')
            video_w_audio = videos.get_highest_resolution()
            video = videos.first()
            if video != None:
                if video_w_audio:
                    video_w_audio.download(os.path.join(folder_path, folder_title))
                    break
                video.download(os.path.join(folder_path, folder_title), 'video.mp4')

                if video.includes_audio_track == False:
                    ppr('Merging audio...')
                    audios = yt.streams.filter(mime_type= "audio/webm")
                    if not audios: audios = yt.streams.filter(mime_type= "audio/mp4")
                    # choose audio with highest bitrate
                    audio = audios.desc().first()
                    audio.download(os.path.join(folder_path, folder_title), 'audio.webm')
                    # merge audio and video
                    os.system(f'ffmpeg -i "{os.path.join(folder_path, folder_title, "audio.webm")}" -i "{os.path.join(folder_path, folder_title, "video.mp4")}" -c copy "{os.path.join(folder_path, folder_title, san_win_name(video.title, substitute='') + ".mp4")}" -hide_banner -loglevel error')
                    os.remove(os.path.join(folder_path, folder_title, "audio.webm"))
                    os.remove(os.path.join(folder_path, folder_title, "video.mp4"))
                break
            if video == None and num == 5:
                ppr('cos poszlo nie tak. ups')
                return 'NO'
    else:
        ppr(f"{yt.vid_info['playabilityStatus']['reason']}: {url}")
        return yt.vid_info['playabilityStatus']['status']
    return None
                    
def gdriveDl(v_url, folder_path, folder_title):
    ppr('Zip downloaded, proceeding to google drive download... Warning! This might take a while.')
    dest = os.path.join(folder_path, folder_title, "movie.mp4")
    gdown.download(v_url, dest, quiet=True, fuzzy=True)
    

# ------------------------------------------------------- #

def translateAndCapitalize(jp_name):

    def to_romaji(jp_name):
        kks = pykakasi.kakasi()
        translated_name = ""
        translated_name_list = kks.convert(jp_name)
        for i in range(len(translated_name_list)):
            translated_name += translated_name_list[i]['hepburn'].capitalize() + " "
        return translated_name.strip()
        
    
    japanese_pattern = re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF\uFF66-\uFF9F]+')
    japanese_substrings = japanese_pattern.findall(jp_name)

    # Translate each Japanese substring using the provided translation function
    translations = {japanese: to_romaji(japanese) for japanese in japanese_substrings}

    # Replace each Japanese substring in the original text with its translation
    translated_text = jp_name
    for original, translated in translations.items():
        translated_text = translated_text.replace(original, translated)
    
    return translated_text.strip()



def checkForCS(text, author = ''):
    # read the keywords from the external file

    with open(r'assets\keywords.txt', 'r', encoding='utf-8') as f:

        kws = []
        aukws = []
        for line in f:
            if '#' in line:
                # Add all lines after '#' to list2
                for line2 in f:
                    if not line2.startswith('#') and line2.strip():
                        aukws.append('^' + line2.strip() + '$')
                break
            else:
                if line.strip():
                    kws.append(line.strip())
        for kw in kws:
            if re.search(kw, text, re.IGNORECASE):
                CSInput = True
                break
            else:
                CSInput = False
        if CSInput == False:
            for aukw in aukws:
                if re.match(aukw, author, re.IGNORECASE):
                    CSInput = True
                    break
                else:
                    CSInput = False
    
    return CSInput


def extractFloat(string):
  # Use a regular expression to search for a float
  match = re.search(r'[-+]?\d*\.\d+|\d+', string)
  if match:
    # If a float is found, return it as a float
    return float(match.group())
  else:
    # If no float is found, return None
    return None

def refreshIdDatabase(path = callPath(), return_all = False):
    # gives the list of level IDs
    IDS = set()
    pcheck = [i for i in path.split("\\") if i]
    if 'songs' in pcheck and not pcheck[-1] in 'songs':
        path = path[: path.index('songs\\') + 6]
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            if not name == "sound" in name:
                try:
                    open(os.path.join(root,name,'data.ini'), 'r')
                    try:
                        with open(os.path.join(root,name,'limk.txt'), 'r') as limk:
                            limk = limk.read()
                            if '/' in limk:
                                limk = limk.split('/')[-1]
                            if return_all == False:
                                if '[NO MOVIE]' in name: limk = '2x' + limk
                                elif '[UNAVAILABLE MOVIE]' in name: limk = '3x' + limk
                                elif '[PRIVATED MOVIE]' in name: limk = '4x' + limk
                                else: 
                                    limk = '1x' + limk
                            
                            if limk == '':
                                ppr(f"Empty limk found in {name}, continuing...")
                                break
                            
                            IDS.add(limk)
                            
                    except FileNotFoundError:
                        # ppr(f'Limk missing in {name}, continuing...')
                        continue
                    except Exception as e: ppr(e)
                except FileNotFoundError:
                    continue
    
    IDS = list(dict.fromkeys(IDS))
    return IDS

def readJson(fname, type):
    try:
        with open(fname, 'r') as f:
            try:
                obj = json.load(f)
            except:
                obj = type()
    except FileNotFoundError:
        open(fname, 'w')
        obj = type()
    return obj
    

"""
to do:

- add config
- add niconico choice if skip or download no video config
- shut up and feel my vibes (target score downloader) broken? no limk generates

for later:

- if no movie, delete only the prefix once the level has downloaded
- exception for no zip
- in case of conflict, read data.ini to determine author (? is this needed?)
"""

