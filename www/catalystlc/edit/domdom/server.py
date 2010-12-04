import sys
import os
import urllib     # For URL encoding
import exceptions

import settings
from dom import Document, Element

class DomDomServerError(exceptions.Exception):
    pass

class Request(object):

    hit_count  = 0
            
    def __init__(self, http_response_code = 200):
        self.http_response_code = http_response_code
        self.content_type       = "text/html"
        self.headers_to_send    = []
        
    def __reduce__(self):
        return handle_nosave, ()
        
    def get_url_sections(self):
        return [path for path in self.path.split("/") if path != ""]
        
    def set_header(self, key, value):
        self.headers_to_send.append((key, value))

    def set_cookie(self, key, value, max_age = None, version = None):
        cookie = key + '=' + str(value)
        if max_age:
            cookie += ";Max-Age=" + str(max_age)
        if version:
            cookie += ";Version=" + str(version)
        self.headers.append(("Set-Cookie", cookie))
    
    def set_type_html(self):
        self.content_type = "text/html"

    def set_type_javascript(self):
        self.content_type = "text/javascript"
        
    def set_type_plain(self):
        self.content_type = "text/plain"
    
    def set_expiration(self, no_cache = True, expires = 0):
        if no_cache:
            request.set_header("Cache-Control", "no-cache, post-check=0, pre-check=0")
            request.set_header("Pragma", "no-store, no-cache, must-revalidate")
        if expires is not None: 
            request.set_header("Expires", str(expires))

    def redirect(self, url, code = 301):
        self.http_response_code  = code
        self.headers_to_send        = []
        self.set_header(key = "Location", value = url)
     
    def route(self):
        url_sections = self.get_url_sections()
        if len(url_sections) > 0 and url_sections[-1].split(".")[-1] == 'ico':
            if settings.chatty:
                print "\n\n\n Ignored media request for icon '" + path + "' . . ."
            return ""
        elif settings.chatty:
            print "\n\n\nIncoming request #" + str(Request.hit_count) + " for path '" + self.path + "' . . ."
            Request.hit_count += 1
            # First, branch -- an event url 
            if len(url_sections) > 0 and url_sections[0] == "event":
                return self.route_event(url_sections = url_sections)
            # If not event, then pass request to local router . . . . 
            else:                
                if settings.server.router is None:
                    settings.server.router = sys.modules['__main__']
                return settings.server.router.route(request = self, url_sections = url_sections)
            
    def route_event(self, url_sections):
        self.set_type_plain()
        dtime       = int(url_sections[1])
        id          = url_sections[2].split(":")    
        # First, try and get the event from the pod cache
        event = settings.cache.get_inst(cls_id = int(id[0]), inst_id = int(id[1]))
        if event.pod.check_if_deleted() or event.get_dtime() != dtime:            
            raise DomDomServerError, "This event has been deleted . . ."
        else:                
            output = event.handle_request(request = request)                                    
            if settings.chatty:
                print "Event  '", event, "' with sensor '", event.sensor, "' with handler '", event.handler, " and document '", event.document, "' being called . . ."
                print "AJAX returning . . . \n<-- start js output -->\n", output, "<-- end js output -->\n",        
            return output 
    
def handle_nosave(*args):
    return None
        
if settings.server.type == settings.server.types.domdom:

    import BaseHTTPServer
    
    class Request_BaseHTTPServer(Request, BaseHTTPServer.BaseHTTPRequestHandler):
    
        def __init__(self, request, client_address, server):
            Request.__init__(self)
            BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
            
        def do_GET(self):
            response = self.route()

            # Now, send headers . . . 
            self.send_response(self.http_response_code)
            self.send_header("Content-type", self.content_type)
            for header in self.headers_to_send:
                self.send_header(header[0], header[1])
            self.end_headers()

            if self.http_response_code == 200:
                self.wfile.write(response)
    
    def run(): 
        BaseHTTPServer.HTTPServer((settings.server.ip, settings.server.port), Request_BaseHTTPServer).serve_forever()
        
elif settings.server.type == settings.server.types.mod_python:

    from mod_python import apache

    class Request_ModPython(Request):
        pass

    def handler(req):
        req.write('HELLO' + settings.name)
        return(apache.OK)

    


        
    
    