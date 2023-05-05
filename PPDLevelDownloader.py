import concurrent.futures, requests, time, re, os
from bs4 import BeautifulSoup
import dllPPD as dll




def get_and_parse(session, page, kw, mode):
    # get the latest gossip from the search results page by sending a GET request
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
        
        
        
        # keep downloading and parsing pages until we reach a page with less than 10 results or we've reached our daily soup quota (10 pages)
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
                        # print(levelslist)
                        for lvcompare in levelslist:
                            licompare.append(lvcompare.find('a').get('href').split("/")[-1])
                        if id in licompare:
                            deletedcount += len(levels[-(len(levels)):])
                            break
                        else:
                            levelslist.extend(levels)
                
                # if levels:
                #     deletedcount = 0
                #     for lcount, level in enumerate(levels):
                #         id = level.find('a').get('href').split("/")[-1]
                #         licompare = []
                #         for lvcompare in levelslist:
                #             licompare.append(lvcompare.find('a').get('href').split("/")[-1])
                #         if id in licompare:
                #             deletedcount += len(levels[-(len(levels)):])
                #             break
                #         else:
                #             levelslist.extend(levels)
            else:
                # add the soup to the levelslist
                levelslist.extend(levels)
            data_dl_page += 1
            print(f'\rPage {data_dl_page-1} slurped up!   ')
            # TEN PAMIETNY BREAK
            # break

            # if the length of the levelslist list did not increase by 10 or the length of the list has not changed,
            # it means there are no more pages to be downloaded (the soup pot is empty)
            # so we just break the loop and go home
            # print('NIE WOLMO PRINTOWAC')
            ####print(deletedcount)
            ####print(len(levelslist))
            ####print(levelslist_len)
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
    #global debug
    #debug = []
    #for item in levelslist:
    #    debug.append(item.prettify())
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
        

        
        
        # dlLink + ID + is the level downloaded (requires ID that's why it's here) + jp title + translated title stuff
        li.append(lv.find("input", class_="form-control hidden").get('value'))
        li.append(lv.find('a').get('href').split("/")[-1])
        li.append(lv.find('a').get('title'))
        li.append(dll.translateAndCapitalize(lv.find('a').get('title')))
        
        # author ID + jp author + author + CSInput stuff
        li.append(lv.select_one(":nth-child(2)").find('a').get('href').split("/")[-1])
        li.append([line for line in lv_text.split('\n') if line.strip()][2].strip())
        li.append(dll.translateAndCapitalize([line for line in lv_text.split('\n') if line.strip()][2].strip()))
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
                
            li.append(value)
        
        # scrape stars and description for our soup
        scrape_stars_n_desc(lv, li)
        
        # info if the level is already downloaded
        #print(li[1])
        
        # combining all the soup ingredients into a single serving
        parsedinfo.append({**dict(zip(keys, li))})
        
    return parsedinfo



def scrape_stars_n_desc(lv, li):
    # not finished yet
    desc_html = lv.find_all("div", class_='clearfix')[1]
    # print(desc_html)
    desc = desc_html.get_text()
    # print(desc)
    # print(desc_html)
    # print(desc_html)
    # read keywords from diff.txt file

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
        # read keywords from diff.txt file
        # search for keywords in description
        for i in range(len(kws)-2):
            li_len = len(li)
            for kwdiff in kws[i]:
                for kwmid in kws[-2]:
                    for kwstar in kws[-1]:
                        tempkw = (kwdiff+kwmid+kwstar).lower()
                        index = desc.lower().find(tempkw)
                        if index != -1:
                            li.append(dll.extractFloat(desc[index+len(tempkw):index+len(tempkw)+20]))
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
                for kwdiff in kws[i]:
                    for kwmid in kws[-2]:
                            tempkw = (kwdiff+kwmid).lower()
                            index = desc.lower().find(tempkw)
                            if index != -1:
                                li[-j-1] = dll.extractFloat(desc[index+len(tempkw):index+len(tempkw)+5])
        # REALLY LAST RESORT AND I MEAN THAT
        # search for sole extreme difficulty if it isn't labeled at all
        #if all(x == '' for x in li[-4:]):
        #    pass
        #    pattern = 
        p_counter = -9
        for x in li[-4:]:
            p_counter += 1
            if li[p_counter]: #and not x:
                # li[p_counter] = punkty
                if p_counter == -8:
                    info = [[1.0, 3.1], [1.5, 4.09], [2.0, 5.15], [2.5, 6.07], [3.0, 7.21], [3.5, 6.83], [4.0, 11.11], [4.5, 12.77], [5.0, 10.88]]
                elif p_counter == -7:
                    info = [[2.0, 6.91], [2.5, 10.82], [3.0, 8.77], [3.5, 9.12], [4.0, 11.22], [4.5, 11.77], [5.0, 15.15], [5.5, 15.83], [6.0, 18.53], [6.5, 16.16], [7.0, 19.52], [7.5, 24.33], [8.0, 27.4]]
                elif p_counter == -6:
                    info = [[4.0, 10.59],[4.5, 12.49],[5.0, 15.48],[5.5, 17.09],[6.0, 18.53],[6.5, 22.23],[7.0, 23.5],[7.5, 25.88],[8.0, 27.59],[8.5, 29.82],[9.0, 32.3],[9.5, 38.61]]
                else:
                    pass
                chosen = 0
                for i in range(len(info)):
                    pass
                    #if info[i][1] - 
    #li.append(desc)
    li.append(desc_html.prettify(formatter="html"))

    


# run the soup kitchen
# handle(input('Search for score: '))
#handle('', 'all', 1)
#handle('bibio4545', 'author', 1)
#handle('rjri', 'author', '1')
#handle('I♡')
# handle('machinegun')

# ZMIENIĆ PRZED DANIEM DLA MICHAŁA
# li.append(desc) => li.append(desc_html)
"""
todo:
    - finish star aproximation
    
    
- stars aproximation if no scraping
- downloading data and loading from that (json files)
- checking if levels are already there

not mine: YES ITS MINEEE 
    O W N
- graphic interface

"""
