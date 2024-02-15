import PPDLevelDownloader as downloader
import dllPPD as dll

parsedinfo = downloader.handle('', 'all')
i = 0
for level in parsedinfo:
    if level['csinput'] == True:
        dll.LvDl(level['id'], 'D:\\KHC\\PPD\\songs\\Creator packs\\' + level['author'].strip(), True, 0, level['video'], level['title'])
        i += 1
        print(f"{i}. {level['title']} by {level['author'].strip()}")
        print(level['saved'])

    