import sys
import os

import pod
from domdom import settings

windows = False if os.path.isdir('/usr') else True 
settings.windows = windows

settings.pod.db = pod.Db(file = ":memory:", connect = True)

settings.server.type = settings.server.types.domdom
settings.server.port = 1993

if settings.windows:
    settings.dirs.main    = r'C:\eclipse_main\workspace\WWW_CATALYSTLC_EDIT'
    settings.urls.main    = r'http://edit.clc.org' 
    settings.urls.media   = r'http://media.clc.org'
    settings.chatty       = True
    settings.very_chatty  = False
else:
    settings.dirs.main    = r'/var/local/www/catalystlc/edit'
    settings.urls.main    = r'http://edit.catalystlc.org' 
    settings.urls.media   = r'http://media.catalystlc.org' 
    settings.chatty       = True
    settings.very_chatty  = False

settings.make_images()

# setup up a router if you want -- if you don't do this, you need to define a route() method in __main__
if True:
    # On this branch, we setup a local router
    import printable
    
    def route(request, url_sections):
        if len(url_sections) == 0 or url_sections[0] == 'main':
            return printable.Printable.route(request = request, url_args = url_sections[1:])
        elif url_sections[0] == 'docs':
            return root.docs.index.route(request = request, url_args = url_sections[1:]).publish()
else:
    # On this branch, we use a 'pre-canned' router that auto maps url to python path 
    from domdom import routers
    settings.server.router = routers.Url2PythonPath
    
    
# And finally, import and start the server
from domdom import server

if settings.server.type == settings.server.types.domdom:
    server.run()
elif settings.server.type == settings.server.types.mod_python:
    handler = server.handler

