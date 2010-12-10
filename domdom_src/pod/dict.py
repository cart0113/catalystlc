import exceptions

import core
import typed
import query
import fn

class PodDictError(exceptions.BaseException):
    pass
                                          
class Dict(core.Object):
    
    def __init__(self, dict = None, **kwargs):
        core.Object.__init__(self, **kwargs)
        if dict:
            self.update(other = dict)

    def __len__(self):
        get_one = query.RawQuery(select = fn.count(DictItem.id) >> 'count', where = DictItem.parent == self).get_one()
        if get_one:
            return get_one.count

    def __getitem__(self, key, return_node = False):
        item = core.Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one()
        if item:
            return item.value
        else:
            raise KeyError                
    
    def __setitem__(self, key, value):
        item = ((DictItem.parent == self) & (DictItem.key == key)).get_one()
        if item:
            item.value = value
        else:
            DictItem(parent = self, key = key, value = value)

    def __delitem__(self, key):
        item = core.Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one()
        if item:
            return item.delete()
        else:
            raise KeyError 

    def __contains__(self, key):
        return True if ((DictItem.parent == self) & (DictItem.key == key)).get_one() else False

    def __iter__(self):
        return self.iterkeys()

    def update(self, other):        
        for key,value in other.iteritems():
            self[key] = value
    
    def clear(self):
        (DictItem.parent == self).delete()

    def copy(self):
        return dict([(key,value) for key,value in self.iteritems()])

    def get(self, key, default = None):
        try:
            return query.Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one().value
        except AttributeError:
            return default
    
    def setdefault(self, key, default):
        try:
            return query.Query(select = DictItem.value, where = (DictItem.parent == self) & (DictItem.key == key)).get_one().value
        except AttributeError:
            self.__setitem__(key, default)
            return default
        
    def keys(self):
        return [item.key for item in core.Query(select = DictItem.key, where = DictItem.parent == self)]
    
    def iterkeys(self):
        return (item.key for item in core.Query(select = DictItem.key, where = DictItem.parent == self))

    def values(self):
        return [item.value for item in core.Query(select = DictItem.value, where = DictItem.parent == self)]
    
    def itervalues(self):
        return (item.value for item in core.Query(select = DictItem.value, where = DictItem.parent == self))
    
    def items(self):
        return [(item.key,item.value) for item in core.Query(select = DictItem.key | DictItem.value, where = DictItem.parent == self)]
    
    def iteritems(self):
        return ((item.key,item.value) for item in core.Query(select = DictItem.key | DictItem.value, where = DictItem.parent == self))

    """ Not Supported """
    def fromkeys(self):
        raise PodDictError, "method fromkeys not implemented . . ."

    def has_key(self):
        raise PodDictError, "method has_key not implemented, use 'in' or __contains__ instead . . ."
    
    def pop(self, key, *args, **kwargs):
        raise PodDictError, "method pop is not implemented . . ."

    def popitem(self):
        raise PodDictError, "method popitem is not implemented . . ."
        
class DictItem(core.Object):
    
    parent = typed.PodObject(index = True)
    key    = typed.Object(index = True)
    value  = typed.Object(index = False)
