import exceptions

import core
import typed
import query
import fn

class PodSetError(exceptions.BaseException):
    pass

class Set(core.Object):
    
    def __init__(self, set = None, **kwargs):
        core.Object.__init__(self, **kwargs)
        if set:
            self.update(set)
        
    def __len__(self):
        # Return the cardinality of set s.
        get_one = query.RawQuery(select = fn.count(SetItem.id) >> 'count', where = SetItem.parent == self).get_one()
        if get_one:
            return get_one.count

    def __contains__(self, value):
        #Test x for membership in s. 
        return True if ((SetItem.parent == self) & (SetItem.value == value)).get_one() else False

    def __iter__(self):
        return (item.value for item in core.Query(select = SetItem.value, where = SetItem.parent == self))

    def copy(self):
        return set([item.value for item in core.Query(select = SetItem.value, where = SetItem.parent == self)])

    def update(self, other):
        for elem in other:
            self.add(elem = elem)
    
    def add(self, elem):
        item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
        if item:
            item.value = elem
        else:
            SetItem(parent = self, value = elem)     

    def remove(self, elem):
        item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
        if item:
            item.delete()
        else:
            raise KeyError

    def discard(self,elem):
        item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
        if item:
            item.delete()

    def pop(self):
        item = core.Query(select = SetItem.value, where = SetItem.parent == self, limit = 1).get_one()
        if item:
            value = item.value
            item.delete()
            return value
        else:
            raise KeyError

    def clear(self):        
        (SetItem.parent == self).delete()


    """ <= """
    def __le__(self, other):
        return self.issubset(other)
    
    def issubset(self, other):
        # set <= other.  Test whether every element in the set is in other.
        return self.copy().issubset(other.copy() if isinstance(other, Set) else other)
    
    """ < """   
    def __lt__(self, other):
        #set < other.  Test whether the set is a true subset of other, that is, set <= other and set != other.
        return self.copy().__lt__(other.copy() if isinstance(other, Set) else other)
    
        
    """ >= """   
    def __ge__(self, other):
        return self.issuperset(other)

    def issuperset(self, other):
        # set >= other.  Test whether every element in other is in the set.
        super = True
        for elem in (other.copy() if isinstance(other, Set) else other):
            item = core.Query(where = (SetItem.parent == self) & (SetItem.value == elem)).get_one()
            if item is None:
                super = False
        return super
    
    """ > """   
    def __gt__(self, other):
        # set > other.  Test whether the set is a true superset of other, that is, set >= other and set != other.
        return self.copy().__gt__(other.copy() if isinstance(other, Set) else other)
        
    """ | """  
    def __or__(self, other):
        return self.union(other)
    
    def union(self, other):
        #union(other, ...) set | other | ... Return a new set with elements from the set and all others.
        # Changed in version 2.6: Accepts multiple input iterables.
        return self.copy().union(other.copy() if isinstance(other, Set) else other)

    """ & """                
    def __and__(self, other):
        return self.intersection(other)
    
    def intersection(self, other):
        #set & other & ... Return a new set with elements common to the set and all others.
        # Changed in version 2.6: Accepts multiple input iterables.
        return self.copy().intersection(other.copy() if isinstance(other, Set) else other)

    """ - """                        
    def __sub__(self, other):
        return self.difference(other)
    
    def difference(self, other):
        # difference(other, ...) set - other - ... Return a new set with elements in the set that are not in the others.
        # Changed in version 2.6: Accepts multiple input iterables.
        return self.copy().difference(other.copy() if isinstance(other, Set) else other)

    """ ^ """                        
    def __xor__(self, other):
        return self.symmetric_difference(other)
    
    def symmetric_difference(self, other):
        #set ^ other
        #Return a new set with elements in either the set or other but not both.
        return self.copy().symmetric_difference(other.copy() if isinstance(other, Set) else other)

    """ SET OPERATIONS """
    def isdisjoint(self, other):
        #Return True if the set has no elements in common with other. Sets are disjoint if and only if their intersection is the empty set.
        raise PodSetError, "method isdisjoint is not implemented at this time . . ."

    def intersection_update(self, other):
        raise PodSetError, "method intersection_update is not implemented at this time . . ."
    
    def difference_update(self, other):
        raise PodSetError, "method difference_update is not implemented at this time . . ."
    
    def symmetric_difference_update(self, other):
        raise PodSetError, "method symmetric_difference_update is not implemented at this time . . ."

class SetItem(core.Object):
    
    parent = typed.PodObject(index = True)
    value  = typed.Object(index = True)

