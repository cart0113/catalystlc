import os

chatty      = False
very_chatty = False

newline     = "\n"
tab         = "\t"

class server:
    ip     = '127.0.0.1'
    port   = 1212
    type   = 0
    router = None
    class types:
        domdom        = 0
        mod_python    = 1
        
class pod:
    db          = None
    clear_cache = False
    close       = False

class events:
    send_mousemove_on = 1

class urls:
    main = None

class dirs:
    main = None

def get_dir_main():
    return dirs.main

def get_dir_media():
    return getattr(dirs, 'media', dirs.main + os.sep + 'media')
        
def get_dir_css():
    return getattr(dirs, 'css',    get_dir_media())

def get_dir_images():
    return getattr(dirs, 'images', get_dir_media() + os.sep + 'images')

def get_url_main():
    return urls.main
   
def get_url_event():
    return getattr(urls, 'event', urls.main + '/event')
    
def get_url_media():
    return getattr(urls, 'media', urls.main + '/media')

def get_url_images():
    return getattr(urls, 'images', urls.media + '/images')
    
def get_url_css():
    return getattr(urls, 'css',   get_url_media())

def get_url_domdom_javascript():
    return getattr(urls, 'domdom_javascript', get_url_media() + '/domdom.js')

def make_images(images_dir = None, images_url = None, py_dir = None):

    if(images_dir is None):
        images_dir = get_dir_images()

    if(images_url is None):
        images_url = get_url_images()
    
    if(py_dir is None):
        py_dir = os.getcwd()

    output = recursive_make_images(dir = images_dir, url = images_url, output = "", tab = "")
    
    open(py_dir + os.sep + 'images.py', 'w').write(output)

def recursive_make_images(dir, url, output, tab):
    
    for path in os.listdir(dir):
        full_path = dir + os.sep + path
        full_url  = url + '/' + path
        if(os.path.isfile(full_path) and full_path[-4:] in ['.png', '.jpg', '.gif']):
            output += tab + path.replace('.', '_').replace("-", "_") + ' = "' + full_url + '"\n'

    for path in os.listdir(dir):
        full_path = dir + os.sep + path
        full_url  = url + '/' + path
        # TODO -- Why was it descending into _svn anyway 
        if(os.path.isdir(full_path) and '.svn' not in full_path and path[0] != "."):
            output = recursive_make_images(dir = full_path, url = full_url, tab = tab + "\t", output = output + tab + "class " + path.replace(".", "_") + ":\n")

    return output
    
    

    