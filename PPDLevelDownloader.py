import concurrent.futures, requests, time, re
from bs4 import BeautifulSoup
import dllPPD as dll

dl_death_flag = False
error_count = 0
def set_dl_death_flag(state):
    global dl_death_flag
    dl_death_flag = state

def get_and_parse(session, page, kw, mode):
    # get the latest gossip from the search results page by sending a GET request
    # 
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

def handle(kw, mode = 'def', maxpages = 0):
    if mode == 'all': kw = ''
    if kw == '': mode = 'all'
        
    # start a session and get ready to slurp up some soup
    with requests.Session() as session:
        data_dl_page = 1
        levelslist = []
        if kw == '':
            levelslist = dll.readJson(r'assets\all.json', list)
        
        
        
        # keep downloading and parsing pages until we reach a page with less than 10 results or we've reached our daily soup quota
        start_time = time.perf_counter()
        while True:
            # download and parse the current page
            print(f"Slurping up page {data_dl_page}...", end='')
            levelslist_len = len(levelslist)

            # submit the task to the soup chef (thread pool executor) and get a Future object
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(get_and_parse, session, data_dl_page, kw, mode)

            # wait for the soup to be ready and get the result
            levels = future.result()
            
            # there are twelve entries in the site when you use kw='', so we remove the last two unnecessary ones
            deletedcount = 0
            if kw == '':
                del levels[-1]
                del levels[-1]
                
                
                if levels:
                    for lcount, level in enumerate(levels):
                        id = level.find('a').get('href').split("/")[-1]
                        licompare = []
                        for lvcompare in levelslist:
                            licompare.append(lvcompare.find('a').get('href').split("/")[-1])
                        if id in licompare:
                            deletedcount += len(levels[-(len(levels)):])
                            break
                        else:
                            levelslist.extend(levels)
                

            else:
                # add the soup to the levelslist
                levelslist.extend(levels)
            data_dl_page += 1
            print(f'\rPage {data_dl_page-1} slurped up!   ')
            # TEN PAMIETNY BREAK
            # break

            # if the length of the levelslist list did not increase by 10 (the whole page) or the length of the list has not changed,
            # it means there are no more pages to be downloaded (the soup pot is empty)
            # so we just break the loop and go home
            # print('NIE WOLMO PRINTOWAC')

            if (len(levelslist) + deletedcount) %10 != 0 or levelslist_len == len(levelslist) + deletedcount:
                break
            if data_dl_page-1 == maxpages:
                break
            # if we have slurped up 20 pages and there are still more pages to be downloaded, ask the user if they want to continue
            if data_dl_page == 41 and False:
                choice = input("Warning: There are more than 40 pages of soup. Would you like to keep slurping? [Y/n] ")
                if choice == "n":
                    break
            
            
            
        elapsed_time = time.perf_counter() - start_time
        print(f"Elapsed time: {elapsed_time:0.2f} seconds")

    parsedinfo = save_to_array(levelslist)
    return parsedinfo
    

    


def save_to_array(ll):
    global parsedinfo
    parsedinfo = []
    for lv in ll:
        keys = ["dlLink", "id", "jpTitle", "title", "authorID", "jpAuthor", "author", "csinput", "date", "downloads", "bpm", "rating", "voted", "duration", "pEasy", "pNormal", "pHard", "pExtreme", "sEasy", "sNormal", "sHard", "sExtreme", "desc"]
        global li
        li = []
        lv_text = lv.get_text()
        

        
        
        # dlLink + ID + is the level downloaded (requires ID that's why it's here) // NOT TRUE + jp title + translated title stuff
        li.append(lv.find("input", class_="form-control hidden").get('value'))
        li.append(lv.find('a').get('href').split("/")[-1])
        li.append(lv.find('a').get('title'))
        li.append(dll.translateAndCapitalize(li[-1]))
        
        # author ID + jp author + author + CSInput stuff
        li.append(lv.select_one(":nth-child(2)").find('a').get('href').split("/")[-1])
        li.append([line for line in lv_text.split('\n') if line.strip()][2].strip())
        li.append(dll.translateAndCapitalize(li[-1]))
        li.append(dll.checkForCS(lv_text, li[4]))
        
        
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
        
        # info if the level is already downloaded
        #print(li[1])
        
        # combining all the soup ingredients into a single serving
        parsedinfo.append({**dict(zip(keys, li))})
        
    return parsedinfo



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
            if li[14+i] != '':
                for kwdiff in kws[i]:
                    if flag:
                        for kwmid in kws[-2]:
                                if flag:
                                    for kwstar in kws[-1]:
                                        if flag:
                                            tempkw = (kwdiff+kwmid+kwstar).lower()
                                            index = desc.lower().find(tempkw)
                                            if index != -1:
                                                toappend = dll.extractFloat(desc[index+len(tempkw):index+len(tempkw)+20])
                                                if toappend:
                                                    li.append(toappend)
                                                flag = False
                                                #print(f'{li[-1]} found by: {tempkw}')
                                            
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
                if li[14+i] != '':
                    for kwdiff in kws[i]:
                        for kwmid in kws[-2]:
                                tempkw = (kwdiff+kwmid).lower()
                                index = desc.lower().find(tempkw)
                                if index != -1:
                                    li[-j-1] = dll.extractFloat(desc[index+len(tempkw):index+len(tempkw)+5])
        # lumi2 is the bane of my existence when it comes to marking hard levels help me
        if li[-2] == '':
            if li[4] == 'lumi2':
                index = desc.lower().find('h☆')
                if index != -1:
                    li[20] = dll.extractFloat(desc[index+2:index+7])
    
        # welcome to abuse of the p counter!!!
        litest = ['', '', '', '']
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
                chosen = 0
                for i in range(len(info)):
                    if abs(info[i][1] - float(li[p_counter])) < abs(float(li[p_counter]) - float(info[chosen][1])):
                        chosen = i
                        li[p_counter + 4] = info[i][0] + 1000

        p_counter = 0
        for num in range(1, 8, 2):
            if li[-num] == li[-num-1]:
                p_counter += 1
        if p_counter == 4:
            for i in range(-9, -13, -1):
                if isinstance(li[i], (float, int)): 
                    p_counter -= 1
            if p_counter == 0:
                for num in range(4):
                    li.pop(-num-1)
                    
        try:
            if li[22] == None:
                li.pop(22)
        except:
            pass
        
        if len(li) > 22:
            if not ((li[22] >= 7.0 and li[22] == li[21] and li[19] == '' and li[18] == '') or (li[22] <= 3.5 and li[22] == li[18] and li[20] != '' and li[19] != '' and li[18] != '')): 
                global error_count
                error_count += 1
                print(f'ERROR WITH DIFFICULTIES AT ID {li[1]}, NAME {li[3]}')
                print(f'Last known diffs: {li[18]}, {li[19]}, {li[20]}, {li[21]}, cause: {li[22]}')
                print("------------------------------------------------------------------------------------")
            li[22] = desc_html.prettify(formatter="html")
        else:
            li.append(desc_html.prettify(formatter="html"))
    


# run the soup kitchen
# handle(input('Search for score: '))

#handle('lumi2', 'author')



"""
todo:
    
- downloading data and loading from that (json/sqlite files?)
- checking if levels are already there

not mine: YES ITS MINEEE 
    O W N
- graphic interface

"""
