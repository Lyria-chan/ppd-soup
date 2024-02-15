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

# Set up the pykakasi converter
kks = pykakasi.Kakasi()

def san_win_name(filename):
    invalid_chars = r'[\\/:\*\?"<>|]'
    sanitized_filename = re.sub(invalid_chars, '_', filename)
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
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            file_path = os.path.join(folder_path, dirname, "limk.txt")
            try:
                with open(file_path, "r") as file:
                    alt_id = file.read().strip()
                    if chart_id.strip() in alt_id:
                        
                        if dirname[0] == '[':
                            while True:
                                try:
                                    file.close()
                                    shutil.rmtree(os.path.join(folder_path, dirname))
                                    try:
                                        os.rmdir(os.path.join(folder_path, dirname))
                                    except:
                                        pass
                                    break
                                except PermissionError:
                                    input("A file you're trying to access is in use, close it and press enter to continue...")
                            ppr("Missing video found, trying to redownload...")
                        else:
                            ppr("Chart is already downloaded!")
                            file.close()
                            return '1'
            except FileNotFoundError:
                pass

    
    if not (v_url or folder_title):
        ppr("Starting download! Scraping data from the site...")
        song_url = 'https://projectdxxx.me/score/index/id/' + chart_id
        v_url, folder_title = getLimkAndTitle(session, song_url)
    else:
        ppr(f"Starting download on {folder_title}...")
    # downloads the zip
    zip_url = 'https://projectdxxx.me/score-library/download/id/' + chart_id
    folder_title = san_win_name(folder_title)
    folder_title = zipDl(session, zip_url, folder_path, folder_title, iskakasi)

    # downloads the video, returns state of video
    try:
        xflag = dlLinkHandler(v_url, folder_path, folder_title, vquality)
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
            print(e)
            n += 1
            if n<9:
                return altLoop(n)
            else:
                a = f"{folder_title}".strip()
                return a
    a = altLoop(0, '')
    return a

        
def dlLinkHandler(v_url, folder_path, folder_title, vquality = 1):
        # now youtube magic, can return the cause other than "NO MOVIE"
    # if that doesn't work, the level gets marked as [NO MOVIE]
    if 'youtu' in v_url:
            flag = ytDl(v_url, folder_path, folder_title, vquality)
            if flag:
                xflag = '3'
                if flag == "ERROR": flag = 'UNAVAILABLE'
                elif flag == "LOGIN_REQUIRED": 
                    flag = 'PRIVATED'
                    xflag = '4'
                try:
                    os.rmdir(os.path.join(folder_path, f'[{flag} MOVIE] {folder_title}'))
                except: 
                    pass
                os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[{flag} MOVIE] {folder_title}'))
                return xflag
    
    elif 'drive.google' in v_url:
        gdriveDl(v_url, folder_path, folder_title)
    elif 'nicovideo.jp/watch/' in v_url:
        nicoDl(v_url, folder_path, folder_title)
    else:
        ppr(f"UNSUPPORTED VIDEO TYPE: {v_url}")
        os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[NO MOVIE] {folder_title}'))
        return '2'
    return '1'


def nicoDl(url, folder_path, folder_title):
    # download for videos on niconico, takes longer than from yt
    ppr('Zip downloaded, proceeding to niconico download... Warning! This might take a while.')
    with NicoNicoVideo(url, log=True) as nico:
        data = nico.get_info()
        nico.download(os.path.join(folder_path, folder_title, data["video"]["title"] + "movie.mp4"))
    

def ytDl(url, folder_path, folder_title, vquality = 1):
    # download for videos on youtube, most videos use this
    ppr('Zip downloaded, proceeding to youtube download...')
    if 'youtu.be/' in url:
        url = 'https://www.youtube.com/watch?v=' + url.split("/")[-1]
    yt = YouTube(url)
    # open(r"D:\\KHC\\PPD\\songs\\debug.txt", "w").write(yt.embed_htm).close()
    if yt.vid_info['playabilityStatus']['status'] == 'OK':
        quals = [1080, 720, 480, 360, 240, 144]
        for num in range(vquality, 6):
            return
            video = yt.streams.filter(mime_type= "video/mp4", res = f'{quals[num]}p').first()
            if video != None:
                video.download(os.path.join(folder_path, folder_title))
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
    name_temp = kks.convert(jp_name)
    name = ""
    for item in name_temp:
        try:
            name += str("{} ".format(item['hepburn'].capitalize()))
        except:
            name = jp_name
    name = name.replace('　',' ')
    while '  ' in name:
        name = name.replace('  ',' ')
    name = name.replace('( ','(')
    name = name.replace(' )',')')
    name = name.replace(' ℃', '℃')
    name = name.strip()
    name = list(name)
    i = 1
    while i <= len(name):
        if name[-i].lower() == jp_name[-i].lower():
            name[-i] = jp_name[-i]
        else:
            break
        i += 1
        
    i = 0
    while i < len(name):
        if name[i].lower() == jp_name[i].lower():
            name[i] = jp_name[i]
        else:
            break
        i += 1
    
    return "".join(name)

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
    

#LvDl(chart_id = 'd4630fb51d91609dcd4af8100bf88bc8', vquality = 1)


#ytDl('https://www.youtube.com/watch?v=eSW2LVbPThw', r'C:\KHC\PPD\songs\testing', 'TEST', 1)

#with requests.Session() as session:
#     nicoDl(session, 'https://www.nicovideo.jp/watch/sm12107146', r'C:\KHC\PPD\songs\testing', 'TEST')

#test = refreshIdDatabase(r'C:\KHC\PPD\songs')

#ppr(refreshIdDatabase())

"""
to do:

    FINISH WITH NO JAVASCRIPT ENABLED (PPD tower defense for testing)
exception for no zip
in case of conflict, read data.ini to determine author

for later:

- if no movie, delete only the prefix once the level has downloaded
"""

