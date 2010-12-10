import os
import pod as pod_db

chatty      = False
very_chatty = False

newline     = "\n"
tab         = "\t"

windows = False if os.path.isdir('/usr') else True 

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
    cache       = None
    cursor      = None
    commit      = True
    clear_cache = False
    close       = False

    @staticmethod
    def connect(file, remove = False, clear = False, chatty = False, very_chatty = False, clear_cache = False, close = False, attach = None):
        pod.clear_cache = clear_cache
        pod.close       = close
        pod.db          = pod_db.Db(file = file, attach = attach, remove = remove, clear = clear, chatty = chatty, very_chatty = very_chatty) 
        pod.cache       = pod.db.cache 
        pod.cursor      = pod.db.cursor
        return pod.db 
    
    @staticmethod
    def attach(obj):
        pod.db.attach(obj = obj)

class events:
    send_mousemove_on = 1

class urls:
    
    main = None
    
    @staticmethod  
    def get_main():
        return urls.main
    
    @staticmethod   
    def get_event():
        return getattr(urls, 'event', urls.main + '/event')
        
    @staticmethod
    def get_media():
        return getattr(urls, 'media', urls.main + '/media')
    
    @staticmethod
    def get_images():
        return getattr(urls, 'images', urls.media + '/images')
        
    @staticmethod
    def get_css():
        return getattr(urls, 'css',   urls.get_media())
    
    @staticmethod
    def get_domdom_javascript():
        return getattr(urls, 'domdom_javascript', urls.get_media() + '/domdom.js')

class dirs:
    
    main = None

    @staticmethod
    def get_main():
        return dirs.main
    
    @staticmethod
    def get_media():
        return getattr(dirs, 'media', dirs.main + os.sep + 'media')
    
    @staticmethod        
    def get_css():
        return getattr(dirs, 'css',    dirs.get_media())
    
    @staticmethod
    def get_images():
        return getattr(dirs, 'images', dirs.get_media() + os.sep + 'images')

class images:
    
    @staticmethod
    def make(images_dir = None, images_url = None, py_dir = None):
    
        if images_dir is None:
            images_dir = dirs.get_images()
    
        if images_url is None:
            images_url = urls.get_images()
        
        if py_dir is None:
            py_dir = os.getcwd()
    
        output = images.make_recursive(dir = images_dir, url = images_url, output = "", tab = "")
        
        open(py_dir + os.sep + 'images.py', 'w').write(output)

    @staticmethod
    def make_recursive(dir, url, output, tab):
        
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
                output = images.make_recursive(dir = full_path, url = full_url, tab = tab + "\t", output = output + tab + "class " + path.replace(".", "_") + ":\n")
    
        return output

    @staticmethod    
    def get_dir(self):
        return dirs.get_images()

    @staticmethod    
    def get_url(self):
        return urls.get_images()

    