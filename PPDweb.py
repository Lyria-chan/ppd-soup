import eel, sys
import PPDLevelDownloader as PPDLD
import dllPPD as dll
        
        
# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']

eel.init('web', allowed_extensions=['.js', '.html'])

try:
    @eel.expose            # Expose this function to Javascript
    def importPPD(kw = '', mode = 'def', maxpages = 0):
        result = PPDLD.handle(kw, mode, maxpages)
        return result
    @eel.expose
    def set_death_flag(state):
        PPDLD.set_dl_death_flag(state)
    @eel.expose
    def callPath(path = '', mode = 'zmien moda'):
        result = dll.callPath(path, mode = 'js')
        return result
except: 
    pass

try:
    eel.start('PPDweb.html', shutdown_delay=10.0)
except OSError:
    eel.start('PPDweb.html', shutdown_delay=10.0, mode='edge')
# Start (this blocks and enters loop)
