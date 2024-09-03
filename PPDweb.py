import eel, os
import PPDLevelDownloader as PPDLD
import dllPPD as dll
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path) 
# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']

eel.init('web', allowed_extensions=['.js', '.html'])

try:
    @eel.expose            # Expose this function to Javascript
    def importPPD(kw = '', mode = 'def'):
        result = PPDLD.handle(kw, mode)
        return result
    @eel.expose
    def set_death_flag(state):
        PPDLD.set_dl_death_flag(state)
    @eel.expose
    def callPath(path = '', mode = 'zmien moda'):
        result = dll.callPath(path, mode = 'js')
        return result
    @eel.expose
    def lvDl(song_id, vquality = 1, v_url = None, folder_title = None, folder_path = callPath(), iskakasi = 'False'):
        result = dll.LvDl(song_id, folder_path, iskakasi, vquality, v_url, folder_title)
        return result
    @eel.expose
    def db_local(mode = 'delete', data = ''):
        PPDLD.db_local(mode, data)
        return
except: 
    pass

try:
    eel.start('PPDweb.html', shutdown_delay=8.0)
except OSError:
    eel.start('PPDweb.html', shutdown_delay=8.0, mode='edge')

