import requests
import dllPPD as dll

# --------- # EDIT VALUES HERE # --------- #
path = r'C:\KHC\PPD\songs\Creator packs\EgguTasteGood'
    # the localization where the songs will be downloaded. write it inside of the  r' '. DO NOT DELETE THE R, THE PROGRAM WILL NOT WORK

# ---------------------------------------- #
link = input('Enter level link or level ID: ')
if '/' in link:
    link = link.split("/")[-1]
with requests.session() as session:
    dll.LvDl(session, link, path, True)