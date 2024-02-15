import subprocess

li = ['lxml', 'eel', 'pykakasi', 'niconico-dl', 'pytubefix', 'gdown']

for l_name in li:
    subprocess.check_call(['pip', 'install', l_name])