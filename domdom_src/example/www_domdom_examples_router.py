# Then, write your router . . .  
from domdom import settings

def route(request):
    if len(request.url_sections) == 0 or request.url_sections[0] != 'examples':
        return request.redirect(url = settings.urls.main + '/examples')
    elif len(request.url_sections) == 1 and request.url_sections[0] == 'examples':
        pass
    elif len(request.url_sections) > 1 and request.url_sections[1] == 'iblog':    
        import iblog    
        return iblog.BlogPage.route(cls = iblog.BlogPage, request = request[2:])
    else:
        return request.send_error(404)