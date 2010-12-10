import sys
import os
import inspect

os.sys.path.append(r'C:\eclipse_main\workspace\DOMDOM_ROOT\trunk')
os.sys.path.append(r'C:\eclipse_main\workspace\POD_ROOT\trunk')
os.sys.path.append(r'/var/local/www/domdom_src')

# global domdom
from domdom import settings, server

# local files
import www_domdom_examples_router as router

if settings.windows:
    import shutil
    shutil.copy(r'C:\eclipse_main\workspace\DOMDOM_ROOT\trunk\domdom\domdom.js', r'C:\eclipse_main\workspace\DOMDOM_ROOT\trunk\example\media\domdom.js')

settings.server.type = settings.server.types.domdom
settings.server.port = 1010

if False and settings.windows:
    settings.dirs.main    = r'C:\eclipse_main\workspace\DOMDOM_ROOT\trunk\example'
    settings.urls.main    = r'http://domdom_inmem.ajc.com' 
    settings.urls.media   = r'http://domdom_media.ajc.com'
    settings.chatty       = False
    settings.very_chatty  = False
    settings.images.make()
    server.restart_xampp_apache()
else:
    settings.dirs.main    = r'/var/local/www/domdom_src/example'
    settings.urls.main    = r'http://domdom.andrewjcarter.com' 
    settings.urls.media   = r'http://domdom_media.andrewjcarter.com' 
    settings.chatty       = False
    settings.very_chatty  = False
    settings.images.make()


# Connect to pod database . . . 
# file = settings.dirs.get_media() + os.sep + 'mypod.sqlite3'
file = ':memory:'
import dos
settings.pod.connect(file = file, attach = dos, very_chatty = False)

# Connect up your router . . . 
settings.server.router = router
    
# And finally, import and start the server
if settings.server.type == settings.server.types.domdom:
    server.run()
elif settings.server.type == settings.server.types.mod_python:
    handler = server.handler



