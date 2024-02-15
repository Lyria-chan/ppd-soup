import dllPPD as dll

path = dll.callPath()

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