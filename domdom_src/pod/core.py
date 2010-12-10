import os
import sys
import time
import exceptions
import warnings
import inspect

import db
import typed

from query import Query, RawQuery

import fn

class PodMetaError(exceptions.BaseException):
    pass

class PodNoDatabaseError(exceptions.BaseException):
    pass

class Meta(type):
    
    POD_RESV_SET = set(['id', 'pod', 'store', 'where'])
    POD_GETA_SET = set(['__new__', '__instancecheck__', 'pod', 'where', '__class__', '__dict__']) 
    POD_SETI_SET = set(['__class__', 'id'])
    
    def __init__(cls, name, bases, dict):      
        
        if cls.__module__ == Meta.__module__:
            # We don't want to create tables and so on for the base classes defined in this module.
            return

        if len(bases) > 1:
            raise PodMetaError, "Currently, pod does not support multiple inheritance . . . "
                
        for key in Meta.POD_RESV_SET:
            if key in dict:
                raise PodMetaError, "'" + key + "' is a reserved class variable and cannot be defined in class " + str(cls)
              
        cls_pod = type(cls).Pod(cls=cls, parent=bases[0] if bases[0] is not Object else None)
        type.__setattr__(cls, 'pod',   cls_pod)        
        type.__setattr__(cls, 'where', type(cls).Where(cls_pod = cls_pod))
                    
    def __getattribute__(cls, key):
        
        if key in Meta.POD_GETA_SET or key in type.__getattribute__(cls, '__dict__'):
            return type.__getattribute__(cls, key)     
        elif key == 'store':
            store = db.Store(db=type.__getattribute__(cls, 'pod').db, prefix=type.__getattribute__(cls, 'pod').table + '_store_')
            type.__setattr__(cls, 'store', store)
            return store
        elif key == 'id':
            id = typed.Int(index=False, cls_pod=type.__getattribute__(cls, 'pod'), name='id')
            type.__setattr__(cls, 'id', id)
            return id
        else:
            return type.__getattribute__(cls, key)
    
    def __setattr__(cls, key, value):
        
        # Here, __setattr__ is only performing error checking because dynamic creation of pod_types has been removed . . . 
        
        if key in Meta.POD_RESV_SET:
            raise PodMetaError, "Key '" + key + "' is a reserved attribute of pod classes . . . "
        
        if isinstance(value, typed.Typed):
            raise PodMetaError, "You cannot create a pod_type '" + key + "' dynamically -- please add it to the class header . . . "
        
        if isinstance(getattr(cls, key, None), typed.Typed):
            raise PodMetaError, "Attr '" + key + "' is of type pod.typed.Typed -- you cannot alter this attribute dynamically -- it must be performed in class header . . ."
        
        return type.__setattr__(cls, key, value)
        
    def __iter__(cls):
        return Query(where=cls).__iter__()
                        
    def execute(cls, query, args=()):
        return cls.pod.cursor.execute(query.replace("cls_table ", cls.pod.table + " ").replace("cls_table_dict", cls.pod.table_dict), args)

    def executemany(cls, query, args=()):
        return cls.pod.cursor.executemany(query.replace("cls_table ", cls.pod.table + " ").replace("cls_table_dict", cls.pod.table_dict), args)
        
    def migrate(cls, new_cls):
        
        if not isinstance(new_cls, Meta):
            raise PodMetaError, "New class must be of type pod.Object"

        for obj in Query(where=cls, child_classes = False):
            obj.full_load()
            new_cls(**obj.copy())
            
        cls.drop(child_classes = False)
        
    def drop(cls, child_classes = True):
        cls.pod.table_drop(child_classes = child_classes)
    
    def clear_all(cls, child_classes = True):
        cls.pod.table_clear(child_classes = child_classes)
        
    def get_count(cls, child_classes=True, count=0):
        get_one = RawQuery(select=fn.count(cls.id) >> 'count').get_one()

        count = get_one.count + count if get_one else count
        
        if child_classes:
            for child_pod in cls.pod.child_pods:
                count = child_pod.cls.get_count(child_classes=child_classes, count=count)
        return count
        
    def get_db(cls):
        return type.__getattribute__(cls, 'pod').db
    
    class Pod(object):
    
        def __init__(self, cls, parent):
            # pass ins
            self.cls = cls
            self.parent_pod = getattr(parent, 'pod', None)
            self.db = None
            self.id = None
            
            self.table = self.get_table_name()
                    
            # Init vars
            self.typed_group = {}
            self.type_callbacks_create = set()
            self.type_callbacks_load = set()
            self.child_pods = set()  
            
            # First, update parent and add any pod_types a parent has to your local dictionary. 
            # The reason you need a local copy of a pod_type is because if you have a ParentClass, ChildClass and a pod_type called 'name'
            # you want ParentClass.name == 'Fred' to return all objects with a name of 'Fred' but ChildClass.name == 'Fred' to 
            # only return ChildClass object with a name == 'Fred'.  type_add_parents takes care of this . . .

            # This updates all the pod_types passed in from the class header. 
            for name, pod_type in self.cls.__dict__.iteritems():
                 if isinstance(pod_type, typed.Typed):
                    self.typed_group[name] = pod_type
                    pod_type.on_pod_init(cls_pod=self, name=name)

            if self.parent_pod is not None:
                object.__getattribute__(self.parent_pod, 'child_pods').add(self)
                for name, pod_type in object.__getattribute__(self.parent_pod, 'typed_group').iteritems():
                    if name in self.cls.__dict__:
                        raise PodMetaError, "Class " + str(self.cls) + " is trying to add pod_type " + name + ", but this pod_type already defined in parent " + str(object.__getattribute__(self.parent_pod, 'cls')) + " . . ."
                    else:
                        pod_type = pod_type.get_deep_copy(cls_pod=self, name=name)
                        type.__setattr__(self.cls, name, pod_type)
                        self.typed_group[name] = pod_type

            # register table name
            if db.register.global_db is None:    # This means no db connection has been made yet
                db.register.pods_to_attach[self.table] = self
                self.__class__ = type.__getattribute__(cls, 'PodNoDatabase')
            elif db.register.global_db is False: # False means db connection was made with 'attach' parameter
                self.db = self.get_parent_db()
            elif db.register.global_db:
                self.attach_to_db(db = db.register.global_db)
                                    
        def __getstate__(self):
            raise PodMetaError, "You cannot pickle a Pod CLASS pod._Meta object . . . "

        def get_parent_db(self):
            
            if self.parent_pod:
                if self.parent_pod.db:
                    db = self.parent_pod.db if self.parent_pod.db is not None else self.parent_pod.get_parent_db()
                    self.attach_to_db(db = db)
                    return db
            else:
                return None
        
        def attach_to_db(self, db):
            
            # If the local 'self.db' is not set, set it to the current and update all your children. 
            # If it is already set, that's okay as long as the two databases match. 
            if self.db is None:

                self.table_dict = self.table + '_kvdict'
                
                self.db         = db               
                self.cursor     = db.get_new_cursor(cls_pod = self)
                
                table_state = self.cursor.table_state_get()
                
                if table_state is None:   
                    self.table_create()   # Note, this calls 'activate_on_get_table_id' at the right place . . . 
                else:
                    self.id      = table_state['id'] 
                    index_kv_old = table_state['index_kv']
                    
                    self.index_kv = getattr(self.cls, 'POD_DYNAMIC_INDEX', self.db.dynamic_index)                        
                    self.mtime    = self.get_mtime(source_file=inspect.getsourcefile(self.cls))
        
                    self.activate_on_get_table_id()
                            
                    if (int(table_state['mtime']) != self.mtime) or (self.index_kv != index_kv_old):
                        self.table_check_for_changes(index_kv_old = index_kv_old)
 
                for child_pod in self.child_pods:
                    child_pod.attach_to_db(db = db)
                    
            elif db is not self.db:
                raise PodMetaError, "Class '" + str(self.cls) + "' is already attached to a database"

        def activate_on_get_table_id(self):
            """ This functions is only called by 1) activate or 2) table_create """
            # This is used by both activate and table_create
            self.db.cache.class_pods[self.id] = self
            self.cache = {}      
            self.zombies = set()    
            self.fulls   = set()  
            for pod_type in self.typed_group.itervalues():
                pod_type.on_db_attach(db=self.db, cls_pod = self)
             
        def clear(self):
            self.cache.clear()
            self.zombies.clear()
            self.fulls.clear()
     
        def get_table_name(self):
            #
            # The table name is: 
            #   1. The module path plus the class name, for example myapp_models_Person. 
            #   2. Just the class name (e.g. just Person) if the user has set POD_TABLE_NAME set to True
            #      in class header. 
            #   3. POD_TABLE_NAME if it's set to a string in the class header
            #
            #   Full name is harder to read if working with sql table directly, but 
            #   uses full module name so it is less likely to have a namespace collision. 
            #
            cls_name = type.__getattribute__(self.cls, '__name__')
            pod_table_name = type.__getattribute__(self.cls, '__dict__').get('POD_TABLE_NAME', None)
            if pod_table_name is None:
                return '_'.join(self.cls.__module__.split('.') + [cls_name])
            elif pod_table_name is True:
                return cls_name
            else:
                return pod_table_name
        
        def get_mtime(self, source_file=None):
            try:
                return int(os.path.getmtime(source_file)) if source_file else int(time.time())
            except:
                if source_file[-7:] == 'list.py' or source_file[-7:] == 'dict.py' or source_file[-6:] == 'set.py':  
                    return 0
                else:                                     
                    raise PodMetaError, "Cannot get mtime on file '" + source_file + "' . . ."
            
        """ TABLE OPERATIONS """
        def table_create(self):

            # First, get the variables . . . 
            self.mtime = self.get_mtime(source_file=inspect.getsourcefile(self.cls))
            self.index_kv = type.__getattribute__(self.cls, '__dict__').get('POD_DYNAMIC_INDEX', self.db.dynamic_index)

            self.id = self.cursor.create_class_tables()
            if self.index_kv:
                self.cursor.index_kv_add()

            self.activate_on_get_table_id()
                        
            for name, pod_type in self.typed_group.iteritems():
                # This will call 'sql_table_state_set'
                self.type_create(name=name, pod_type=pod_type, is_new=True)
            
            if len(self.typed_group) == 0:
                # if len == 0, the iteration above will not call 'sql_table_state_set', so call it. 
                self.cursor.table_state_set()

        def table_drop(self, child_classes = True):
            if self.id:
                self.cursor.drop_class_tables()
                self.db.commit(clear_cache=True, close=False)
                if child_classes:
                    for child_pod in self.child_pods:
                        child_pod.table_drop()

        def table_clear(self, child_classes=True):
            if self.id:                     
                self.clear()   
                self.cursor.clear_class_tables()
                if child_classes:
                    for child_pod in self.child_pods:
                        child_pod.table_clear()

        def table_check_for_changes(self, index_kv_old, copy_dropped_to_dict=True):

            if self.index_kv is True and index_kv_old is False:
                self.cursor.index_kv_add()
                self.table_change_msg(msg='Adding index for dynamic attributes . . . ')
            elif self.index_kv is False and index_kv_old is True:
                self.cursor.index_kv_drop()
                self.table_change_msg(msg='Dropping index for dynamic attributes . . . ')

            old_pod_types = self.cursor.get_old_pod_types()
            set_old_pod_types = set(old_pod_types.keys())
            
            for name, pod_type in old_pod_types.iteritems():
                pod_type.on_pod_init(cls_pod=self, name=name)
            
            if set(self.type_get_current_db_pod_types()) != set_old_pod_types:  
                raise PodMetaError, "Fatal error -- pod_types in table are not same as pod_types in class table . . ."
            
            # All the things that could change: 
            #
            #    What could happen:
            #         1. Drop:                     the new_pod_types might not have a pod_type found in old_pod_types -->  In this case, drop the old pod_type. 
            #         2. Add:                      the new_pod_types might have a pod_type not found in old_pod_types -->  In this case, add the new pod_type. 
            #         3. Change typed.Typed:       a new_pod_type might have changed type -- in this case, drop and add. 
            #         4. Change Index or Unique:   the new_pod_types might have a pod_type whose index/unique is not the same as the old pod_type --> In this case, either add/drop index on that pod_type. 
            #         5. Do nothing!:              a new pod_type and the old pod_type match!!!  YES!!
            #
            #    After this, update the mtime on the class and restore pod_type in the database. 

            set_new_pod_types = set(self.typed_group.keys())
            
            set_changed_type_pod_types = set([name for name in set_new_pod_types & set_old_pod_types if self.typed_group[name].__class__ != old_pod_types[name].__class__])
            
            # You need to drop 1) all pod_types that changed type and 2) if auto_drop is true, you need to also drop set_old_pod_types - set_new_pod_types
            #
            # ** auto_drop no longer supported, so this line has changed
            # set_drop_pod_types = set_changed_type_pod_types if self.auto_drop is False else set_changed_type_pod_types | (set_old_pod_types - set_new_pod_types)
            set_drop_pod_types = set_changed_type_pod_types | (set_old_pod_types - set_new_pod_types)
            set_add_pod_types = set_changed_type_pod_types | (set_new_pod_types - set_old_pod_types)
                       
            # 1. Drop 
            if len(set_drop_pod_types) > 0:
                self.type_drop_old(old_pod_types=old_pod_types, set_old_pod_types=set_old_pod_types, set_drop_pod_types=set_drop_pod_types, copy_dropped_to_dict=copy_dropped_to_dict)

            # 2. Add
            for name in set_add_pod_types:
                self.type_create(name=name, pod_type=self.typed_group[name], is_new=False)

            # 4. Change index
            for new_pod_type, old_pod_type in [(self.typed_group[name], old_pod_types[name]) for name in (set_old_pod_types & set_new_pod_types)]:   
                if new_pod_type.index != old_pod_type.index:
                    if old_pod_type.index:
                        self.type_drop_index(name=old_pod_type.name)
                    if new_pod_type.index:
                        self.type_add_index(name=new_pod_type.name) #, unique=new_pod_type.index == typed.unique)
                    
            self.cursor.table_state_set()

        def table_change_msg(self, msg=None):
            
            if self.db.chatty:
                if 'start_message' not in self.__dict__:
                    self.start_message = "Class '" + self.cls.__name__ + "' needs to be created/updated . . . checking to see if any pod_types need to be updated:"
                if self.start_message:
                    print self.start_message
                    self.start_message = False
                if msg:
                    print "\tFor class '" + self.cls.__name__ + "' " + msg
        
        """ TYPE OPERATIONS """ 
        def type_drop_old(self, old_pod_types, set_old_pod_types, set_drop_pod_types, copy_dropped_to_dict):
            
            set_keep_pod_types = set_old_pod_types - set_drop_pod_types
            self.table_change_msg(msg="dropping pod_types " + ",".join(set_drop_pod_types) + "  . . . ")
            list_keep_pod_types = list(set_keep_pod_types)
            list_drop_pod_types = list(set_drop_pod_types)

            if copy_dropped_to_dict and len(list_drop_pod_types) > 0:
                self.cursor.execute("SELECT " + ",".join(['id'] + list_drop_pod_types) + " FROM " + self.table)
                args = []
                cache = self.db.cache
                for row in self.cursor.fetchall():
                    for i, type_name in enumerate(list_drop_pod_types):
                        old_pod_type = old_pod_types[type_name]
                        value = row[i+1]
                        if value is None:
                            new_value = None
                        elif isinstance(old_pod_type, typed.Object):
                            new_value = value
                        elif isinstance(old_pod_type, typed.PodObject):
                            new_value = Undefined(id = value.split(":"), cache = cache)
                        else:
                            new_value = old_pod_type.load(value)                             
                        args.append((row[0], type_name,self.cursor.pickle_dump(value = new_value),))  # Don't need to provide inst,attr for mutables check because this is a copy
                self.cursor.executemany("INSERT OR REPLACE INTO " + self.table_dict + " (fid,key,value) VALUES (?,?,?)", args)

            # Now, put humpty dumpty back together again . . . 
            self.cursor.execute("SELECT " + ",".join(['id'] + list_keep_pod_types) + " FROM " + self.table)
            rows = self.cursor.fetchall()
                        
            self.cursor.execute("DROP TABLE IF EXISTS " + self.table)                
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table + " (id INTEGER PRIMARY KEY)")
            
            for name in list_keep_pod_types:
                old_pod_types[name].on_pod_init(cls_pod=self, name=name)
                self.type_create(name=name, pod_type=old_pod_types[name], is_new=True)
            
            # NOW PUT ALL THE ROWS BACK INTO DB -- HOWEVER, COPY PED COLUMN DATA BACK INTO THE DICT

            names = '(' + ",".join(['id'] + list_keep_pod_types) + ')'                
            quest = '(' + ",".join(["?" for i in range(len(list_keep_pod_types) + 1)]) + ')'
            self.cursor.executemany("INSERT INTO " + self.table + " " + names + " VALUES " + quest, (row[0:len(list_keep_pod_types) + 1] for row in rows))
                
        def type_drop_and_delete_forever(self, pod_type):

            if self.db.chatty:  
                print "You have chosen to permentally drop and delete pod_type '" + pod_type.name + "' from '" + self.table + "'.  All data will be lost forever "
                print "Remember!  You have to remove this pod.typed attribute from the class header or else it will be added back on next import . . . "
            
            delattr(self.cls, pod_type.name)
            del self.typed_group[pod_type.name]
            
            self.table_check_for_changes(index_kv_old = self.index_kv, copy_dropped_to_dict=False)
            
            for child_pod in self.child_pods:
                child_pod.type_drop_and_delete_forever(child_pod.typed_group[pod_type.name])

            # Now you want to resave a local mtime, because we want to reimport the class after this . . . 
            self.cursor.table_state_set()
            
            for inst in self.cache.itervalues():
                dict = object.__getattribute__(inst, '__dict__')
                if pod_type.name in dict:
                    del dict[pod_type.name]
            
        def type_create(self, name, pod_type, is_new):
            # If the pod_type is new, then you don't need to copy all the data from the __dict__ to the new pod_type. 
                    
            self.table_change_msg(msg="adding pod_type '" + name + "'  . . . ")
            self.cursor.execute("ALTER TABLE " + self.table + " ADD COLUMN " + pod_type.get_alter_table())
    
            if pod_type.index:
                self.type_add_index(name=name)
                
            if is_new is False:
                # IF NOT NEW, THEN, ADD COLUMN TO DATABASE
                self.cursor.execute("SELECT fid,value FROM " + self.table_dict + " WHERE key=?", (name,))                          
                # NOW, COPY THE NEW VALUE FROM THE inst.__dict__ TO THE COLUMN . . . 
                # Just note, on pod_type.dump call, you only need to provide 'value' since this is a copy and the db.mutables
                # stack will not need updating . . . 
                self.cursor.executemany("UPDATE " + self.table + " SET " + name + "=? WHERE id=?", [(pod_type.dump(value = self.cursor.pickle_load(row[1])), row[0]) for row in self.cursor.fetchall()])
                self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE key=?", (name,))
                                    
            # And finally, store new pod_types to database 
            self.cursor.table_state_set()
     
        def type_add_index(self, name, unique=False):
            unique = "" if unique is False else "UNIQUE "
            self.table_change_msg(msg="adding " + unique.lower() + "index '" + name + "'  . . . ")
            self.cursor.execute("CREATE " + unique + "INDEX IF NOT EXISTS " + self.table + "_pin_" + name + " ON " + self.table + " (" + name + ")")
                    
        def type_drop_index(self, name):        
            self.table_change_msg(msg="dropping index '" + name + "'  . . . ")
            self.cursor.execute("DROP INDEX IF EXISTS " + self.table + "_pin_" + name)
                   
        def type_get_current_db_pod_types(self):            
            self.cursor.execute("PRAGMA table_info(" + self.table + ")")
            return [str(col[1]) for col in self.cursor.fetchall() if str(col[1]) != 'id']
        
        def type_get_current_table_indexes(self):
            self.cursor.execute("PRAGMA index_list(" + self.table + ")")
            return [str(col[1]).replace(self.table + "_pin_", "") for col in self.cursor.fetchall()]

        def type_get_current_table_dict_indexes(self):
            self.cursor.execute("PRAGMA index_list(" + self.table_dict + ")")
            return [str(col[1]).replace(self.table + "_pin_", "") for col in self.cursor.fetchall()]
                                                   
        """ instance methods """
        def inst_new(self, inst=None, kwargs=None):
                
            # This is for special pod_type types (like pod_type.TimeCreate) which want to do something on create . . 
            for pod_type in set(self.type_callbacks_create) | set(self.type_callbacks_load):
                inst, kwargs = pod_type.on_inst_create(inst=inst, kwargs=kwargs)
                   
            typed_values    = {}
            dynamic_values = {}
           
            if kwargs is not None:
                object.__getattribute__(inst, '__dict__').update(kwargs)  # This sets the objects dict
                for key, value in kwargs.iteritems():
                    if key in self.typed_group:
                        typed_values[key] = self.typed_group[key].dump(value = value, inst = inst)
                    else:
                        dynamic_values[key] = self.cursor.pickle_dump(value = value, inst = inst, attr = key)
    
            inst_id = self.cursor.insert_object(values = typed_values)
            self.cursor.add_many_kvargs(values = dynamic_values, inst_id = inst_id)
     
            object.__setattr__(inst, 'id', inst_id)                                  
            self.cache[inst_id] = inst
                                        
            object.__getattribute__(inst, 'on_new_or_load_from_db')()
            
            #Then, add it to the list of 'fully loaded' instances 
            self.fulls.add(inst)
            
            return inst
                
        def inst_update_dict(self, inst, kwargs):
            
            object.__getattribute__(inst, '__dict__').update(kwargs)
            
            type_attrs = ""
            type_values = []
            nom_values = []
            id = inst.id         
               
            for key, value in kwargs.items():
                self.__setattr__(key, value)
                if key in self.typed_group:
                    type_attrs += key + '=?,'
                    type_values.append(self.typed_group[key].dump(value = value, inst = inst))
                else:
                    nom_values.append((id, key,self.cursor.pickle_dump(value = value, inst = inst, attr = key),))

            if len(type_values) > 0:
                type_values.append(id)
                self.cursor.execute('UPDATE ' + self.table + ' SET ' + type_attrs[:-1] + ' WHERE id=?', type_values)
 
            if len(nom_values) > 0:
                self.cursor.executemany('INSERT OR REPLACE INTO ' + self.table_dict + ' (fid,key,value) VALUES (?,?,?)', nom_values)                    
                      
        def inst_get_inst_by_id(self, inst_id, zombie=True):
            
            if inst_id in self.cache:
                return self.cache[inst_id]                
            else:
                inst = self.cls.__new__(self.cls)
                if zombie:
                    self.zombies.add(inst)
                object.__setattr__(inst, 'id', inst_id)
                object.__getattribute__(inst, 'on_new_or_load_from_db')()
                object.__getattribute__(inst, 'on_load_from_db')()
                self.cache[inst_id] = inst
                for pod_type in self.type_callbacks_load:
                    inst = pod_type.on_inst_load(inst=inst)
                return inst
        
        def inst_load_attr_from_db(self, inst, attr):
            
            if attr in self.typed_group:
                self.cursor.execute("SELECT " + attr + " FROM " + self.table + " WHERE id=?", (object.__getattribute__(inst, 'id'),))
                row = self.cursor.fetchone()
                if row:
                    self.zombies.discard(inst)
                    object.__setattr__(inst, attr, self.typed_group[attr].load(row[0]))                    
                else:
                    raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " had been deleted . .  ."
            else:
                self.cursor.execute("SELECT value FROM " + self.table_dict + " WHERE fid=? AND key=?", (object.__getattribute__(inst, 'id'), attr,))
                row = self.cursor.fetchone()
                if row:
                    self.zombies.discard(inst)
                    object.__setattr__(inst, attr, self.cursor.pickle_load(value = row[0], inst = inst, attr = attr))
                else:
                    self.inst_check_if_exists(inst)

        def inst_set_attr(self, inst, attr, value):
            if attr in Meta.POD_SETI_SET:
                raise PodObjectError, "You cannot set attr '" + attr + "' of a pod object . . ."
            if self.inst_check_if_exists(inst):
                object.__setattr__(inst, attr, value)         
                self.inst_save_attr_to_db(inst, attr, value)
        
        def inst_save_attr_to_db(self, inst, attr, value):
            if attr in self.typed_group:
                self.cursor.execute('UPDATE ' + self.table + ' SET ' + attr + '=? WHERE id=?', (self.typed_group[attr].dump(value = value, inst = inst), inst.id,))
            else:
                self.cursor.execute('INSERT OR REPLACE INTO ' + self.table_dict + ' (fid,key,value) VALUES (?,?,?)', (inst.id, attr, self.cursor.pickle_dump(value = value, inst = inst, attr = attr),))                    
                
        def inst_del_attr(self, inst, attr):
            # If the attribute is in inst's pod_types, you can't really delete it -- just set it to None (since the pod_type will have NULL)
            # If not in pod_type group, then delete it from the table. 
            
            id = object.__getattribute__(inst, 'id')
                        
            if attr in self.typed_group:
                self.cursor.execute('UPDATE ' + self.table + ' SET ' + attr + '=? WHERE id=?', (None,id,))
                object.__setattr__(inst, attr, None)
            else:
                self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=? AND key=?", (id, attr,))  
                dict = object.__getattribute__(inst, '__dict__')
                if attr in dict:
                    del dict[attr]
                                            
        def inst_delete(self, inst):
            object.__getattribute__(inst, 'pre_delete')()
            id = object.__getattribute__(inst, 'id')
            self.cursor.execute("DELETE FROM " + self.table + " WHERE id=?", (id,))
            self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=?", (id,))
            if inst in self.db.mutables:
                del self.db.mutables[inst]
            # THEN, MAKE IT A DELETED OBJECT()
            object.__setattr__(inst, '__class__', Deleted)
            object.__setattr__(inst, '__dict__', {})
            return None

        def inst_full_load(self, inst):                    
            if inst not in self.fulls:
                cursor    = self.cursor
                id        = object.__getattribute__(inst, 'id')
                inst_dict = object.__getattribute__(inst, '__dict__')
                pod_types = [pod_type for pod_type in self.typed_group.keys() if pod_type not in inst_dict]
                cursor.execute("SELECT " + ",".join(['id'] + pod_types) + " FROM " + self.table + " WHERE id=?", (id,))
                row = cursor.fetchone()
                if row:
                    self.zombies.discard(inst)
                    self.fulls.add(inst)
                    for i, name in enumerate(pod_types):
                        object.__setattr__(inst, name, self.typed_group[name].load(row[i+1]))
                    cursor.execute("SELECT key,value FROM " + self.table_dict + " WHERE fid=?", (id,))
                    rows = cursor.fetchall()
                    for kv in rows:
                        if kv[0] not in inst_dict:
                            object.__setattr__(inst, kv[0], self.cursor.pickle_load(value = kv[1], inst = inst, attr = kv[0]))               
                else:
                    raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " had been deleted . .  ."
          
        def inst_clear_all(self, inst):
            id = object.__getattribute__(inst, 'id')
            sets = ""
            args = []
            new_dict = {'id': id}
            for type in self.typed_group.keys():
                sets += type + '=?,'
                args.append(None)
                new_dict[type] = None
                    
            if len(args) > 0:
                args.append(id)
                self.cursor.execute('UPDATE ' + self.table + ' SET ' + sets[:-1] + ' WHERE id=?', args)
            
            self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=?", (id,))
            
            object.__setattr__(inst, '__dict__', new_dict)
            
        def inst_len(self, inst, id = False):
            if inst in self.fulls:
                return len(object.__getattribute__(inst,'__dict__')) - (0 if id else 1)
            else:
                return len(self.typed_group) + self.cursor.execute('SELECT COUNT(rowid) FROM ' + self.table_dict + ' WHERE fid=?', (object.__getattribute__(inst,'id'),)).fetchone()[0] + (1 if id else 0)
            
        def inst_contains(self, inst, key):
            if inst in self.fulls:
                return key in object.__getattribute__(inst,'__dict__')
            else:
                if key in self.typed_group:
                    return True
                else:
                    return bool(self.cursor.execute('SELECT COUNT(rowid) FROM ' + self.table_dict + ' WHERE fid=? AND key=?', (object.__getattribute__(inst,'id'),key,)).fetchone()[0])
                    
        def inst_check_if_exists(self, inst, error = True):
            if inst not in self.zombies:
                return True
            else:
                self.cursor.execute("SELECT id FROM " + self.table + " WHERE id=?", (object.__getattribute__(inst, 'id'),))
                row = self.cursor.fetchone()
                if row:
                    self.zombies.discard(inst)
                elif error:
                    raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " has been deleted . .  ."

    class PodNoDatabase(object):
        
        def __getattribute__(self, key):
            if key == 'attach_to_db':
                object.__setattr__(self, '__class__', type.__getattribute__(object.__getattribute__(self, 'cls'), 'Pod'))
                return object.__getattribute__(self, key)
            elif key in ['id', 'child_pods']:
                return object.__getattribute__(self, key)
            else:
                raise PodNoDatabaseError, "You have not connected the class '" + str(object.__getattribute__(self, 'cls')) + "' to any database . . . "
            
        def __setattr__(self, key, value):
            raise PodNoDatabaseError, "You have not connected the class '" + str(object.__getattribute__(self, 'cls')) + "' to any database . . . "
        
    class Where(object):
        
        def __init__(self, cls_pod):
            self.cls_pod = cls_pod
        
        def __getattr__(self, key):
            if key in self.cls_pod.typed_group:
                return self.cls_pod.typed_group[key]
            else:
                return typed.Dynamic(cls_pod=self.cls_pod, name=key)  
              
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
##
##   Object: THE OBJECT IN P'O'D
##
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class PodObjectError(exceptions.BaseException):
    pass

class PodObjectDeleted(exceptions.BaseException):
    pass

class PodObjectUndefined(exceptions.BaseException):
    pass

class Object(object):

    __metaclass__ = Meta
    
    def __init__(self, **kwargs):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_new(inst=self, kwargs=kwargs)

    def __getattribute__(self, attr):  
        
        dict = object.__getattribute__(self, '__dict__')
        
        if attr in dict:
            value = dict[attr]
        elif attr == '__dict__':
            return dict
        else:
            cls_pod = type.__getattribute__(object.__getattribute__(self, '__class__'), 'pod')            
            if attr in cls_pod.typed_group:
                cls_pod.inst_load_attr_from_db(self, attr)
                value = dict[attr]
            else:
                return object.__getattribute__(self, attr)  # This, then, will call __getattr__ on fail and try to load from database . . . '
                    
        return value
                  
    def __getattr__(self, attr):
        dict = object.__getattribute__(self, '__dict__')
        cls_pod = object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod')            
        cls_pod.inst_load_attr_from_db(self, attr)
        if attr in dict:
            return dict[attr]
        else:
            raise AttributeError, "'" + self.__class__.__name__ + "' object has no attribute '" + attr + "'"
                            
    def __setattr__(self, attr, value): 
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_set_attr(self, attr, value)
    
    def __delattr__(self, attr):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_del_attr(self, attr)
        
    def delete(self):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_delete(self)
    
    def full_load(self):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        
    def get_full_id(self):
        return str(type.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').id) + ":" + str(object.__getattribute__(self, 'id')) 

    def set_many(self, **kwargs):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_update_dict(self, kwargs)

    def update(self, other):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_update_dict(self, other)

    """ pass through convenience functions """
    def on_new_or_load_from_db(self):
        pass

    def on_load_from_db(self):
        pass
    
    def pre_delete(self):
        pass
              
    """ dictionary interface """
    def __len__(self, id = False):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_len(self, id = False)

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        return object.__getattribute__(self, '__setattr__')(key, value)

    def __contains__(self, key):
        return object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_contains(inst = self, key = key)

    def __iter__(self):
        return self.iterkeys(id = False)
    
    def clear(self):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_clear_all(self)
         
    def copy(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        new_dict = object.__getattribute__(self, '__dict__').copy()
        if id is False:
            del new_dict['id']
        return new_dict

    def get(self, key, default = None):
        return getattr(self, key, default)
    
    def setdefault(self, key, default):
        try:
            return getattr(self, key)
        except AttributeError:
            object.__getattribute__(self, '__setattr__')(key, default)
            return default
        
    def keys(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        return [key for key in object.__getattribute__(self, '__dict__').iterkeys() if key != 'id' or id]
    
    def iterkeys(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        return (key for key in object.__getattribute__(self, '__dict__').iterkeys() if key != 'id' or id)

    def values(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        return [value for key,value in object.__getattribute__(self, '__dict__').iteritems() if key != 'id' or id]
    
    def itervalues(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        return (value for key,value in object.__getattribute__(self, '__dict__').iteritems() if key != 'id' or id)
    
    def items(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        return [(key,value) for key,value in object.__getattribute__(self, '__dict__').iteritems() if key != 'id' or id]
    
    def iteritems(self, id = False):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_full_load(self)
        return ((key,value) for key,value in object.__getattribute__(self, '__dict__').iteritems() if key != 'id' or id)
               
class Undefined(Object):
    
    POD_GETA_SET = set(['__class__', '__init__', '__reduce__', '__reduce_ex__', 'get_full_id'])
    
    def __init__(self, id, cache):
        object.__setattr__(self, 'id',    id)
        object.__setattr__(self, 'cache', cache)
        
    def get_full_id(self):
        id = object.__getattribute__(self, 'id')
        return str(id[0]) + ":" + str(id[1])

    def __getattribute__(self, key):
        if key in Undefined.POD_GETA_SET:
            return object.__getattribute__(self, key)
        else:
            object.__getattribute__(self, 'try_to_activate_class')(key)
            # The above function changes the class, preventing an infinite loop
            return getattr(self, key)

    def __setattr__(self, key, value):
        object.__getattribute__(self, 'try_to_activate_class')(key)
        self.__setattr__(key, value)
    
    def try_to_activate_class(self, key):
        id    = object.__getattribute__(self, 'id')
        cache = object.__getattribute__(self, 'cache')        
        cls_id, inst_id = id[0], id[1]
        if cls_id in cache.class_pods:
            cls_pod = cache.class_pods[cls_id]
            inst_id = id[1]
            object.__setattr__(self, '__class__', cls_pod.cls)
            object.__setattr__(self, 'id', inst_id)
            object.__delattr__(self, 'cache')
            cls_pod.cache[inst_id] = self
        else:
            raise PodObjectUndefined, "You tried to access attr '" + key + "' on a pod.Undefined of class type -- this means the class was not loaded at import time. . . "
        
""" Things you don't want to save """
class NoSave(object):
    
    def get_full_id(self):
        return "0:0"
  
class Deleted(NoSave):
    
    
    def get_full_id(self):
        return "0:0"

    def __getattribute__(self, key):
        raise PodObjectDeleted, "You tried to get attr '" + key + "' on a pod.Deleted object -- this means that this is a reference to an object that was deleted . . . "
    
    def __setattr__(self, key, value):
        raise PodObjectDeleted, "You tried to set attr '" + key + "' on a pod.Deleted object -- this means that this is a reference to an object that was deleted . . . "


