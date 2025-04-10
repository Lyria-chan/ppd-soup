import extra_soup as downloader
import extra_library as dll
from time import sleep

edit_code_mode = False
def DlLoop(level):
        print(f"Downloading {enum(i)} chart: {level['title']} by {level['author'].strip()}")
        print(f'--      {level['id']}       --')
        # if edit_code_mode:
        #    add_to_level_path = 'Creator packs\\' + level['author'].strip()
        # else:
        #    add_to_level_path = level['author'].strip()
        add_to_level_path = 'Creator packs\\' + level['author'].strip()
        dll.LvDl(level['id'], 'D:\\KHC\\PPD\\songs\\' + add_to_level_path, True, 0, level['video'], level['title'])
        print(' ')

def enum(number):
    # turn 1 into '1st', 2 into '2nd', 3 into '3rd', 4 into '4th', etc.
    if number % 10 == 1 and number % 100 != 11:
        return str(number) + 'st'
    elif number % 10 == 2 and number % 100 != 12:
        return str(number) + 'nd'
    elif number % 10 == 3 and number % 100 != 13:
        return str(number) + 'rd'
    else:
        return str(number) + 'th'

if edit_code_mode:
        # authorwhitelist = ['siteswap', 'kazoo king', 'sach', 'blue star', 'palmtree_freak']
    authorwhitelist = ['eggutastegood']
    authorblacklist = []
    path = 'D:\\KHC\\PPD\\songs\\Creator packs\\'

    parsedinfo = downloader.handle('', 'all')
    i = 0
    for level in parsedinfo:
        if level['csinput'] == True:
            if authorwhitelist:
                if level['author'].strip().lower() in authorwhitelist:
                    DlLoop(level)
                    i+= 1




else:
    i = 1
    # STILL WIP!!!!!!!!!! WORKING ON IT
    path = dll.callPath()
    batch_file = 'batch_downloading.txt'
    # check if file exists, if not, create it
    case = input(f'Change batch file to be used? Currently: {batch_file} (y/N) ')
    if case.lower() == 'y':
        batch_file = input('Your file name: ')
    try:
        with open(batch_file, 'r') as file:
            pass
    except FileNotFoundError:
        with open(batch_file, 'w') as file:
            file.write('''# Here enter the IDs or links of levels you want to download, line by line
# You can also add authors be name, like: @siteswap or @blue star
# Everything after # will be ignored''')

    # read lines from file batch_downloading.txt    
    with open(batch_file, 'r') as file:
        lines = file.readlines()
    # if line starts with #, ignore it
    lines = [line for line in lines if not line.startswith('#')]
    links = []
    authors = []
    # if with @, add to authors, if not, add to links
    for line in lines:
        if '@' in line:
            authors.append(line.split('@')[1].lower().strip())
        else:
            links.append(line.lower().strip())

    if not links and not authors:
        print(f'No links or authors found! Add them to {batch_file}')
        exit()
    
    case = input(f'Change path? Currently: {path} (y/N) ')
    if case.lower() == 'y':
        pcheck = [i for i in path.split("\\") if i]
        if 'songs' in pcheck and not pcheck[-1] in 'songs':
            path = path[: path.index('songs\\') + 6]
        append = input(f'New path: {path}')
        dll.callPath(path + append + "\\")
    
    if links:
        print("Now downloading charts by IDs...")
        sleep(2)
        for link in links:
            print(f"Downloading {enum(i)} chart: https://projectdxxx.me/score/index/id/{link}")
            dll.LvDl(link, path, True)
            i += 1
        print(f'Downloaded {i-1} charts by IDs!')
        print(' ')
    if authors:
        print('Now downloading charts from authors...')
        sleep(2)

        parsedinfo = downloader.handle('', 'all')
        for level in parsedinfo:
            if level['author'].strip().lower() in authors:
                DlLoop(level)
                i += 1






    """
    link = input('Enter level link or level ID: ')
    case = input(f'Change path? Currently: {path} (y/N) ')
    if case.lower() == 'y':
        pcheck = [i for i in path.split("\\") if i]
        if 'songs' in pcheck and not pcheck[-1] in 'songs':
            path = path[: path.index('songs\\') + 6]
        append = input(f'New path: {path}')
        dll.callPath(path + append + "\\")
    if '/' in link:
        link = link.split("/")[-1]
    dll.LvDl(link, path, True)
    """