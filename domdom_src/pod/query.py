import exceptions

try:
    import sqlite3
except:
    from pysqlite import dbapi2 as sqlite3

import core

""" ############################################################################################
###
###    THE QUERY 
###
""" ############################################################################################
    
class PodQueryError(exceptions.BaseException):
    pass
                
class Query(object):

    def __init__(self, select = None, where = None, order_by = None, offset = None, limit = None, child_classes = True):

        self.select        = select
        self.where         = where
        self.order_by      = order_by
        self.limit         = limit
        self.offset        = offset
        # Other flags . . . 
        self.child_classes = child_classes
        self.db            = None
    
    def __iter__(self):
        return QueryIterator(query = self)
    
    def get_sql_setup(self):
        
        if isinstance(self.where, core.Meta):
            cls_pod = type.__getattribute__(self.where, 'pod')
            where = None
        elif self.where:
            self.where.get_sql(full_name = False, type = 'where')
            if len(self.where.class_pods) > 1:
                raise PodQueryError, "You cannot mix class types in a pod.Query where statement -- use pod.RawQuery instead . . . "
            cls_pod = self.where.class_pods.pop()
            where = self.where
        else:
            raise PodQueryError, "Improper where statement . . ."

        self.db              = cls_pod.db
        self.class_pod_list  = self.get_class_list(cls_pod = cls_pod, list = [])
        
        return cls_pod,where
        
    def get_sql(self):

        if self.select:
            self.select.get_sql(full_name = False)
            if len(self.select.class_pods) > 1:
                raise PodQueryError, "You cannot mix class types in a pod.Query select statement -- use pod.RawQuery instead . . . "
        
        if self.where is None:
            self.where = [class_pod for class_pod in self.select.class_pods][0].cls
        
        cls_pod,where = self.get_sql_setup()
                    
        if self.order_by:
            self.order_by.get_sql(full_name = False)

        sql,values = "",[]

        for i,cls_pod in enumerate(self.class_pod_list):
                        
            if i > 0:
                sql += " UNION " 

            sql += "SELECT " + str(i) + " AS PODCLASS,id"
            
            if self.select:
                sql    += "," + self.select.expression
                if len(self.select.args) > 0:
                    raise PodQueryError, "You cannot do any processing within a pod.Query select statement -- use pod.RawQuery instead . . . "
                values += self.select.args
                
            sql += " FROM " + cls_pod.table
            
            if where:
                sql    += " WHERE " + where.expression.replace('%kvdict%', cls_pod.table_dict) 
                values += where.args
            
        if len(sql) > 2 and self.order_by is not None:
            sql += " ORDER BY " + self.order_by.expression
                
        if len(sql) > 2 and self.limit is not None:
            sql += " LIMIT " + str(self.limit)

        if len(sql) > 2 and self.offset is not None:
            sql += " OFFSET " + str(self.offset)

        return sql,values
            
    def get_class_list(self, cls_pod, list):
        
        if cls_pod.id is not None:
            list.append(cls_pod)
        
        if self.child_classes:
            for new_cls_pod in cls_pod.child_pods:
                list = self.get_class_list(cls_pod = new_cls_pod, list = list)
            
        return list
     
    """ 
    API
    """
    def get_one(self, error_on_multiple = True):
        objects = [object for object in self]
        if len(objects) == 0:
            return None
        else:
            if error_on_multiple and len(objects) > 1:
                raise PodQueryError, "More than one object returned . . . "
            return objects[0]
            
    def delete(self):
        cls_pod,where = self.get_sql_setup()
        
        for i,cls_pod in enumerate(self.class_pod_list):
            if where:
                ids    = [(row[0],) for row in cls_pod.cursor.execute('SELECT id FROM ' + cls_pod.table + ' WHERE ' + where.expression.replace('%kvdict%', cls_pod.table_dict), where.args)]
                cls_pod.cursor.execute("DELETE FROM " + cls_pod.table + " WHERE " + where.expression.replace('%kvdict%', cls_pod.table_dict), where.args)
                cls_pod.cursor.executemany("DELETE FROM " + cls_pod.table_dict + " WHERE fid=?", ids)
                   
class QueryIterator(object):
    
    def __init__(self, query):
        
        self.query = query
        sql,values = query.get_sql()  
        
        # TODO: we need to check out this row factory business
        # If we have two nested loops, one regular and one raw, do they confilct?
        # this only affects nested RawQuery objects . . . 
        query.db.connection.row_factory = None
                
        if query.db.very_chatty:
            self.current_cursor = query.db.get_new_cursor()
        else:
            self.current_cursor = query.db.connection.cursor()
                
        self.current_cursor.execute(sql, values)
        if self.current_cursor.description:
            pod_types = [desc[0] for desc in self.current_cursor.description][2:]
            if len(pod_types) > 0:
                self.returned_pod_types = []
                for i,cls_pod in enumerate(query.class_pod_list):
                    self.returned_pod_types.append([])
                    for j,col in enumerate(pod_types):
                        if col in cls_pod.typed_group:
                            self.returned_pod_types[i].append((j+2,col, cls_pod.typed_group[col]))   # Duck typing: both pod_types and pickler support 'load' method
                        else:
                            # This is where we check that the pod_types are right!
                            raise PodQueryError, "You asked for pod_type '" + col + "' but it is not a defined pod.pod_type . . . "
            else:
                self.returned_pod_types = None    
    def next(self):
        row     = self.current_cursor.next()
        cls_num = row[0]
        cls_pod = self.query.class_pod_list[cls_num]
        inst    = cls_pod.inst_get_inst_by_id(inst_id = row[1], zombie = False)
        if self.returned_pod_types:
            inst_dict = object.__getattribute__(inst, '__dict__')
            new_results = {}
            for j,col,loader in self.returned_pod_types[cls_num]:
                if col not in inst_dict:
                    new_results[col] = loader.load(value = row[j], inst = inst)
            inst_dict.update(new_results)
        return inst
                                            
class RawQuery(object):
    
    def __init__(self, select = None, distinct = False, where = None, order_by = None, group_by = None, having = None, offset = None, limit = None, cls = None):
    
        self.select   = select
        self.distinct = distinct
        self.where    = where
        self.order_by = order_by
        self.group_by = group_by
        self.having   = having 
        self.offset   = offset
        self.limit    = limit
        Row.cls       = Row if cls is None else cls

        self.db            = None
        
    def __iter__(self):
        return RawQueryIterator(raw_query = self)
    
    def get_sql(self):
        
        if isinstance(self.where, core.Meta):
            class_pods = set(self.where)
            where   = None
            self.db = class_pods[0].db
        elif self.where:
            where = self.where
            where.get_sql(full_name = False, type = 'where')
            self.db = None
            class_pods = self.where.class_pods
        else:
            class_pods = set()
        
        sql,values = "",[]    
        
        sql += "SELECT "
        
        if self.distinct:
            sql += "DISTINCT "
        
        if self.select:
            self.select.get_sql(full_name = True, type = 'select')
            sql        += self.select.expression            
            values     += self.select.args
            class_pods |= self.select.class_pods
        else:
            sql += "* "
        
                    
        sql += " FROM " + ",".join([cls_pod.table for cls_pod in class_pods])

        if self.where:
            self.where.get_sql(full_name = True)
            sql    += " WHERE " + where.expression
            values += where.args
    
        if self.group_by:
            self.group_by.get_sql(full_name = True, type = 'group_by')
            sql    += " GROUP BY " + self.group_by.expression            
            values += self.group_by.args
        
        if self.having:
            self.having.get_sql(full_name = True, type = 'where')
            sql    += " HAVING " + self.having.expression            
            values += self.having.args
    
        if self.order_by:
            self.order_by.get_sql(full_name = True)
            sql += " ORDER BY " + self.order_by.expression
                
        if self.limit:
            sql += " LIMIT " + str(self.limit)
    
        if self.offset:
            sql += " OFFSET " + str(self.offset)

        # Now, define a database connection
        for cls_pod in class_pods:
            if self.db is None:
                self.db = cls_pod.db
            elif self.db is not cls_pod.db:
                raise PodQueryError, "You are trying to get records from classes from different database connections . . . "

        # This checks to see if any of the tables have yet to be created. 
        # If they haven't, return an empty query
        for cls_pod in class_pods:        
            if cls_pod.id is None:
                return '',() 
        return sql,values        
    
    def get_one(self, error_on_multiple = True):
        objects = [object for object in self]
        if len(objects) == 0:
            return None
        else:
            if error_on_multiple and len(objects) > 1:
                raise PodQueryError, "More than one object returned . . . "
            return objects[0]

class RawQueryIterator(object):
    
    def __init__(self, raw_query):
        
        self.raw_query = raw_query
        
        # First, activate make sure the Row.cls has a table if it's a pod.Object
        # If you don't do this, you'll get this error: sqlite3.OperationalError: cannot commit transaction - SQL statements in progress
        if isinstance(Row.cls, core.Meta) and Row.cls.pod.id is None:
            Row.cls.pod.table_create(inst = None, kwargs = None, create_inst = False)
            
        sql,values = raw_query.get_sql()  
        raw_query.db.connection.row_factory = Row
        if raw_query.db.very_chatty:
            self.current_cursor = raw_query.db.get_new_cursor()
        else:
            self.current_cursor = raw_query.db.connection.cursor()
            
        self.current_cursor.execute(sql, values)
        
        # Now, setup the row factory . .  .    
        if self.current_cursor.description:        
            Row.pod_types = [desc[0].split(".")[-1] for desc in self.current_cursor.description]
        if isinstance(Row.cls, core.Meta):
            Row.pod_type_fns = Row.cls.pod.typed_group
        else:
            Row.pod_type_fns = {}
            
        if raw_query.db.chatty:
            print 'pod.RawQuery to return the following pod_types: \n\t' + str(Row.pod_types) + '\n'

    def next(self):
        return self.current_cursor.next()
    
class Row(object):
    
    cls         = None
    pod_types     = None
    pod_type_fns  = None

    def __new__(cls, *args):
        
        new_dict = {}
        if Row.cls is Row:
            inst = object.__new__(Row)
            for i,value in enumerate(args[1]):
                if isinstance(value, unicode):
                    value = str(value)
                new_dict[i] = value
                new_dict[Row.pod_types[i]] = value
            inst.__dict__.update(new_dict)
            return inst
        else:
            for i,value in enumerate(args[1]):
                name = Row.pod_types[i]
                if name in Row.pod_type_fns:
                    # TODO: See if this load call effects mutable callbacks . . . 
                    new_dict[name] = Row.pod_type_fns[name].load(value)
                else:
                    if isinstance(value, unicode):
                        value = str(value)
                    new_dict[name] = value    
            return Row.cls(**new_dict)                    
              
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value
                
