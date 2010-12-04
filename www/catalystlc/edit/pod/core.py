import os
import sys
import time
import exceptions
import warnings
import inspect

import db
from column import Column, Int, Query

PY_VERSION_IS_25 = sys.version[0:3] == '2.5'

class PodMetaError(exceptions.BaseException):
    pass

class Meta(type):
    
    def __init__(cls, name, bases, dict):      
        
        if cls.__module__ == Meta.__module__:
            # We don't want to create tables and so on for the base classes defined in this module.
            return

        if len(bases) > 1:
            raise PodMetaError, "Currently, pod does not support multiple inheritance . . . "
                
        if 'id' in dict:
            raise PodMetaError, "'id' is a reserved class variable and cannot be defined in class " + str(cls)
            
        if db.is_connected() is False:
            warnings.warn("pod.Object " + name + " created but no pod database found -- data will not be saved!")
            return
          
        type.__setattr__(cls, 'pod', type(cls).Pod(cls         = cls, 
                                                   name        = name, 
                                                   parent      = bases[0] if bases[0] is not Object else None)
                        )

        cls.pod.onload()
               
    def __getattribute__(cls, key):
        if key in ['__new__', '__instancecheck__', 'pod'] or key in type.__getattribute__(cls, '__dict__'):
            return type.__getattribute__(cls, key)     
        elif key == 'store':
            store = db.Store(db = cls.pod.db, prefix = cls.pod.table + '_store_')
            type.__setattr__(cls, 'store', store)
            return store
        elif key == 'id':
            id = Int(index = False, cls = cls, db = cls.pod.db, name = 'id')
            type.__setattr__(cls, 'id', id)
            return id
        else:
            return type.__getattribute__(cls, key)
  
    def __setattr__(cls, key, value):
        
        # Here, __setattr__ is only performing error checking because dynamic creation of columns has been removed . . . 
        
        if key == 'pod':
            raise PodMetaError, "Key '" + key + "' is a reserved attribute of pod classes . . . "
        
        if isinstance(value, Column):
            raise PodMetaError, "You cannot create a column '" + key + "' dynamically -- please add it to the class header . . . "
        
        if isinstance(getattr(cls, key, None), Column):
            raise PodMetaError, "Attr '" + key + "' is of type pod.Column -- you cannot alter this attribute dynamically -- it must be performed in class header . . ."
        
        # Dynamic creation not supported at this time . . .  
        # cls.pod.column_create_after_import(name = key, column = value)
        return type.__setattr__(cls, key, value)
        
    def __iter__(cls):
        return Query(where = cls)
    
    def __getitem__(cls, index):
        
        if isinstance(index, slice):
            if index.step:
                raise PodMetaError, "You cannot include a 'step' parameter when slicing a pod.Object class . . . "
            elif index.start < 0:
                raise PodMetaError, "The index 'start' cannot be less than 0"
            elif index.stop < 0:
                raise PodMetaError, "The index 'stop' cannot be less than 0"
            elif index.stop-index.start < 0:
                raise PodMetaError, "The index 'stop'-'start' cannot be less than zero.  You cannot go backwards through a podObject table."
            else:
                return Query(where = cls, offset = index.start, limit = index.stop-index.start)

        else:
            return type.__getitem__(cls, index)
        
    def execute(cls, query, args = ()):
        return cls.pod.cursor.execute(query.replace("cls_table", cls.pod.table).replace("cls_dict_table", cls.pod.table_dict), args)

    def executemany(cls, query, args = ()):
        return cls.pod.cursor.executemany(query.replace("cls_table", cls.pod.table).replace("cls_dict_table", cls.pod.table_dict), args)
        
    def migrate(cls, new_cls):
        cls.pod.migrate_to_new_cls(new_cls = new_cls)
        
    def drop(cls):
        cls.pod.drop_table()
        
    class Pod(object):
    
        def __init__(self, cls, name, parent):
            # pass ins
            self.cls            = cls
            self.parent         = parent

            # Init vars
            self.column_group            = {}
            self.column_callbacks_create = set()
            self.column_callbacks_mod    = set()
            self.child_classes           = set()  

            # We changed this to only look for column types!
            # self.obj_methods             = set(['__class__'] + [fn_name for fn_name in dir(cls) if inspect.isroutine(getattr(cls, fn_name))])
            
            # Set the db . . . 
            self.db             = db.current.db if parent is None else parent.pod.db
            self.cursor         = self.db.cursor            
            # Use the full name for the class name if either: 
            #  1.  The class has define _POD_FULL_TABLE_NAME = True
            #  2.  Or, the class does not define this variable, but the database has set it True (the default)
            #  Full name is harder to read if working with sql table directly, but uses Hungarian Notation of 
            #  directory _ module _ class it less likely to have a namespace collision. 
            self.table      = self.get_table_name(db = self.db, cls = cls, cls_name = name)
            self.table_dict = self.table + '_kvdict'
            
            # setups 
            self.mtime       = self.get_mtime(source_file = inspect.getsourcefile(cls))
            
        def __getstate__(self):
            raise PodMetaError, "You cannot pickle a Pod CLASS pod._Meta object . . . "
                
        def onload(self):

            # Start the rather complex startup processing . . .

            #
            # STEP 1. Update parent and add parent columns to own local __dict___
            #
            # First, update parent and add any columns a parent has to your local dictionary. 
            # The reason you need a local copy of a column is because if you have a ParentClass, ChildClass and a column called 'name'
            # you want ParentClass.name == 'Fred' to return all objects with a name of 'Fred' but ChildClass.name == 'Fred' to 
            # only return ChildClass object with a name == 'Fred'.  column_add_parents takes care of this . . .
            #
            if self.parent is not None:
                self.parent.pod.child_classes.add(self.cls)
                self.column_add_parents()
                    
            #
            # STEP 2. Try and select row by name from pod_classes table -- if not there, add the table. 
            #
            row = self.cursor.execute("SELECT id,mtime FROM pod_classes WHERE cls_name=(?)", (self.table,)).fetchone()
                
            if row is None:   
                # if row is None, means a new class and a new table needs to be made  
                self.cursor.execute("INSERT INTO pod_classes (cls_name, ctime, mtime) VALUES (?,?,?)", (self.table,self.mtime,self.mtime,))
                self.id = self.cursor.lastrowid
                self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table + " (id INTEGER PRIMARY KEY AUTOINCREMENT)")
                self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table_dict + " (fid INTEGER, key TEXT, value BINARY, PRIMARY KEY (fid, key))")
            else:
                self.id = int(row[0])
            
            #
            # STEP 3. Init cache and add yourself cache.classes.  
            #
            self.db.cache.classes[self.id]     = self.cls
            self.cache                         = {}
            # took this out, undefineds . . . also, check to see if you are in the 'undefineds' cache.  If so, update these instances to cls now that it is defined. 
            #if self.id in self.db.cache.undefineds:    
            #    self.db.cache.instances[self.id] = self.db.cache.undefineds[self.id]
            #    for inst_id,inst in self.db.cache.instances[self.id].iteritems():
            #        self.db.cache._init_inst_from_db(cls = self.cls, inst = inst, inst_id = inst_id)
            #    del self.db.cache.undefineds[self.id]
                  
            # This updates all the columns passed in from the class header. 
            [self.column_create_and_update(name = key, column = value, create = False) for key,value in self.cls.__dict__.iteritems() if isinstance(value, Column)]
                
            #
            # STEP 4. Check if 1) the class is brand new or 2) the mod time has changed.  Update on either condition . . .
            #
            if row is None or (int(row[1]) != self.mtime):
                self.is_new     = row is None
                self.column_check_for_schema_changes()
            else:
                self.is_new     = False
                
        @staticmethod
        def get_table_name(db, cls, cls_name):
            return '_'.join(cls.__module__.split('.') + [cls_name]) if getattr(cls, 'POD_USE_FULL_TABLE_NAME', db.use_full_table_name) else cls_name

        def get_mtime(self, source_file = None):
            return int(os.path.getmtime(source_file)) if source_file else int(time.time())
            
        def column_print_msg(self, msg = None):
            
            if self.db.chatty:
                if 'start_message' not in self.__dict__:
                    self.start_message = "Class '" + self.cls.__name__ + "' needs to be created/updated . . . checking to see if any columns need to be updated:"
                if self.start_message:
                    print self.start_message
                    self.start_message = False
                if msg:
                    print "\tFor class '" + self.cls.__name__ + "' " + msg
            
        def column_check_for_schema_changes(self, copy_dropped_to_dict = True):
            
            if self.db.chatty:
                self.column_print_msg(msg = None)

            old_columns = {} if self.is_new else self.db.pickler.load(self.cursor.execute("SELECT columns FROM pod_classes WHERE id=(?)", (self.id,)).fetchone()[0])
            set_old_columns = set(old_columns.keys())
            
            for name,col in old_columns.iteritems():
                col.update(cls = self.cls, db = self.db, name = name)
            
            if set(self.column_get_current_db_columns()) != set_old_columns:
                raise PodMetaError, "Fatal error -- columns in table are not same as columns in class table . . ."
            
            # All the things that could change: 
            #
            #    What could happen:
            #         1. Drop:         the new_columns might not have a column found in old_columns -->  In this case, drop the old column. 
            #         2. Add:          the new_columns might have a column not found in old_columns -->  In this case, add the new column. 
            #         3. Change Type:  a new_column might have changed type -- in this case, drop and add. 
            #         4. Change Index: the new_columns might have a column whose index is not the same as the old column --> In this case, either add/drop index on that column. 
            #         5. Do nothing!:  a new column and the old column match!!!  YES!!
            #
            #    After this, update the mtime on the class and restore column in the database. 

            set_new_columns = set(self.column_group.keys())
            
            set_changed_type_columns = set([name for name in set_new_columns & set_old_columns if self.column_group[name].__class__ != old_columns[name].__class__])
            
            # You need to drop 1) all columns that changed type and 2) if auto_drop is true, you need to also drop set_old_columns - set_new_columns
            #
            # ** auto_drop no longer supported, so this line has changed
            # set_drop_columns = set_changed_type_columns if self.auto_drop is False else set_changed_type_columns | (set_old_columns - set_new_columns)
            set_drop_columns = set_changed_type_columns | (set_old_columns - set_new_columns)
            set_add_columns = set_changed_type_columns | (set_new_columns - set_old_columns)
                       
            # 1. Drop 
            if len(set_drop_columns) > 0:
                self.column_drop_old(old_columns = old_columns, set_old_columns = set_old_columns, set_drop_columns = set_drop_columns, copy_dropped_to_dict = copy_dropped_to_dict)

            # 2. Add
            for name in set_add_columns:
                self.column_create_and_update(name = name, column = self.column_group[name])

            # 4. Change index
            for new_column, old_column in [(self.column_group[name], old_columns[name]) for name in (set_old_columns & set_new_columns)]:   
                if new_column.index is True and old_column.index is False:
                    self.column_add_index(name = name)
                elif new_column.index is False and old_column.index is True:
                    self.column_drop_index(name = name)
                    
            self.column_commit_to_db()
            
        def column_drop_old(self, old_columns, set_old_columns, set_drop_columns, copy_dropped_to_dict):
            
            set_keep_columns = set_old_columns - set_drop_columns
            self.column_print_msg(msg = "dropping columns " + ",".join(set_drop_columns) + "  . . . ")
            list_keep_columns = list(set_keep_columns)
            list_drop_columns = list(set_drop_columns)

            if copy_dropped_to_dict and len(list_drop_columns) > 0:
                self.cursor.execute("SELECT " + ",".join(['id'] + list_drop_columns) + " FROM " + self.table)
                args = []
                for row in self.cursor.fetchall():
                    for i,col_name in enumerate(list_drop_columns):
                        args.append((row[0], col_name, self.db.pickler.dump(old_columns[col_name].load(row[i+1]))))
                self.cursor.executemany("INSERT OR REPLACE INTO " + self.table_dict + " (fid,key,value) VALUES (?,?,?)", args)

                        
            # Now, put humpty dumpty back together again . . . 
            self.cursor.execute("SELECT " + ",".join(['id'] + list_keep_columns) + " FROM " + self.table)
            rows = self.cursor.fetchall()
                        
            self.cursor.execute("DROP TABLE IF EXISTS " + self.table)                
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table + " (id INTEGER PRIMARY KEY)")
            
            for name in list_keep_columns:
                old_columns[name].update(cls = self.cls, db = self.db, name = name)
                self.column_create_and_update(name = name, column = old_columns[name], is_new = True)
            
            # NOW PUT ALL THE ROWS BACK INTO DB -- HOWEVER, COPY PED COLUMN DATA BACK INTO THE DICT

            names  = '(' + ",".join(['id'] + list_keep_columns) + ')'                
            quest  = '(' + ",".join(["?" for i in range(len(list_keep_columns)+1)]) + ')'
            self.cursor.executemany("INSERT INTO " + self.table + " " + names + " VALUES " + quest, (row[0:len(list_keep_columns)+1] for row in rows))
                
        def column_drop_and_delete_forever(self, column):

            if self.db.chatty:
                print "You have chosen to permentally drop and delete column '" + column.name + "' from '" + self.table + "'.  All data will be lost forever "
                print "Remember!  You have to remove this column from the class header or else it will be added back on next import . . . "
            
            delattr(self.cls, column.name)
            del self.column_group[column.name]
            
            self.column_check_for_schema_changes(copy_dropped_to_dict = False)
            
            for child in self.child_classes:
                child.pod.column_drop_and_delete_forever(child.pod.column_group[column.name])

            # Now you want to resave a local mtime, because we want to reimport the class after this . . . 
            self.column_commit_to_db(mtime = self.get_mtime())
            
        def column_create_and_update(self, name, column, create = True, is_new = None):
                
            self.column_group[name] = column
            column.update(cls = self.cls, name = name, db = self.db)
            
            if create:
                
                # If the column is new, then you don't need to copy all the data from the __dict__ to the new column. 
                is_new = self.is_new if is_new is None else is_new
            
                self.column_print_msg(msg = "adding column '" + name + "'  . . . ")
                self.cursor.execute("ALTER TABLE " + self.table + " ADD COLUMN " + column.get_alter_table())
        
                if column.index:
                    self.column_add_index(name = name)
                    
                if not is_new:
                    # IF NOT NEW, THEN, ADD COLUMN TO DATABASE
                    self.cursor.execute("SELECT fid,value FROM " + self.table_dict + " WHERE key=?", (name,))                          
                    # NOW, COPY THE NEW VALUE FROM THE inst.__dict__ TO THE COLUMN . . . 
                    self.cursor.executemany("UPDATE " + self.table + " SET " + name + "=? WHERE id=?", [(column.dump(self.db.pickler.load(row[1])), row[0]) for row in self.cursor.fetchall()])
                    self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE key=?", (name,))
                                        
                # And finally, store new columns to database 
                self.column_commit_to_db()       
        
        def column_add_index(self, name):
            self.column_print_msg(msg = "adding index '" + name + "'  . . . ")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS " + self.table + "_pin_" + name + " ON " + self.table + " (" + name +")")
                    
        def column_drop_index(self, name):        
            self.column_print_msg(msg = "dropping index '" + name + "'  . . . ")
            self.cursor.execute("DROP INDEX IF EXISTS " + self.table + "_pin_" + name)
        
        def column_add_parents(self):
            for name, column in ((key,value) for key,value in self.parent.__dict__.iteritems() if(isinstance(value, Column))):
                if name in self.cls.__dict__:
                    raise PodMetaError, "Class " + str(self.cls) + " is trying to add column " + name + ", but this column already defined in parent " + str(self.parent) + " . . ."
                else:
                    type.__setattr__(self.cls, name, column.get_deep_copy(cls = self.cls))
                   
        def column_get_current_db_columns(self):            
            self.cursor.execute("PRAGMA table_info(" + self.table + ")")
            return [str(col[1]) for col in self.cursor.fetchall() if str(col[1]) != 'id']
        
        def column_get_current_db_indexes(self):
            self.cursor.execute("PRAGMA index_list(" + self.table + ")")
            return [str(col[1]).replace(self.table + "_pin_", "") for col in self.cursor.fetchall()]
                 
        def column_commit_to_db(self, mtime = None):
            mtime = self.mtime if mtime is None else mtime
            self.cursor.execute("UPDATE pod_classes SET mtime=?,columns=? WHERE id=?", (mtime,self.db.pickler.dump(self.column_group),self.id,))      
            self.db.connection.commit()
                    
        def migrate_to_new_cls(self, new_cls):
            if new_cls.__bases__[0] is not object:
                raise PodMetaError, "The new_cls '" + new_cls.__name__ + "' must descend directly from object (you can change it later to pod.Object, but first migrate the old class over . . . "
            new_cls_name = self.get_table_name(db = self.db, cls = new_cls, cls_name = new_cls.__name__)
            self.cursor.execute("UPDATE pod_classes SET cls_name=? WHERE id=?", (new_cls_name, self.id,))
            self.cursor.execute("ALTER TABLE " + self.table      + " RENAME TO " + new_cls_name)
            self.cursor.execute("ALTER TABLE " + self.table_dict + " RENAME TO " + new_cls_name + '_kvdict')            
            self.db.commit(clear_cache = True, close = True)
              
        def drop_table(self):
            self.cursor.execute("DELETE FROM pod_classes WHERE id=?", (self.id,))
            self.cursor.execute("DROP TABLE IF EXISTS " + self.table)                    
            self.cursor.execute("DROP TABLE IF EXISTS " + self.table_dict)                    
            self.db.commit(clear_cache = True, close = True)
            for child in self.child_classes:
                child.pod.drop_table()
              
        """ instance methods """
        def inst_new(self, cls):

            inst = object.__new__(cls)          
    
            if cls is Object:
                raise PodObjectError, "You cannot create instances of type Object directly."
            
            
            if PY_VERSION_IS_25 or True:
                # There is a bug in the sqlite3 bindings in 2.5.4
                self.cursor.execute("INSERT INTO " + str(self.table) + "(id) VALUES (NULL)")
            else:
                self.cursor.execute("INSERT INTO " + str(self.table) + " DEFAULT VALUES")
                
            inst_id = self.cursor.lastrowid
            object.__setattr__(inst, 'id', inst_id)
            object.__setattr__(inst, '_pod_exists', True)
            
            type.__getattribute__(cls, 'pod').cache[inst_id] = inst
    
            # This is for special column types (like column.TimeCreate) which want to do something on create . . 
            for col in self.column_callbacks_create:
                col.on_inst_create(inst = inst)
                        
            return inst
                  
        def inst_get_inst_by_id(self, cls, inst_id, exists = None):
            if inst_id in self.cache:
                return self.cache[inst_id]                
            else:
                inst = object.__new__(cls)
                object.__setattr__(inst, 'id', inst_id)
                object.__setattr__(inst, '_pod_exists', exists)
                object.__getattribute__(inst, 'on_load_from_db')()
                self.cache[inst_id] = inst
                return inst
        
        def inst_update_dict(self, inst, kwargs):
            self.db.dirty.setdefault(self,{}).setdefault(inst, set()).update(kwargs.keys())
            object.__getattribute__(inst, '__dict__').update(kwargs)
        
        def inst_mark_attr_dirty(self, inst, attr):
            self.db.dirty.setdefault(self,{}).setdefault(inst, set()).add(attr)
                                    
        def inst_load_attr_from_db(self, inst, attr):
            
            if attr in self.column_group:
                self.cursor.execute("SELECT " + attr + " FROM " + self.table + " WHERE id=?",(object.__getattribute__(inst,'id'),))
                row = self.cursor.fetchone()
                if row:
                    object.__setattr__(inst, '_pod_exists', True)
                    object.__setattr__(inst, attr, self.column_group[attr].load(row[0]))                    
                else:
                    raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " had been deleted . .  ."
            else:
                self.cursor.execute("SELECT value FROM " + self.table_dict + " WHERE fid=? AND key=?",(object.__getattribute__(inst,'id'),attr,))
                row = self.cursor.fetchone()
                if row:
                    object.__setattr__(inst, '_pod_exists', True)
                    object.__setattr__(inst, attr, self.db.pickler.load(row[0]))
                else:
                    # Now, you need to check for existence
                    if self.inst_check_if_exists(inst) is False:
                        raise PodObjectDeleted, "The object " + str(inst.inst) + " with id " + inst.get_full_id() + " has been deleted . .  ."

        def inst_set_attr(self, inst, attr, value):
            if attr in ['__class__', 'id']:
                raise PodObjectError, "You cannot set attr '" + attr + "' of a pod object . . ."
            if self.inst_check_if_exists(inst):
                self.inst_mark_attr_dirty(inst,attr)
                return object.__setattr__(inst, attr, value)              
            else:
                raise PodObjectDeleted, "You tried to set an attributed on a deleted pod object '" + inst.get_full_id() + "' . . . "
        
        def inst_del_attr(self, inst, attr):
            # If the attribute is in inst's columns, you can't really delete it -- just set it to None (since the column will have NULL)
            # If not in column group, then delete it from the table. 
            if attr in self.column_group:
                object.__setattr__(inst, attr, None)
                self.inst_mark_attr_dirty(inst,attr)
                return None
            else:
                self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=? AND key=?", (object.__getattribute__(inst,'id'),attr,))
                self.db.dirty.setdefault(self,{}).setdefault(inst, set()).discard(attr)  # Use discard, doesn't throw KeyError
                return object.__delattr__(inst, attr)
                      
        def inst_delete(self, inst):
            object.__getattribute__(inst, 'pre_delete')()
            id = object.__getattribute__(inst,'id')
            self.cursor.execute("DELETE FROM " + self.table      + " WHERE id=?",  (id,))
            self.cursor.execute("DELETE FROM " + self.table_dict + " WHERE fid=?", (id,))
            if id in self.cache:
                del self.cache[id]
            if self in self.db.dirty and inst in self.db.dirty[self]:
                del self.db.dirty[self][inst]
            # THEN, MAKE IT A DELETED OBJECT()
            object.__setattr__(inst, '__class__', Deleted)
            object.__setattr__(inst, '__dict__',  {})
            return None

        def inst_full_load(self, inst):                    
            cursor   = self.cursor
            id       = object.__getattribute__(inst,'id')
            cols     = [col for col in self.column_group.keys()]
            load     = self.db.pickler.load        
            cursor.execute("SELECT " + ",".join(['id'] + cols) + " FROM " + self.table + " WHERE id=?",(id,))
            row = cursor.fetchone()
            if row:
                object.__setattr__(inst, '_pod_exists', True)
                for i,name in enumerate(cols):
                    object.__setattr__(inst, name, self.column_group[name].load(row[i+1]))
                cursor.execute("SELECT key,value FROM " + self.table_dict + " WHERE fid=?",(id,))
                rows = cursor.fetchall()
                for kv in rows:
                    object.__setattr__(inst, kv[0], load(kv[1]))               
            else:
                raise PodObjectDeleted, "The object " + str(inst) + " with id " + inst.get_full_id() + " had been deleted . .  ."
          
        def inst_check_if_exists(self, inst):
            pod_exists = object.__getattribute__(inst, '_pod_exists')
            if pod_exists is None:
                self.cursor.execute("SELECT id FROM " + self.table + " WHERE id=?",(object.__getattribute__(inst,'id'),))
                row = self.cursor.fetchone()
                if row:
                    object.__setattr__(inst, '_pod_exists', True)
                    return True
                else:
                    object.__setattr__(inst, '_pod_exists', False)
                    return False
            else:
                return pod_exists
        
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
    
    def __new__(cls, **kwargs):
        return type.__getattribute__(cls, 'pod').inst_new(cls)
            
    def __init__(self, **kwargs):
        object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_update_dict(self, kwargs)

    def __reduce__(self):
        return handle_unreduce, (object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').id, object.__getattribute__(self, 'id'))
        
    def __getattribute__(self, attr):  
        
        dict = object.__getattribute__(self, '__dict__')
        
        if attr in dict:
            value = dict[attr]
        elif attr == '__dict__':
            return dict
        else:
            cls_pod = object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod')            
            if attr in cls_pod.column_group:
                cls_pod.inst_load_attr_from_db(self, attr)
                value = dict[attr]
            else:
                return object.__getattribute__(self, attr)  # This, then, will call __getattr__ on fail and try to load from database . . . 

        if value is not None and not isinstance(value, (Object, str, int, float, bool, long, complex, tuple, frozenset)):
            object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').inst_mark_attr_dirty(self, attr)
        
        return value
                  
    def __getattr__(self, attr):
        
        dict = object.__getattribute__(self, '__dict__')
        cls_pod = object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod')            
        cls_pod.inst_load_attr_from_db(self, attr)
        if attr in dict:
            value = dict[attr]
            if value is not None and not isinstance(value, (Object, str, bool, int, float, long, complex, tuple, frozenset)):
                cls_pod.inst_mark_attr_dirty(self, attr)
            return value
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
        return str(object.__getattribute__(object.__getattribute__(self, '__class__'), 'pod').id) + ":" + str(object.__getattribute__(self, 'id')) 

    """ pass through convenience functions """
    def on_load_from_db(self):
        pass
        
    def pre_save(self):
        pass
    
    def pre_cancel(self):
        pass
    
    def pre_delete(self):
        pass
               
class NoSave(object):
    
    def __reduce__(self):
        return handle_nosave, ()
  
class Deleted(NoSave):
    
    def __getattr__(self, key):
        raise PodObjectUndefined, "You tried to get attr '" + key + "' on a pod.Deleted object -- this means that this is a reference to an object that was deleted . . . "
    
    def __setattr__(self, key, value):
        raise PodObjectUndefined, "You tried to set attr '" + key + "' on a pod.Deleted object -- this means that this is a reference to an object that was deleted . . . "

class Undefined(object):
    
    def __init__(self, id):
        object.__setattr__(self, 'id', id)
        
    def __reduce__(self):
        return handle_unreduce, object.__getattribute__(self, 'id')
    
    def get_full_id(self):
        return str(self.id[0]) + ":" + str(self.id[1])

    def __getattr__(self, key):
        raise PodObjectUndefined, "You tried to get attr '" + key + "' on a pod.Undefined object -- this means the class was not loaded at import time. . . "
    
    def __setattr__(self, key, value):
        raise PodObjectUndefined, "You tried to set attr '" + key + "' on a pod.Undefined object -- this means the class was not loaded at import time . . . "


    
""" These methods handle unpickling """
def handle_unreduce(*args):
    return db.current.cache.get_inst(cls_id = args[0], inst_id = args[1])

def handle_nosave(*args):
    return None


