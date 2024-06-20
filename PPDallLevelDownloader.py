import PPDLevelDownloader as downloader
import dllPPD as dll

authorwhitelist = ['siteswap', 'kazoo king', 'sach', 'blue star', 'palmtree_freak']
authorblacklist = []

def DlLoop(i, level):
    i += 1
    print(f"{i}. {level['title']} by {level['author'].strip()}")
    print(f'--      {level['id']}       --')
    dll.LvDl(level['id'], 'D:\\KHC\\PPD\\songs\\Creator packs\\' + level['author'].strip(), True, 0, level['video'], level['title'])
    print(' ')
    return i

parsedinfo = downloader.handle('', 'all')
i = 0
for level in parsedinfo:
    if level['csinput'] == True:
        if authorwhitelist:
            if level['author'].strip().lower() in authorwhitelist:
                i = DlLoop(i, level)