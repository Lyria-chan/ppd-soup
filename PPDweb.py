import eel, sys
import PPDLevelDownloader as PPDLD


def close_callback(route, websockets):
    if not websockets:
        #sys.exit()
        #exit()
        pass
        
        
# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']

eel.init('web', allowed_extensions=['.js', '.html'])

try:
    @eel.expose            # Expose this function to Javascript
    def importPPD(kw, mode = 'def', maxpages = 0):
        result = PPDLD.handle(kw, mode, maxpages)
        return result
except: 
    pass

try:
    eel.start('PPDweb.html', close_callback=close_callback)
except OSError:
    eel.start('PPDweb.html', close_callback=close_callback, mode='edge')
# Start (this blocks and enters loop)
