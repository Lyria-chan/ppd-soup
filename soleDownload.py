import requests
import dllPPD as dll


path = dll.callPath()

link = input('Enter level link or level ID: ')
if '/' in link:
    link = link.split("/")[-1]
with requests.session() as session:
    dll.LvDl(session, link, path, True)