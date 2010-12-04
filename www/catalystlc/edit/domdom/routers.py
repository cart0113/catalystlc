import exceptions

from dom import Document
import settings

class DomDomRouterError(exceptions.Exception):
    pass

class Router(object):
    pass

class Url2PythonPath(Router):

    modules    = []
    routeables = []

    @staticmethod
    def route(request, url_sections, root = 'root'):
        pass

    @staticmethod
    def mapper():
        pass

