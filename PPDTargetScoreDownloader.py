import requests, pykakasi, json
from time import time
import extra_library as dll

dldirectory = dll.callPath()
if 'songs' in dldirectory:
    dldirectory = dldirectory[:dldirectory.index('songs') + 6]

# --------- # EDIT VALUES HERE # --------- #
dldirectory = fr'{dldirectory}TARGET SCORES'
    # the localization where the songs will be downloaded. write it inside of the  fr' '. DO NOT DELETE THE 'fr', THE PROGRAM WILL NOT WORK
videoquality = 1
    # highest video quality the program will attempt to download from youtube. 0 is 1080p, 1 is 720p, 5 is 144p etc.
startfrom = 0
    # start from this position in the song list, use if download was interrupted
# ---------------------------------------- #


# here is the rest of the code. good luck analyzing it if you want to

def addIDToTxt(id, name):
    # open file specified in path /assets/{name}.txt
    with open(f'assets/{name}.txt', 'a') as f:
        f.write('\n' + str(id))
    pass

def loadUrl(url, session):
    for attempts in range(10):
        try:
            html=session.get(url)
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
    for song_num in range(len(html_list)):
        html_list[song_num] = html_list[song_num].split(",",1)
        song_list.append({})
        for data in range(len(html_list[song_num])):
            html_list[song_num][data] = html_list[song_num][data][1:-1]
        song_list[song_num]['url'] = "https://projectdxxx.me/score/index/id/" + html_list[song_num][0]
        song_list[song_num]['name'] = html_list[song_num][1]
        song_list[song_num]['name'] = dll.transcribeToRomaji(song_list[song_num]['name'])
    
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


song_list = loadList()

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
print("Choose what to download:" +
      "\n 1) CSInput charts (default, if not sure choose this)" +
      "\n 2) All charts" +
      "\n 3) Charts by author ID" +
      "\n 4) Custom content search")

mode = int(input())

checked_count = 0
found_count = 0
keyword_not_list = []
keyword_list = []

match mode:
    case 1:
        keyword_list = csinput_keyword_list
    case 2:
        keyword_list = ['']
    case 3, 4:
        if mode == 3:
            key = "author ID"
            key_start = "投稿者:\n      <a href=\"/user/index/id/"
        while True:
            keyword = {}
            keyword['display'] = input(f"Input {key}: ")
            keyword['raw'] = key_start + keyword['display'].lower()
            keyword_list.append(keyword)
            choice = input(f"Do you want to add more {key}s? [Y/n] ")
            if choice == "n":
                break


time_start = round(time(),2)

with open('assets/log.txt','a') as log:
    log.write("ppdSongSearch log file")
    if mode == 1:
        log.write("\nSearching for CSInput")
    else:
        log.write("\nSearching for the following:\n")
        log_keywords = ""
        for keyword in keyword_list:
            log_keywords += f"{keyword['display']}, "
        log_keywords = log_keywords[:-2]
        log.write(log_keywords)
    log.write("\n\nSongs found:\n")
    
with requests.Session() as session:
    cs_local_ids = dll.refreshIdDatabase(fr'{dldirectory}TARGET SCORES', return_all = True)
    no_cs_local_ids = open(r'assets/target_scores_no_csinput.txt','r').read().splitlines()

    local_ids = cs_local_ids
    if mode == 1:
        local_ids += no_cs_local_ids
    real_checked_count = None
    for song in song_list[startfrom:]:
        song_id = song['url'].split('/')[-1]
        if song_id in local_ids:
            # if real_checked_count != None:
                # print(f"\r{song['name']} already downloaded, skipping...", end='')
            rank = checked_count + 1 + startfrom
            checked_count += 1
        else:
            if real_checked_count == None: real_checked_count = 0
            html = str(loadUrl(song['url'], session))
            
            rank = checked_count + 1 + startfrom
            old_found_count = found_count
            for keyword in keyword_list:
                if keyword_not_list:
                    for keyword_not in keyword_not_list:
                        if keyword['raw'] in html.lower() and not keyword_not['raw'] in html.lower():
                            print(f"\rKeyword \"{keyword['display']}\" found in \"{song['name']}\", rank {rank}" + 20 * " " +
                                  f"\nurl: {song['url']}" +
                                  "\n- - - - -")
                            found_count += 1
                            with open('assets/log.txt','a') as log:
                                log.write(f"{song['name']}, rank {rank}, {song['url']}\n")
                            dll.LvDl(song_id, dldirectory, True, videoquality)
                else:
                    if keyword['raw'] in html.lower():
                        print(f"\rKeyword \"{keyword['display']}\" found in \"{song['name']}\", rank {rank}" + 20 * " " +
                              f"\nurl: {song['url']}" +
                              "\n- - - - -")
                        found_count += 1
                        with open('assets/log.txt','a', encoding="utf-8") as log:
                            log.write(f"{song['name']}, rank {rank}, {song['url']}\n")
                        dll.LvDl(song_id, dldirectory, True, videoquality)
            checked_count += 1
            real_checked_count+=1
            if old_found_count == found_count:
                addIDToTxt(song_id, "target_scores_no_csinput")


            time_remaining = (round(time() - time_start,2) / real_checked_count) * (len(song_list) - checked_count)
            time_remaining = timeString(time_remaining)
                
            progress = round(rank * 100 / len(song_list))
            
            print(f"\r{rank} checked, {found_count} found, {progress}% completed, {time_remaining} remaining" + 10 * " ",end='')
        
        total_time = round(time() - time_start)
        total_hr = str(total_time // 3600).zfill(2)
        total_min = str((total_time % 3600) // 60).zfill(2)
        total_sec = str(total_time % 60).zfill(2)
        total_time = f"{total_hr}:{total_min}:{total_sec}"
    if found_count:
        print(f"\rSearch completed in {total_time}. {checked_count} songs checked, {found_count} found." + 20 * " ")
    else:
        print("\rThere's no new ranked levels, you muffinhead. Go use the other tool to download more charts!" + 20 * " ")
    input("Press enter to exit...")