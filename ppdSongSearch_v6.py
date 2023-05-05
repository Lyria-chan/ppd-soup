import requests, pykakasi, json
from time import time
import dllPPD as dll


# --------- # EDIT VALUES HERE # --------- #
dldirectory = r'C:\KHC\PPD\songs\TARGET SCORES\test'
    # the localization where the songs will be downloaded. write it inside of the  r' '. DO NOT DELETE THE R, THE PROGRAM WILL NOT WORK
videoquality = 1
    # highest video quality the program will attempt to download from youtube. 0 is 1080p, 1 is 720p, 5 is 144p etc.

# ---------------------------------------- #


# here is the rest of the code. good luck analyzing it if you want to
kks = pykakasi.kakasi()

def loadUrl(url, session):
    for attempts in range(10):
        try:
            html=requests.get(url)
            if html.status_code==200:
                html = html.text
                break
            else:
                print("Error in loading web page")
        except ConnectionError:
            html = ""
            continue
    return html

def loadList():
    with requests.Session() as session:
        html = loadUrl('https://projectdxxx.me/api/active-score', session)
    html = html.replace("</Root>","<Root>")
    html = html.split("<Root>",2)[1]
    html = html.replace("<Entry ","")
    html = html.replace("ID=","")
    html = html.replace(" Title=",",")
    html = html.replace(" Temp=\"2\"","")
    html_list = html.split("/>")
    html_list = html_list[:-1]

    song_list = []
    for song in range(len(html_list)):
        html_list[song] = html_list[song].split(",",1)
        song_list.append({})
        for data in range(len(html_list[song])):
            html_list[song][data] = html_list[song][data][1:-1]
        song_list[song]['url'] = "https://projectdxxx.me/score/index/id/" + html_list[song][0]
        song_list[song]['name'] = html_list[song][1]
    
    for song in song_list:
        name_temp = kks.convert(song['name'])
        name = ""
        for item in name_temp:
            try:
                name += str("{} ".format(item['hepburn'].capitalize()))
            except:
                name = song['name']
        if name[-1] == ' ':
            name = name[:-1]
        name = name.replace('　',' ')
        if '  ' in name:
            while '  ' in name:
                name = name.replace('  ',' ')
        name = name.replace('( ','(')
        name = name.replace(' )',')')
        song['name'] = name
    
    return song_list

def timeString(time):
    if time >= 100:
        time = str(round(time / 60)) + " minutes"
    elif time >= 60:
        time = "about 1 minute"
    elif time >= 2:
        time = str(round(time)) + " seconds"
    else:
        time = "1 second"
    return time

def updateSongs(song_list_new):
    with open("assets/target_scores.json","r") as song_list_old:
        song_list_old = json.loads(song_list_old.read())
    
    song_list_updated = []
    for song_new in song_list_new:
        if not any(song_new['url'] == song_old['url'] for song_old in song_list_old):
            song_list_updated.append(song_new)
    return song_list_updated


song_list = loadList()

with open("assets/target_scores.json","w") as song_list_old:
    json.dump(song_list,song_list_old)

csinput_keyword_list = [
    {'raw':'csinput','display':'CSInput'},
    {'raw':'csimput','display':'CSImput'},
    {'raw':'cs input','display':'CS Input'},
    {'raw':'cs imput','display':'CS Imput'},
    {'raw':'cs included','display':'CS Included'},
    {'raw':'perfectinput','display':'PerfectInput'},
    {'raw':'perfect input','display':'Perfect Input'},
    {'raw':'投稿者:\n      <a href=\"/user/index/id/palmtree_freak','display':'Palmtree_Freak'},
    {'raw':'投稿者:\n      <a href=\"/user/index/id/bluestar','display':'Blue Star'},
    {'raw':'投稿者:\n      <a href=\"/user/index/id/bryntae','display':'bryntae'},
    {'raw':'投稿者:\n      <a href=\"/user/index/id/boku_boku_','display':'Boku_Boku_'},
    {'raw':'投稿者:\n      <a href=\"/user/index/id/genmo','display':'Genmo'},
    {'raw':'投稿者:\n      <a href=\"/user/index/id/HpGucciPencils','display':'Kyle'},]
"""
    Charters covered by the standard csinput arguments:
        - Siteswap
        - EgguTasteGood
    
    
    
"""
print("Choose search mode:" +
      "\n 1) CSInput search (default, if not sure choose this)" +
      "\n 2) additional author ID search" +
      "\n 3) author ID search without CSInput" +
      "\n 4) custom website content search")
mode = int(input())

#newOnly = input("Do you want to search from [F]ull list of songs or only from [n]ew songs?\n")
#if newOnly == "n":
#    newOnly = True
#else:
#    newOnly = False
newOnly = False

checked_count = 0
found_count = 0
keyword_not_list = []
keyword_list = []

if mode == 1:
    keyword_list = csinput_keyword_list
elif 2 <= mode <= 4:
    if mode == 2 or mode == 3:
        key = "author ID"
        key_start = "投稿者:\n      <a href=\"/user/index/id/"
        if mode == 3:
            keyword_not_list = csinput_keyword_list
    else:
        key = "keyword"
        key_start = ""
    while True:
        keyword = {}
        keyword['display'] = input(f"Input {key}: ")
        keyword['raw'] = key_start + keyword['display'].lower()
        keyword_list.append(keyword)
        choice = input(f"Do you want to add more {key}s? [Y/n] ")
        if choice == "n":
            break
else:
    mode /= 0
    
if newOnly:
    song_list = updateSongs(song_list)

time_start = round(time(),2)

with open('assets\log.txt','a') as log:
    log.write("ppdSongSearch log file")
    if mode == 1:
        log.write("\nSearching for CSInput")
    else:
        log.write("\nSearching for following author IDs:\n")
        log_keywords = ""
        for keyword in keyword_list:
            log_keywords += f"{keyword['display']}, "
        log_keywords = log_keywords[:-2]
        log.write(log_keywords)
    log.write("\n\nSongs found:\n")
    
with requests.Session() as session:
    for song in song_list:
        song_id = song['url'].split('/')[-1]
        html = str(loadUrl(song['url'], session))
        
        # for keyword, keyword_not in zip(keyword_list, keyword_not_list):
        #     print(keyword_list)
        #     if keyword['raw'] in html.lower() and not keyword_not['raw'] in html.lower():
        #         print(f"\rKeyword \"{keyword['display']}\" found in \"{song['name']}\", rank {checked_count+1}" + 20 * " " +
        #               f"\nurl: {song['url']}" +
        #               "\n- - - - -")
        #         found_count += 1
        #         with open('log.txt','a') as log:
        #             log.write(f"{song['name']}, rank {checked_count+1}, {song['url']}\n")
        
        for keyword in keyword_list:
            if keyword_not_list:
                for keyword_not in keyword_not_list:
                    if keyword['raw'] in html.lower() and not keyword_not['raw'] in html.lower():
                        print(f"\rKeyword \"{keyword['display']}\" found in \"{song['name']}\", rank {checked_count+1}" + 20 * " " +
                              f"\nurl: {song['url']}" +
                              "\n- - - - -")
                        found_count += 1
                        with open('assets\log.txt','a') as log:
                            log.write(f"{song['name']}, rank {checked_count+1}, {song['url']}\n")
                        dll.LvDl(session, song_id, dldirectory, True, videoquality)
            else:
                if keyword['raw'] in html.lower():
                    print(f"\rKeyword \"{keyword['display']}\" found in \"{song['name']}\", rank {checked_count+1}" + 20 * " " +
                          f"\nurl: {song['url']}" +
                          "\n- - - - -")
                    found_count += 1
                    with open('assets\log.txt','a') as log:
                        log.write(f"{song['name']}, rank {checked_count+1}, {song['url']}\n")
                    dll.LvDl(session, song_id, dldirectory, True, videoquality)
        checked_count += 1
        
        time_remaining = (round(time() - time_start,2) / checked_count) * (len(song_list) - checked_count)
        time_remaining = timeString(time_remaining)
            
        progress = round(checked_count * 100 / len(song_list))
        
        print(f"\r{checked_count} checked, {found_count} found, {progress}% completed, {time_remaining} remaining" + 10 * " ",end='')
    
    total_time = round(time() - time_start)
    total_hr = str(total_time // 3600).zfill(2)
    total_min = str((total_time % 3600) // 60).zfill(2)
    total_sec = str(total_time % 60).zfill(2)
    total_time = f"{total_hr}:{total_min}:{total_sec}"
    
    print(f"\rSearch completed in {total_time}. {checked_count} songs checked, {found_count} found." + 20 * " ")