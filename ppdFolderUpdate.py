import os, requests, json
import PySimpleGUI as sg
import dllPPD as dll

def loadUrl(url):
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
    html = loadUrl('https://projectdxxx.me/api/active-score')
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
        song['name'] = dll.translateAndCapitalize(song['name'])
    
    return song_list

song_list = loadList()

try:
    with open("assets\path.json","r") as f:
        f = f.read()
        path = json.loads(f)
    print(path)
except FileNotFoundError:
    layout = [  [sg.Text("Looks like you haven't entered the songs' path yet!")],
            [sg.Text("(This pop-up should only appear the first time you're running the program.)")],
            [sg.Checkbox('Use the default path', default = True)],
            [sg.Text('Enter a custom path:')],
            [sg.Input()],
            [sg.Button('OK')] ]
    window = sg.Window('PPDFolderUpdate', layout)
    event, values = window.read()
    if values[0]:
        path = "C:\KHC\PPD\songs"
    else:
        path = values[1]
    window.close()
    
with open("assets\path.json","w") as f:
    json.dump(path,f)
    
for root, dirs, files in os.walk(path, topdown=False):
    for name in dirs:
        if not name == "sound" and not '[NO MOVIE]' in name:
            try:
                with open(os.path.join(root,name,'limk.txt'), 'r') as limk:
                    limk = limk.read()
                    if limk == '':
                        print(f"INVALID LINK FOUND IN DIR {name}")
                        break
            except FileNotFoundError:
                continue
            except Exception as e: print(e)
            print(name)
            for song in song_list:
                if limk in song['url']:
                    if ". " in name:
                        dirname = name.split(". ",1)
                        try:
                            test = int(dirname[0])
                            dirname_number = dirname[0]
                            dirname = dirname[1]
                        except ValueError:
                            dirname = name
                            dirname_number = 0
                    else:
                        dirname = name
                        dirname_number = 0
                    try:
                        if int(dirname_number) != song_list.index(song)+1:
                            os.rename(os.path.join(root,name),os.path.join(root,str(song_list.index(song)+1)+". "+dirname))
                    except Exception as e: print(e)