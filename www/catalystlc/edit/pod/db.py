import os
import sqlite3
import time
import exceptions

#import pickle as cPickle
import cPickle
import StringIO

class current:
    db   = None
    cache = None
    
def is_connected():
    if current.db:
        return current.db.is_connected()
    else:
        return False

""" You need to import core AFTER the external methods for db are defined """

import core

class PodDbError(exceptions.BaseException):
    pass

class PodClassUndefined(exceptions.BaseException):
    pass

class Db(object):
    
    def __init__(self, file, remove = False, clear = False, connect = True, chatty = False, very_chatty = False, use_full_table_name = True):
    
        current.db = self
        
        # SETTINGS
        self.chatty      = chatty if very_chatty is False else True
        self.very_chatty = very_chatty
        # Can also be set in the class header under POD_USE_FULL_TABLE_NAME
        self.use_full_table_name = use_full_table_name   

        self.file       = file
        
        self.dirty      = {}
        
        if remove:    
            self.remove()
        
        self.cache      = Cache(db = self)
        self.pickler    = Pickler(db = self)
        
        if self.file and connect:
            self.connect()
        else:
            self.connection = None
            self.cursor     = None    
                
        if clear: 
            self.clear()
            
        self.create_base_tables()
        
    def __getattr__(self, key):
        if key == 'store':
            self.store = Store(db = self)
            return self.store
        else:
            raise AttributeError, key 
           
    def create_base_tables(self):
        # This was moved to seperate function inorder not to conflict with clear . . . 
        self.execute("CREATE TABLE IF NOT EXISTS pod_classes (id INTEGER PRIMARY KEY AUTOINCREMENT, cls_name TEXT UNIQUE, ctime INTEGER, mtime INTEGER, columns BINARY)")
        self.execute("CREATE UNIQUE INDEX IF NOT EXISTS _cls_name_index ON pod_classes (cls_name)")
            
    def connect(self):
        current.db        = self
        self.connection   = sqlite3.connect(self.file)
        if self.very_chatty:
            self.cursor       = Cursor(db = self) 
        else:
            self.cursor = self.connection.cursor()
        
    def remove(self):
        if self.is_connected():
            self.connection.close()
        if 'file' in self.__dict__ and os.path.isfile(self.file):
            os.remove(self.file)
    
    def clear(self):
        if self.chatty:
            print '*** Clearing database     ***'
        tables = [str(table[0]) for table in self.execute(query = 'select name from sqlite_master where type = ?', args = ('table',))]
        for table in tables:   
            if table != 'sqlite_sequence':
                if self.chatty:
                    print 'Clearing . . . dropping table ' + table
                self.execute(query = 'DROP TABLE ' + table)    
        self.commit(clear_cache = True, close = False)     
        self.vacuum()
        if self.chatty:
            print '*** End clearing database ***\n\n'

    def is_connected(self):
        return getattr(self, 'connection', None) is not None
                 
    def commit(self, clear_cache = False, close = False):
        
        if getattr(self, 'time_stamp', None):
            self.time_stamp.set_time()

        dump = self.pickler.dump
        
        col_commits = {}
        reg_commits = []
        for cls_pod,insts in self.dirty.iteritems():
            # CLASS LOOP
            column_group         = cls_pod.column_group
            column_group_set     = set(column_group.keys())
            column_stand_set     = column_group_set | set(['_pod_exists', 'id'])
            column_callbacks_mod = cls_pod.column_callbacks_mod
            for inst,attrs in insts.iteritems():
                # INSTANCE LOOP
                object.__getattribute__(inst, 'pre_save')()
                for column in column_callbacks_mod:
                    column.on_inst_mod(inst)                
                dict = object.__getattribute__(inst, '__dict__')
                dict_keys = set(dict.keys())
                id   = dict['id']
                col_attrs = dict_keys & column_group_set 
                reg_attrs = dict_keys - column_stand_set
                if len(col_attrs) > 0:
                    sql = ",".join([attr + "=?" for attr in col_attrs])
                    col_commits.setdefault(sql,[]).append([column_group[attr].dump(dict[attr]) for attr in col_attrs] + [id])
                if len(reg_attrs) > 0:
                    reg_commits += [(id,attr,dump(dict[attr])) for attr in reg_attrs]
            # BACK TO CLASS LOOP
            for sql,args in col_commits.iteritems():
                self.cursor.executemany("UPDATE " + cls_pod.table + " SET " + sql + " WHERE id=?", args)
            if len(reg_commits) > 0:
                self.executemany("INSERT OR REPLACE INTO " + cls_pod.table_dict + " (fid,key,value) VALUES (?,?,?)", reg_commits)        
            col_commits.clear()
            del reg_commits[:]
            insts.clear()
        self.dirty.clear()
                
        self.connection.commit()
    
        if clear_cache:
            self.cache.clear_cache()
        
        if close:
            self.connection.close()
            
    def cancel(self, clear_cache = True, close = False):
        
        for cls_pod,insts in self.dirty.iteritems():
            for inst,attrs in insts.iteritems():
                object.__getattribute__(inst, 'pre_cancel')()
                for attr in attrs:
                    del inst.__dict__[attr]
                attrs.clear()
            insts.clear()
        self.dirty.clear()
    
        self.connection.rollback()
        
        if clear_cache:
            self.cache.clear_cache()
        
        if close:
            self.connection.close()
        
                                     
    def vacuum(self):
        self.execute('VACUUM')
        
    def get_new_cursor(self):
        return Cursor(db = self)
        
    # Cursor passthroughs . . . 
    
    def execute(self, query, args = ()):
        return self.cursor.execute(query, args)
    
    def executemany(self, query, seq_of_args):
        return self.cursor.executemany(query, seq_of_args)
        
class Pickler:
    
    def __init__(self, db):
        self.db   = db
        self.cache = db.cache
         
    @staticmethod
    def dump(value):    
        return sqlite3.Binary(cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL))

    def load(self, value):
        current.cache = self.cache     # This set the current cache so the unpickler core.handle_unreduce knows which cache to grab the attribute from . . . 
        return cPickle.loads(str(value))
    
class Cursor(object):

    def __init__(self, db):
        self.db = db
        self.very_chatty = db.very_chatty
        self.cursor = db.connection.cursor()

    def __iter__(self):
        return self.cursor.__iter__()

    def __getattr__(self, attr):
        return self.cursor.__getattribute__(attr)

    def execute(self, query, args = ()):
        if self.very_chatty:
            self._sql_count = getattr(self, '_sql_count', -1) + 1
            print "\tSQL COMMAND #" + str(self._sql_count) + ": \t" + query
            print "\tSQL VALUES:  \t\t" + str(args) + '\n'
        return self.cursor.execute(query, args)
    
    def executemany(self, query, seq_of_args):
        if self.very_chatty:
            self._sql_count = getattr(self, '_sql_count', -1) + 1
            print "\tSQL COMMAND #" + str(self._sql_count) + ": \t" + query
            print "\tSQL VALUES:  \t\t" + str(seq_of_args) + '\n'
        return self.cursor.executemany(query, seq_of_args)
        
class Cache(object):
    
    def __init__(self, db):
        
        self.db          = db        
        self.classes     = {}

    def get_inst(self, cls_id, inst_id, exists = None): 

        cls = self.classes.get(cls_id, None)
        
        if cls is None:
            return core.Undefined(id = (cls_id, inst_id))
        else:
            return cls.pod.inst_get_inst_by_id(cls = cls, inst_id = inst_id, exists = exists)
    
    def clear_cache(self):            
        for cls in self.classes.itervalues():
            cls.pod.cache.clear()
    

      
""" STORE """  
class Store(object):
    
    def __init__(self, db, prefix = "pod_db_store_"):
        object.__setattr__(self, 'db', db)
        object.__setattr__(self, 'prefix', prefix)
        
        self.db.execute("CREATE TABLE IF NOT EXISTS pod_store_all (key_name TEXT UNIQUE PRIMARY KEY, value BINARY)")
        self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS _key_name_index ON pod_store_all (key_name)")

    def __getitem__(self, key):
        result = self.db.execute(query = "SELECT value FROM pod_store_all WHERE key_name=?", args = (self.prefix + key,)).fetchall()
        if len(result) == 1:
            return self.db.pickler.load(result[0][0])
        else:
            raise PodDbError, "The key '" + key + "' was not found in the database store all . . . "

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key, value):
        self.db.execute(query = "INSERT OR REPLACE INTO pod_store_all (key_name,value) VALUES (?,?)", args = (self.prefix + key, self.db.pickler.dump(value),))
        
    def __setattr__(self, key, value):
        return self.__setitem__(key, value)     

