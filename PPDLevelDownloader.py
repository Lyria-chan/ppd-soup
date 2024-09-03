import concurrent.futures, requests, time, re, sqlite3, urllib.parse, os
from bs4 import BeautifulSoup
import dllPPD as dll

keys = ["video", "id", "saved", "jpTitle", "title", "authorId", "jpAuthor", "author", "csinput", "date", "downloads", "bpm", "rating", "voted", "duration", "pEasy", "pNormal", "pHard", "pExtreme", "sEasy", "sNormal", "sHard", "sExtreme", "desc"]

def set_dl_death_flag(state):
    global dl_death_flag
    dl_death_flag = state


def get_and_parse(session, page, kw, mode):
    # get the latest gossip from the search results page by sending a GET request
    # 
    kw = urllib.parse.quote(kw, safe='')
    if mode == 'all':
        score_kw_url = f'https://projectdxxx.me/score-library/index/page/{page}'
    elif mode == 'author':
        score_kw_url = f'https://projectdxxx.me/user/scorelist/id/{kw}/page/{page}'
    else: 
        score_kw_url = f'https://projectdxxx.me/search/score/word/{kw}/page/{page}'
    response = session.get(score_kw_url)
    html = response.text

    # use BeautifulSoup to turn the HTML into a delicious soup and find all the juicy bits (div elements with class "panel panel-default")
    soup = BeautifulSoup(html, "lxml")
    levels = soup.find_all("div", class_="panel panel-default")

    return levels


def handle(kw = '', mode = 'def'):
    start_time = time.perf_counter()
    global parsedinfo
    global downloaded
    global dl_death_flag
    parsedinfo = []
    downloaded = 0
    dl_death_flag = False
    limitentries = ''
    if mode == 'start': 
        limitentries = 30
        mode = 'all'
    
    
    
    saved = dll.refreshIdDatabase(dll.callPath())
    
    
    
    db_local('update', saved)
    if kw == '': mode = 'all'
    if mode == 'all':
        parsedinfo = db_local('load', saved)
        kw = ''
    
    elapsed_time = time.perf_counter() - start_time
    dll.ppr(f"Elapsed time so far: {elapsed_time:0.2f} seconds")

    # start a session and get ready to slurp up some soup
    with requests.Session() as session:
        data_dl_page = 1
        
        
        
        # keep downloading and parsing pages until we reach a page with less than 10 results or we've reached our daily soup quota
        while not dl_death_flag:
            # download and parse the current page
            dll.ppr(f"Slurping up page {data_dl_page}...")

            # submit the task to the soup chef (thread pool executor) and get a Future object
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(get_and_parse, session, data_dl_page, kw, mode)

            # wait for the soup to be ready and get the result
            levels = future.result()
            
            # there are twelve entries in the site when you use kw='', so we remove the last two unnecessary ones
            if kw == '':
                del levels[-1:-3:-1]
                if data_dl_page == 1:
                    if '広告された譜面' in levels[-1].find('h3', class_='panel-title').get_text().strip(): del levels[-1]
                
            data_dl_page += 1
            dll.ppr(f'Page {data_dl_page-1} slurped up!')
            # TEN PAMIETNY BREAK
            # break
        
            # asynchronously call save_to_array using a separate thread pool executor
            # with concurrent.futures.ThreadPoolExecutor() as save_executor:
            #    save_future = save_executor.submit(save_to_array, levels, saved, mode)
            save_to_array(levels, saved, mode)
            
            # if there are less than 10 levels to add, there are no more pages to be downloaded (the soup pot is empty)
            if len(levels) != 10:
                break
            
        elapsed_time = time.perf_counter() - start_time
        dll.ppr(f"Total elapsed time: {elapsed_time:0.2f} seconds")
        # save_future.result()
    
    if mode == 'all':
        dll.ppr(f'{downloaded} new entries added, {len(parsedinfo)} in total.')
        if downloaded and not downloaded == len(parsedinfo):
            dll.ppr("WARNING: IF NEW ENTRIES DON'T SHOW UP REFRESH USING F5")
    
    
    if limitentries: return parsedinfo[:limitentries]
    else: return parsedinfo
    

def save_to_array(ll, saved = '', mode = 'def', maxpages = 0):
    global parsedinfo
    global dl_death_flag
    global keys
    global li
    for lv in ll:
        li = []
        lv_text = lv.get_text()
        

        # dlLink + ID + is the level downloaded (requires ID that's why it's here) // NOT TRUE + jp title + translated title stuff
        li.append(lv.find("input", class_="form-control hidden").get('value'))
        
        li.append(lv.find('a').get('href').split("/")[-1])
        flag = False
        for item in saved:
            if li[-1] in item.split('x')[-1]:
                flag = item.split('x')[0]
        if flag:
            li.append(flag)
        else: 
            li.append('0')
        li.append(lv.find('a').get('title'))
        li.append(dll.translateAndCapitalize(li[-1]))
        
        # author ID + jp author + author + CSInput stuff
        li.append(lv.select_one(":nth-child(2)").find('a').get('href').split("/")[-1])
        li.append([line for line in lv_text.split('\n') if line.strip()][2].strip())
        li.append(dll.translateAndCapitalize(li[-1]))
        li.append(dll.checkForCS(lv_text, li[5]))
        
        
        # time stuff (don't ask what happened there, all you need to know that it magically finds time and writes it to unix)
        li.append(int(time.mktime(time.strptime(re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", lv_text)[-1], "%Y-%m-%d %H:%M:%S"))))
        
        # difficulty + some other parameters stuff
        table = lv.find("table", class_="table table-striped")
        cells = table.find_all('td')
        i = -5
        while i <= 2:
            i += 1
            value = cells[i].text.strip()
            value = value.replace("pt", "")
            if i == -2:
                # first append is the rating, the 'value' is the amount of people that voted
                if value.split('(')[0] == '評価なし':
                    li.append('')
                    value = ''
                else:
                    li.append(value.split('(')[0])
                    value = value.strip(')').split('(')[1]
            try:
                li.append(float(value))
            except:
                li.append(value)
        
        # scrape stars and description for our soup
        scrape_stars_n_desc(lv, li)
        data = {**dict(zip(keys, li))}
        
        
        # combining all the soup ingredients into a single serving
        #data = 
        if mode == 'all':
            if db_local('save', data):
                parsedinfo.append(data)
            pass
        else: parsedinfo.append(data)
        if len(data) != 24: dl_death_flag = True

def scrape_stars_n_desc(lv, li):
    # scrape well the description duh
    desc_html = lv.find_all("div", class_='clearfix')[1]

    desc = desc_html.get_text()
    # read keywords from diff.txt file and categorize them
    with open(r"assets\diff.txt", "r", encoding='utf-8') as f:
        kws = [[]]
        i = 0
        for line in f:
            if line.strip():
                if line.startswith('#'):
                    i+= 1
                    kws.append([])
                if line.startswith('$'):
                    kws[i].append('')
                if not line.startswith('#') and not line.startswith('$'):
                    kws[i].append(line[:-1])
        # search for keywords in description, standard procedure
        for i in range(len(kws)-2):
            flag = True
            li_len = len(li)
            if li[15+i] != '':
                for kwdiff in kws[i]:
                    if flag:
                        for kwmid in kws[-2]:
                            if flag:
                                for kwstar in kws[-1]:
                                    if flag:
                                        tempkw = (kwdiff+kwmid+kwstar).lower()
                                        index = desc.lower().find(tempkw)
                                        if index != -1:      
                                            aindex = 0 # additional index
                                            while True:
                                                index = desc[aindex:].lower().find(tempkw)
                                                if index != -1:  
                                                    index += aindex
                                                    toappend = dll.extractFloat(desc[index+len(tempkw) : index+len(tempkw)])
                                                    if toappend:
                                                        li.append(toappend)
                                                        flag = False
                                                        break
                                                    elif toappend == None:
                                                        aindex = index + len(tempkw) 
                                                    else: 
                                                        break
                                                else:
                                                    break
                                            
            if li_len == len(li):
                li.append('')
        # search for extremes that are labeled "x Stars"
        if all(x == '' for x in li[-4:]):
            tempkw = (kwdiff+kwstar).lower()
            index = desc.lower().find("stars")
            if index != -1:
                li[-1] = dll.extractFloat(desc[index-5:index])
        
        # search for difficulties that don't have stars before the number, can be wrong
        if all(x == '' for x in li[-4:]):
            for i, j in zip(range(len(kws)-2), reversed(range(len(kws)-2))):
                flag = True
                if li[15+i] != '':
                    if flag:
                        for kwdiff in kws[i]:
                                if flag:
                                    for kwmid in kws[-2]:
                                        if flag:
                                            tempkw = (kwdiff+kwmid).lower()
                                            index = desc.lower().find(tempkw)
                                            if index != -1:      
                                                aindex = 0 # additional index
                                                while True:
                                                    index = desc[aindex:].lower().find(tempkw)
                                                    if index != -1:  
                                                        index += aindex
                                                        toappend = dll.extractFloat(desc[index+len(tempkw) : index+len(tempkw) + 10])
                                                        if toappend:
                                                            li[-j-1] = toappend
                                                            flag = False
                                                            break
                                                        elif toappend == None:
                                                            aindex = index + len(tempkw) 
                                                        else:
                                                            break
                                                    else:
                                                        break
        # lumi2 is the bane of my existence when it comes to marking hard levels help me
        if li[-2] == '':
            if li[5] == 'lumi2':
                index = desc.lower().find('h☆')
                if index != -1:
                    li[-2] = dll.extractFloat(desc[index+2:index+7])
        # check for misread stars
        for x in [-1, -2, -3, -4]:
            if type(li[x]) == (float or int) and li[x] > 100:
                li[x] = ''
        
        # welcome to abuse of the p counter!!!
        p_counter = -9
        for x in range(4, 0, -1):
            if li[-x] == None: 
                li[-x] = ''
            p_counter += 1
            if li[p_counter] and not li[-x]:
                # li[p_counter] = punkty
                if p_counter == -8:
                    info = [[1.0, 3.1], [1.5, 4.09], [2.0, 5.15], [2.5, 6.07], [3.0, 7.21], [3.5, 6.83], [4.0, 11.11], [4.5, 12.77], [5.0, 10.88], [5.5, 14.92], [6.0, 15.66], [6.5, 16.25], [7.0, 18.34], [7.5, 19.49], [8.0, 21.61], [8.5, 22.71], [9.0, 24.87], [9.5, 26.04], [10.0, 28.22]]
                elif p_counter == -7:
                    info = [[1.0, 4.82], [1.5, 5.87], [2.0, 6.91], [2.5, 10.82], [3.0, 8.77], [3.5, 9.12], [4.0, 11.22], [4.5, 11.77], [5.0, 15.15], [5.5, 15.83], [6.0, 18.53], [6.5, 16.16], [7.0, 19.52], [7.5, 24.33], [8.0, 27.4], [8.5, 28.95], [9.0, 31.48], [9.5, 32.72], [10.0, 33.68]]
                elif p_counter == -6:
                    info = [[1.0, 5.16], [1.5, 5.81], [2.0, 6.46], [2.5, 7.81], [3.0, 8.27], [3.5, 9.95], [4.0, 10.59],[4.5, 12.49],[5.0, 15.48],[5.5, 17.09],[6.0, 18.53],[6.5, 22.23],[7.0, 23.5],[7.5, 25.88],[8.0, 27.59],[8.5, 29.82],[9.0, 32.3],[9.5, 38.61], [10.0, 40]]
                else:
                    info = [[1.0, 5.61], [1.5, 6.35], [2.0, 7.02], [2.5, 7.77], [3.0, 8.48], [3.5, 9.45], [4.0, 10.29], [5.0, 14.76], [6.0, 14.33], [6.5, 15.37], [7.0, 18.89], [7.5, 20.83], [8.0, 24.83], [8.5, 28.77], [9.0, 31.38], [9.5, 35.01], [10.0, 41.08]]
                chosen = 1
                for i in range(len(info)):
                    if abs(info[i][1] - float(li[p_counter])) < abs(float(li[p_counter]) - float(info[chosen][1])):
                        chosen = i
                        li[p_counter + 4] = info[i][0] + 1000

        li.append(desc_html.prettify(formatter="html"))
    
def db_local(mode, data = ''):
    
    global downloaded, keys

    if mode == 'delete':
        try:
            os.remove(r'assets\local.db')
            
        except Exception as e:
            dll.ppr(e)
            dll.ppr(r"This file already doesn't exist, proceeding...")

        conn = sqlite3.connect(r'assets\local.db')
        c = conn.cursor()
        
        keys[1] = 'id PRIMARY KEY'
        c.execute(f'CREATE TABLE IF NOT EXISTS scores ({", ".join(keys)})')
        keys[1] = 'id'
        return
    
    conn = sqlite3.connect(r'assets\local.db')
    c = conn.cursor()
    
    if mode == 'load':
        keys[1] = 'id PRIMARY KEY'
        c.execute(f'CREATE TABLE IF NOT EXISTS scores ({", ".join(keys)})')
        keys[1] = 'id'
        conn.commit()
        c.execute('SELECT * FROM scores ORDER BY date DESC')
        rows = c.fetchall()
        column_names = [description[0] for description in c.description]
        levelslist = [
            {
                column_names[i]: (True if value == 1 else False) if column_names[i] == 'csinput' else value
                for i, value in enumerate(row)
            }
            for row in rows
        ]
        return(levelslist)
        
            
    elif mode == 'save':
        c.execute("SELECT COUNT(id) FROM scores")
        rows_len = c.fetchone()[0]
        values = ', '.join('?' * len(data))
        data_values = tuple(data.values())
        c.execute(f'INSERT OR IGNORE INTO scores VALUES ({values})', data_values)
        conn.commit()
        c.execute("SELECT COUNT(id) FROM scores")
        
        if rows_len == c.fetchone()[0]: 
            set_dl_death_flag(True)
            result = False
        else:
            downloaded += 1
            result = True
    
    elif mode == 'validate':
        c.execute("SELECT EXISTS(SELECT 1 FROM scores WHERE id = 'cf3a9cb7baecea6620af0b6b37a271d3')")
        if not c.fetchone()[0]:
            dll.ppr('WARNING: YOUR DATABASE MIGHT NOT BE COMPLETE. WIPE AND REDOWNLOAD IT AT CONFIGURATION')

    elif mode == 'update':
        try:
            c.execute("UPDATE scores SET saved = 0")
        except:
            db_local('load', data)
            db_local('update')
        update_data = [(entry.split('x')[0], entry.split('x')[1]) for entry in data]
        c.executemany("UPDATE scores SET saved = ? WHERE id = ?", update_data)
        conn.commit()
            
    
    conn.close()
    try:
        return result
    except:
        pass
    
    
# run the soup kitchen
# handle(input('Search for score: '))
#handle('紅蓮華 ver.萌愛')# , 'all')
#handle('')
#handle('psi')
"""
todo:


- deleting database doesn't work for some reason
- saved scores for some reason don't get immediately displayed? why

not mine: YES ITS MINEEE 
    O W N
- graphic interface
"""
