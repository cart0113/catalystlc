import exceptions

import time
import datetime
 
import core

class PodColumnError(exceptions.BaseException):
    pass

class Expression(object):
    
    def __init__(self, left = None, right = None, op = None, parens = True):            
        self.left    = left
        self.right   = right
        self.op      = op
        self.parens  = parens
    
    def get_sql(self, full_name = False, type = None):
        
        self.expression = ""
        self.args       = []
        self.classes    = set()
        self.full_name  = full_name
        #type includes select, raw_select, where, group_by, order_by
        self.type       = type
        
        self.get_my_sql(head = self)

    def get_my_sql(self, head):
        
        """ left """
        if head.type == 'where' and self.parens:
            head.expression += "("
        if isinstance(self.left, Expression):
            self.left.get_my_sql(head = head)
        elif self.left is not None:
            self.process_arg(head = head, value = self.left)
            
        if self.op:
            head.expression += self.op
        else:
            raise PodColumnError, "Expression must be either terminal or have an operation . . . "
        
        """ right """
        if isinstance(self.right, Expression):
            self.right.get_my_sql(head = head)
        elif self.right is not None:
            self.process_arg(head = head, value = self.right)

        if head.type == 'where' and self.parens: 
            head.expression += ")"
                 
    def process_arg(self, head, value):
        if isinstance(value, Expression):
            value.get_my_sql(head = head)
        elif isinstance(value, core.Object):
            head.expression += "?"
            head.args.append(value.get_full_id())
        elif isinstance(value, bool):
            head.expression += "?"
            head.args.append(int(bool(value)))
        elif isinstance(value, (list,set)):
            head.expression += "("
            for item in value:
                self.process_arg(head = head, value = item)
                head.expression += ","
            head.expression = head.expression[:-1] + ")"    
        else:
            head.expression += "?"
            head.args.append(value)
        
    """ EXPRESSION CHAINING """
    def __and__(self, other):
        raise PodColumnError, "The INTERSECT '&' operator not supported on column expressions . . . "
    
    def __or__(self, other):
        return Expression(left = self, right = other, op = ',')
    
    """ THE AS NAME NAMING OPERATOR """
    def __rshift__(self, as_name):
        #if self.as_name and as_name:
        #    raise PodColumnError, "You tried to set column expression to '" + as_name + "' but it's already set to '" + str(self.as_name) + "' . . . "
        return AsName(left = self, right = None, op = ' AS ' + as_name + ' ')
    
    """ MATH OPERATORS """
    def __add__(self, other):
        return Math(left = self, right = other, op = '||' if isinstance(other, str) else ' + ' )
    def __radd__(self, other):
        return Math(left = other, right = self, op = '||' if isinstance(other, str) else ' + ' )
    def __sub__(self, other):
        return Math(left = self, right = other, op = "-")
    def __rsub__(self, other):
        return Math(left = other, right = self, op = "-")
    def __mul__(self, other):
        return Math(left = self, right = other, op = "*")
    def __rmul__(self, other):
        return Math(left = other, right = self, op = "*")
    def __div__(self, other):
        return Math(left = self, right = other, op = "/")
    def __rdiv__(self, other):
        return Math(left = other, right = self, op = "/")
    
    """ COMPARISON OPERATORS """
    def __eq__(self, value):
        if value is None:
            return Condition(left = self, op = ' IS NULL', right = None)
        else:
            return Condition(left = self, op = '=', right = value)

    def __ne__(self, value):
        if value is None:
            return Condition(left = self, op = 'IS NOT NULL', right = None)
        else:
            return Condition(left = self, op = '<>', right = value)
    
    def contains(self, value):
        return Condition(left = self, op = ' LIKE ',   right = '%' + str(value) + '%')
    
    def startswith(self, value):
        return Condition(left = self, op = ' LIKE ',   right = str(value) + '%')
    
    def endswith(self, value):
        return Condition(left = self, op = ' LIKE ', right = '%' + str(value))
    
    def is_in(self, value):
        return Condition(left = self, op = ' IN ', right = value) 
        
    def __gt__(self, value):
        return Condition(left = self, op = ' > ',  right = value)
    
    def __ge__(self, value):
        return Condition(left = self, op = ' >= ', right = value)
    
    def __lt__(self, value):
        return Condition(left = self, op = ' < ',  right = value)
      
    def __le__(self, value):
        return Condition(left = self, op = '<= ', right = value)

    def between(self, low, high):
        return Condition(left = self, op = ' BETWEEN ', right = Condition(left = low, right = high, op = ' AND ', parens = False))
    
    """ order by """
    def asc(self):
        return OrderAsc(col = self)
    
    def desc(self):
        return OrderDesc(col = self)
        
class AsName(Expression):
    
    
    def get_my_sql(self, head):
        if head.type != 'select':
            raise PodColumnError, "You cannot use AS operator '>>' in anything but the select statement . . ."
        return Expression.get_my_sql(self, head)
    
class Math(Expression):
    
    def __init__(self, left = None, right = None, op = None, parens = True):            
        self.left    = left
        self.right   = right
        self.op      = op
        self.parens  = parens

class Condition(Expression):
    
    def __init__(self, left = None, right = None, op = None, parens = True):            
        self.left    = left
        self.right   = right
        self.op      = op
        self.parens  = parens
        
    def __and__(self, other):
        return Condition(left = self, right = other, op = ' AND ')

    def __or__(self, other):
        return Condition(left = self, right = other, op = ' OR ')
    
    def __iter__(self):
        return Query(where = self)

    def delete(self):
        return Query(where = self).delete()

""" ############################################################################################
###
###    THE COLUMNS
###
""" ############################################################################################

class Column(Expression):

    def __init__(self, index = False, cls = None, db = None, name = None):        
        Expression.__init__(self)
        self.index = index
        if cls and db and name:
            self.update(cls = cls, db = db, name = name)

    def __getstate__(self):
        return {'index': self.index}
            
    def drop(self):
        self.cls.pod.column_drop_and_delete_forever(self)
            
    def get_deep_copy(self, cls):
        return self.__class__(index = self.index, cls = cls, db = self.db, name = self.name)
        
    def update(self, cls, db, name):
        self.cls     = cls
        self.db      = db
        self.name    = name
                
    def get_alter_table(self):
        return self.name + " " + self.db_type
    
    def dump(self, value):
        return None if value is None else self.py_type(value)
    
    def load(self, value):
        return None if value is None else self.py_type(value)
    
    def is_same_column_type(self, other):
        return other.index == self.index and other.__class__ is self.__class__
    
    def get_my_sql(self, head):
        head.expression += self.get_sql_column_name(head = head)
        head.classes.add(self.cls)
                   
    def get_sql_column_name(self, head):
        return type.__getattribute__(self.cls, 'pod').table + '.' + self.name if head.full_name else self.name
                   
""" Boolean """
class Boolean(Column):
    
    db_type = 'INTEGER'

    def dump(self, value):
        return None if value is None else int(bool(value))
    
    def load(self, value):
        return None if value is None else bool(value)

""" String """    
class String(Column):
    
    db_type = 'TEXT'
    py_type = str
        
""" Number """
class Number(Column):
    pass

class Int(Number):
    db_type = 'INTEGER'
    py_type = int

class Float(Number):
    db_type = 'REAL'
    py_type = float

# can be True, False, None

""" Objects -- This is a biggie! """
class Object(Column):
    
    db_type = 'TEXT'
                           
    def dump(self, value):
        if value is None:
            return None
        elif isinstance(value, core.Object):
            return value.get_full_id()
        elif isinstance(value, core.Undefined):
            return value.get_full_id()
        elif isinstance(value, core.Deleted):
            return None
        else:
            raise PodColumnError, "Value '" + str(value) + "' is not of type pod.Object . . . "
    
    def load(self, value):
        if value:
            value = value.split(":")
            return self.db.cache.get_inst(cls_id = int(value[0]), inst_id = int(value[1]))
        else:
            return None

""" Collection """    
class Collection(Column):    
    
    db_type = 'TEXT'
    
    def get_str(self, value):
        output = ">"
        for item in list(value):
            output += self.get_element_value(item)
        return output + "<"
    
    def get_element_value(self, value):
        if value is None:
            output = "<n>"
        elif isinstance(value, bool):
            output = "<b" + str(value) + ">"
        elif isinstance(value, str):
            output = "<s" + value.replace("><", "\>\<") + ">"
        elif isinstance(value, int):
            output = "<i" + str(value) + ">"
        elif isinstance(value, float):
            output = "<f" + str(value) + ">"
        elif isinstance(value, core.Object):
            output = "<o" + value.get_full_id() + ">"
        elif isinstance(value, core.Undefined):
            output = "<o" + value.get_full_id() + ">"
        elif isinstance(value, core.Deleted):
            output = "<n>"
        else:
            raise PodColumnError, "Type " + str(type(value)) + " on value " + str(value) + " not supported . . . only NoneType,bool,str,int,float,pod.Object supported at this time"
        return output 
    
    def load(self, value):
        if value is not None:
            values = str(value).split("><")[1:-1]
            new_list = []
            for item in values:
                if item[0] == "n":
                    new_list.append(None)
                elif item[0] == "b":
                    new_list.append(bool(str(item[1:])))
                elif item[0] == "s":
                    new_list.append(str(item[1:]).replace("\>\<", "><"))
                elif item[0] == "i":
                    new_list.append(int(str(item[1:])))
                elif item[0] == "f":
                    new_list.append(float(str(item[1:])))
                elif item[0] == "o":
                    o = str(item[1:]).split(":")
                    new_list.append(self.db.cache.get_inst(cls_id = int(o[0]), inst_id = int(o[1])))
            return new_list
        else:
            return None

    """ COMPARISON OPERATORS """
    def __eq__(self, value):
        if value is None:
            return Condition(left = self, op = ' IS NULL', right = None)
        else:
            return Condition(left = self, op = '=', right = self.get_str(value))

    def __ne__(self, value):
        if value is None:
            return Condition(left = self, op = 'IS NOT NULL', right = None)
        else:
            return Condition(left = self, op = '<>', right = self.get_str(value))

    def contains(self, value):
        return Condition(left = self, op = ' LIKE ',   right = '%' + self.get_element_value(value) + '%')

class List(Collection):
    
    def dump(self, value):
        if value is None:
            return None
        else:
            if isinstance(value, list):
                return self.get_str(value)
            else:
                raise PodColumnError, "Value must be a list for column.List type.  You gave " + str(value) + " . . ."

class Set(Collection):

    def dump(self, value):
    
        if(value is None):
            return None
        else:
            if isinstance(value, set):
                return self.get_str(value)
            else:
                raise PodColumnError, "Value must be a set for column.Set type.  You gave " + str(value) + " . . ."

    def load(self, value):
        return None if value is None else set(Collection.load(self, value))
                   
""" Special columns that do automagic things """

class Time(Int):
    
    @staticmethod
    def utc_timestamp(): 
        #t = datetime.datetime.utcnow()
        #return time.mktime(t.timetuple()) +1e-6*t.microsecond
        return int(time.mktime(datetime.datetime.utcnow().timetuple()))
    
    def __init__(self, index = False, date_string = False, local_time = True, convert_time_stamp = True, cls = None, db = None, name = None):
        Int.__init__(self, index = index, cls = cls, db = db, name = name)
        self.date_string        = date_string
        self.local_time         = local_time
        self.convert_time_stamp = convert_time_stamp
        self.utc_offset         = Time.utc_timestamp()-int(time.time())

    def load(self, value):
        if self.date_string and self.convert_time_stamp:
            return self.convert_utc_stamp_to_time(Int.load(self, value))
        else:
            return Int.load(self, value)
    
    def dump(self, value):
        if isinstance(value, TimeStamp):
            return Int.dump(self, value)
        elif self.date_string and self.convert_time_stamp:
            return Int.dump(self, self.convert_time_to_utc_stamp(value))
        else:
            return Int.dump(self, value)


    def add_time_stamp_to_db(self):
        db = self.cls.pod.db
        if getattr(db, 'time_stamp', None) is None:
            db.time_stamp = TimeStamp()
        
    def older_than(self, years = 0, weeks = 0, days = 0, hours = 0, minutes = 0, seconds = 0):
        ctime = years*365*24*3600 + weeks*7*24*3600 + days*24*3600 + hours*3600 + minutes*60 + seconds
        return self <= int(Time.utc_timestamp()-ctime)
    
    def younger_than(self, years = 0, weeks = 0, days = 0, hours = 0, minutes = 0, seconds = 0):
        ctime = years*365*24*3600 + weeks*7*24*3600 + days*24*3600 + hours*3600 + minutes*60 + seconds
        return self >= int(Time.utc_timestamp()-ctime)
    
    def pre_dates(self, year = None, month = None, day = None, hour = None, minute = None, second = None, time_stamp = None, local_time = None):
        return self <= self.args_to_epoch(year,month,day,hour,minute,second,time_stamp,local_time if local_time is not None else self.local_time)
        
    def post_dates(self, year = None, month = None, day = None, hour = None, minute = None, second = None, time_stamp = None, local_time = None):
        return self >= self.args_to_epoch(year,month,day,hour,minute,second,time_stamp,local_time if local_time is not None else self.local_time)
    
    def is_date(self, year = None, month = None, day = None, local_time = None):
        local_time = local_time if local_time is not None else self.local_time
        if day:
            year = year if year is not None else datetime.datetime.now().year
            month = month if month is not None else datetime.datetime.now().month
            return self.post_dates(year,month,day,None,None,None,None,local_time) & self.pre_dates(year,month,day+1,None,None,None,None,local_time)
        elif month:
            year = year if year is not None else datetime.datetime.now().year
            return self.post_dates(year,month,day,None,None,None,None,local_time) & self.pre_dates(year,month+1,day,None,None,None,None,local_time)
        elif year:
            return self.post_dates(year,month,day,None,None,None,None,local_time) & self.pre_dates(year+1,month,day,None,None,None,None,local_time)
        else:
            raise PodQueryError, "You did not provide a year, month, or day for is_date . . . "

    def args_to_epoch(self,y,m,d,h,n,s,time_stamp,local_time):        
        if time_stamp and self.date_string is None:
            raise PodQueryError, "You provided a time_stamp '" + str(time_stamp) + "' but this column does not have a date_string convertor set . . . "
        elif time_stamp and self.date_string:
            ctime = time.mktime(time.strptime(time_stamp, self.date_string))
        else:
            y = y if y is not None else datetime.datetime.now().year
            m = m if m is not None else 1
            d = d if d is not None else 1
            h = h if h is not None else 0
            n = n if n is not None else 0
            s = s if s is not None else 0        
            ctime = time.mktime(datetime.datetime(y,m,d,h,n,0).timetuple())+s        
        return int(ctime + int(local_time)*self.utc_offset)
        
    def convert_time_to_utc_stamp(self, value, date_string = None, local_time = None):
        date_string = date_string if date_string is not None else self.date_string
        value = datetime.datetime.fromtimestamp(value) if isinstance(value, (int,float,long)) else value
        value = time.strptime(value, date_string) if date_string else value.timetuple()                  
        return int(time.mktime(value) + self.utc_offset*int(local_time if local_time is not None else self.local_time))
    
    def convert_utc_stamp_to_time(self, value, date_string = None, local_time = None):
        date_string = date_string if date_string is not None else self.date_string
        value = int(value-self.utc_offset*int(local_time if local_time is not None else self.local_time))
        return datetime.datetime.fromtimestamp(value).strftime(date_string) if date_string else value
    
class TimeCreate(Time):
    
    def update(self, cls,db,name):
        Time.update(self, cls = cls, db = db, name = name)
        cls.pod.column_callbacks_create.add(self)
        self.add_time_stamp_to_db()
        
    def on_inst_create(self, inst):
        if self.name not in object.__getattribute__(inst, '__dict__'):
            object.__getattribute__(object.__getattribute__(inst, '__class__'), 'pod').inst_set_attr(inst, self.name, self.db.time_stamp)
        
class TimeMod(Time):
    
    def update(self,cls,db,name):
        Time.update(self, cls = cls, db = db, name = name)
        cls.pod.column_callbacks_mod.add(self)        
        self.add_time_stamp_to_db()

    def on_inst_mod(self, inst):
        if self.name not in object.__getattribute__(inst, '__dict__'):
            object.__getattribute__(object.__getattribute__(inst, '__class__'), 'pod').inst_set_attr(inst, self.name, self.db.time_stamp)

class TimeStamp(object):
        
    def set_time(self):
        self.time = Time.utc_timestamp()
        
    def __int__(self):
        return self.time



class Order(Expression):
    
    def __init__(self, col):
        Expression.__init__(self)
        self.col = col
        
    
    def get_my_sql(self, head):
        head.expression += self.col.get_sql_column_name(head) + " " + self.TYPE

class OrderAsc(Order):
    TYPE = 'ASC'

class OrderDesc(Order):
    TYPE = 'DESC'
        
        
""" ############################################################################################
###
###    THE QUERY 
###
""" ############################################################################################
    
class PodQueryError(exceptions.BaseException):
    pass
                
class Query(object):

    def __init__(self, select = None, where = None, order_by = None, offset = None, limit = None, get_children = True):

        self.select        = select
        self.where         = where
        self.order_by      = order_by
        self.limit         = limit
        self.offset        = offset
        # Other flags . . . 
        self.get_children  = get_children
        self.db            = None
        self.active        = False
    
    def __iter__(self):
        return self
        
    def get_sql(self):
        
        if isinstance(self.where, core.Meta):
            cls = self.where
            where = None
        elif self.where:
            where = self.where
            where.get_sql(full_name = False, type = 'where')
            if len(where.classes) > 1:
                raise PodQueryError, "You cannot mix class types in a pod.Query where statement -- use pod.RawQuery instead . . . "
            cls = where.classes.pop()
        else:
            raise PodQueryError, "Improper where statement . . ."

        self.db              = cls.pod.db
        self.class_list      = self.get_class_list(cls = cls, list = [])
            
        if self.select:
            self.select.get_sql(full_name = False)
            if len(self.select.classes) > 1:
                raise PodQueryError, "You cannot mix class types in a pod.Query select statement -- use pod.RawQuery instead . . . "
        
        if self.order_by:
            self.order_by.get_sql(full_name = False)

        sql,values = "",[]

        for i,cls in enumerate(self.class_list):
                        
            if i > 0:
                sql += " UNION " 

            sql += "SELECT " + str(i) + " AS PODCLASS,id"
            
            if self.select:
                sql    += "," + self.select.expression 
                if len(self.select.args) > 0:
                    raise PodQueryError, "You cannot do any processing within a pod.Query select statement -- use pod.RawQuery instead . . . "
                values += self.select.args
                
            sql += " FROM " + cls.pod.table
            
            if where:
                sql    += " WHERE " + where.expression
                values += where.args
            
        if self.order_by:
            sql += " ORDER BY " + self.order_by.expression
                
        if self.limit:
            sql += " LIMIT " + str(self.limit)

        if self.offset:
            sql += " OFFSET " + str(self.offset)

        return sql,values
            
    def get_class_list(self, cls, list):
        
        list.append(cls)
        
        if self.get_children:
            for new_cls in cls.pod.child_classes:
                list = self.get_class_list(cls = new_cls, list = list)
            
        return list
     
    """
    The meat of the iterator
    """
    def next(self):
        if self.active is False:
            self.active = True
            sql,values = self.get_sql()  
            self.db.connection.row_factory = None
            if self.db.very_chatty:
                self.current_cursor = self.db.get_new_cursor()
            else:
                self.current_cursor = self.db.connection.cursor()
            self.current_cursor.execute(sql, values)
            columns = [desc[0] for desc in self.current_cursor.description][2:]
            if len(columns) > 0:
                self.returned_columns = []
                for i,cls in enumerate(self.class_list):
                    cls_pod = type.__getattribute__(cls,'pod')
                    self.returned_columns.append([])
                    for j,col in enumerate(columns):
                        if col in cls_pod.column_group:
                            self.returned_columns[i].append((j+2,col, cls_pod.column_group[col]))   # Duck typing: both columns and pickler support 'load' method
                        else:
                            # This is where we check that the columns are right!
                            raise PodQueryError, "You asked for column '" + col + "' but it is not a defined pod.column . . . "
            else:
                self.returned_columns = None
            return self.next()
        else:
            row     = self.current_cursor.next()
            cls_num = row[0]
            cls     = self.class_list[cls_num]
            cls_pod = type.__getattribute__(cls, 'pod')
            inst    = cls_pod.inst_get_inst_by_id(cls = cls, inst_id = row[1], exists = True)
            if self.returned_columns:
                new_results = {}
                for j,col,loader in self.returned_columns[cls_num]:
                    new_results[col] = loader.load(row[j])
                object.__getattribute__(inst, '__dict__').update(new_results)
            return inst

    """ 
    API
    """
    def delete(self):
        self.db = self.where[0].pod.db  
        self.current_cursor = self.db.get_new_cursor()      
        for cls in self.get_class_list(cls = self.where[0], list = []):
            sql = "DELETE FROM " + cls.pod.table + " WHERE " + self.where[1]    
            self.current_cursor.execute(sql,self.where[2])
        return self

    """ If you want to reset a query . . . """
    def reset(self):
        self.active = False
                                            
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
        self.active        = False
        
    def __iter__(self):
        return self
    
    def get_sql(self):
        
        if isinstance(self.where, core.Meta):
            classes = set(self.where)
            where   = None
            self.db = classes[0].pod.db
        elif self.where:
            where = self.where
            where.get_sql(full_name = False, type = 'where')
            self.db = None
            classes = self.where.classes
        else:
            classes = set()
        
        sql,values = "",[]    
        
        sql += "SELECT "
        
        if self.distinct:
            sql += "DISTINCT "
        
        if self.select:
            self.select.get_sql(full_name = True, type = 'select')
            sql     += self.select.expression            
            values  += self.select.args
            classes |= self.select.classes
        else:
            sql += "* "
        
                    
        sql += " FROM " + ",".join([cls.pod.table for cls in classes])

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
        for cls in classes:
            if self.db is None:
                self.db = cls.pod.db
            elif self.db is not cls.pod.db:
                raise PodQueryError, "You are trying to get records from classes from different database connections . . . "


        return sql,values        
    
    def next(self):
        if self.active is False:
            self.active = True
            sql,values = self.get_sql()  
            self.db.connection.row_factory = Row
            if self.db.very_chatty:
                self.current_cursor = self.db.get_new_cursor()
            else:
                self.current_cursor = self.db.connection.cursor()
            self.current_cursor.execute(sql, values)
            # Now, setup the row factory . .  .            
            Row.columns = [desc[0].split(".")[-1] for desc in self.current_cursor.description]
            if isinstance(Row.cls, core.Meta):
                Row.column_fns = Row.cls.pod.column_group
            else:
                Row.column_fns = {}
                
            if self.db.chatty:
                print 'pod.RawQuery to return the following columns: \n\t' + str(Row.columns) + '\n'
            return self.current_cursor.next()
        else:
            return self.current_cursor.next()

class Row(object):
    
    cls         = None
    columns     = None
    column_fns  = None

    def __new__(cls, *args):
        
        new_dict = {}
        if Row.cls is Row:
            inst = object.__new__(Row)
            for i,value in enumerate(args[1]):
                if isinstance(value, unicode):
                    value = str(value)
                new_dict[i] = value
                new_dict[Row.columns[i]] = value
            inst.__dict__.update(new_dict)
            return inst
        else:
            for i,value in enumerate(args[1]):
                name = Row.columns[i]
                if name in Row.column_fns:
                    new_dict[name] = Row.column_fns[name].load(value)
                else:
                    if isinstance(value, unicode):
                        value = str(value)
                    new_dict[name] = value    
            return Row.cls(**new_dict)                    
              
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value
                


