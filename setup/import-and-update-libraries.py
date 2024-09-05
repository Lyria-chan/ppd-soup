import subprocess

li = ['lxml', 'eel', 'pykakasi', 'niconico.py', 'pytubefix', 'gdown']

for l_name in li:
    subprocess.check_call(['pip', 'install', l_name, '--upgrade'])