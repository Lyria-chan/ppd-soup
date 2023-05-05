import requests, zipfile, os, re, pykakasi, json #, sqlite3
from niconico_dl import NicoNicoVideo
from pytube import YouTube
from bs4 import BeautifulSoup



# Set up the pykakasi converter
kks = pykakasi.Kakasi()


def slowLvDl(session, song_id, folder_path, iskakasi = 'True'):
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            file_path = os.path.join(folder_path, dirname, "limk.txt")
            try:
                with open(file_path, "r") as file:
                    alt_id = file.read().strip()
                    if song_id.strip() in alt_id:
                        print('Chart is already downloaded!')
                        file.close()
                        return
            except FileNotFoundError:
                pass
    song_url = 'https://projectdxxx.me/score/index/id/' + song_id
    zip_url = 'https://projectdxxx.me/score-library/download/id/' + song_id
    v_url, folder_title = getLimkAndTitle(session, song_url)
    folder_title = zipDl(session, zip_url, folder_path, folder_title, iskakasi)
    file_path = os.path.join(folder_path, folder_title, "limk.txt")
    with open(file_path, "w") as file:
        file.write(song_id)
        file.close()
    pattern = 'www.nicovideo.jp/watch/'
    try:
        yt_error_check = ytDl(session, v_url, folder_path, folder_title)
        if yt_error_check == "VideoPrivate":
            print("VIDEO IS PRIVATE")
            os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[PRIVATED MOVIE] {folder_title}'))
    except:
        if re.match(pattern, v_url):
            nicoDl(session, v_url, folder_path, folder_title)
        else:
            print("MISSING VIDEO")
            os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[NO MOVIE] {folder_title}'))
            return
    print('Song downloaded, proceeding...                                     ', end='')
            
# =============================================================================
def fastLvDl(session, song_id, folder_path, iskakasi = 'True', vquality = 1):
    for root, dirs, files in os.walk(folder_path):
        for dirname in dirs:
            file_path = os.path.join(folder_path, dirname, "limk.txt")
            try:
                with open(file_path, "r") as file:
                    alt_id = file.read().strip()
                    if song_id.strip() in alt_id:
                        print('Chart is already downloaded!')
                        file.close()
                        return
            except FileNotFoundError:
                pass
    song_url = 'https://projectdxxx.me/score/index/id/' + song_id
    zip_url = 'https://projectdxxx.me/score-library/download/id/' + song_id
    v_url, folder_title = getLimkAndTitle(session, song_url)
    folder_title = zipDl(session, zip_url, folder_path, folder_title, iskakasi)
    file_path = os.path.join(folder_path, folder_title, "limk.txt")
    with open(file_path, "w") as file:
        file.write(song_id)
        file.close()
    try:
        yt_error_check = ytDl(session, v_url, folder_path, folder_title)
        if yt_error_check == "VideoPrivate":
            print("VIDEO IS PRIVATE")
            os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[PRIVATED MOVIE] {folder_title}'))
    except:
        if 'nicovideo.jp/watch/' in v_url:
            nicoDl(session, v_url, folder_path, folder_title)
        else:
            print("MISSING VIDEO")
            os.rename(os.path.join(folder_path, folder_title), os.path.join(folder_path, f'[NO MOVIE] {folder_title}'))
            return
    print('Chart downloaded, proceeding...                                     ', end='')
# =============================\================================================
            
    
def getLimkAndTitle(session, url):
    # searches for for yt/nico download video link, should become obsolete
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    limk = soup.label.next_sibling.next_sibling['value']
    title = soup.find("h3", class_='panel-title pull-left').get_text().strip()
    return limk, title

# ------------------------------------------------------- #

def zipDl(session, url, folder_path, folder_title, iskakasi):
    # downloads zip file from url and extracts it to folder path
    zip_response = requests.get(url)
    open(os.path.join(folder_path, 'folder.zip'), 'wb').write(zip_response.content)
    with zipfile.ZipFile(os.path.join(folder_path, 'folder.zip'), 'r') as zip_ref:
        zip_ref.extractall(path=folder_path)
        alt_folder_title = zip_ref.namelist()[0].split("/",1)[0]
        zip_ref.close()
    os.remove(os.path.join(folder_path, 'folder.zip'))
    
    corrupted = "╖δα╡σ±┼ªéîàÄⁿ¬ëÅ╣"
    if any(char in alt_folder_title for char in corrupted):
        if iskakasi:
            folder_title = translateAndCapitalize(folder_title)
    else:
        if iskakasi:
            folder_title = translateAndCapitalize(alt_folder_title)
            
    os.rename(os.path.join(folder_path, alt_folder_title), os.path.join(folder_path, folder_title))
    return folder_title
        

def nicoDl(session, url, folder_path, folder_title):
    # download for videos on niconico, takes longer than from yt
    print('\rZip downloaded, proceeding to niconico download...',end='')
    with NicoNicoVideo(url, log=True) as nico:
        data = nico.get_info()
        nico.download(os.path.join(folder_path, folder_title, data["video"]["title"] + "movie.mp4"))

def ytDl(session, url, folder_path, folder_title, vquality = 1):
    # download for videos on youtube, most videos use this
    print('\rZip downloaded, proceeding to youtube download...',end='')
    if 'youtu.be/' in url:
        url = 'https://www.youtube.com/watch?v=' + url.split("/")[-1]
    yt = YouTube(url)
    if 'This video is private' in yt.embed_html:
        # perform any necessary actions here
        return "VideoPrivate"
    quals = [1080, 720, 480, 360, 240, 144]
    for num in range(vquality, 6):
        video = yt.streams.filter(mime_type= "video/mp4", res = f'{quals[num]}p').first()
        if video != None:
            video.download(os.path.join(folder_path, folder_title))
            break
        if video == None and num == 5:
            print('cos poszlo nie tak. ups')
                    


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
    #     keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    # for keyword in keywords:
    #     if re.search(keyword, text, re.IGNORECASE):
    #         CSInput = True
    #         break
    #     else:
    #         CSInput = False


def extractFloat(string):
  # Use a regular expression to search for a float
  match = re.search(r'[-+]?\d*\.\d+|\d+', string)
  if match:
    # If a float is found, return it as a float
    return float(match.group())
  else:
    # If no float is found, return None
    return None

def refreshIdDatabase(path, save = True):
    # gives the list of level IDs
    IDS = []
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            if not name == "sound" and not '[NO MOVIE]' in name:
                try:
                    open(os.path.join(root,name,'data.ini'), 'r')
                    try:
                        with open(os.path.join(root,name,'limk.txt'), 'r') as limk:
                            limk = limk.read()
                            if '/' in limk:
                                limk = limk.split('/')[-1]
                            if limk == '':
                                print(f"Empty limk found in {name}, continuing...")
                                break
                            IDS.append(limk)
                            
                    except FileNotFoundError:
                        print(f'Limk missing in {name}, continuing...')
                        continue
                    except Exception as e: print(e)
                except FileNotFoundError:
                    continue
    
    IDS = list(dict.fromkeys(IDS))
#    if save == True:
        
    
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
    
with requests.session() as session:
    slowLvDl(session, '2073d054d3fb0e8812dfd52c7cbbf048', r'C:\KHC\PPD\songs\testing', True)

#with requests.Session() as session:
#     ytDl(session, 'https://youtu.be/e0VtkZYtzrI', r'C:\KHC\PPD\songs\testing', 'TEST', 1)

#with requests.Session() as session:
#     nicoDl(session, 'https://www.nicovideo.jp/watch/sm12107146', r'C:\KHC\PPD\songs\testing', 'TEST')

#test = refreshIdDatabase(r'C:\KHC\PPD\songs')
"""
to do:
- default path for save (?)
- json save for the parsed data if keyword is ''
- fix yt dl for 'topic' videos (no mp4) 
"""

