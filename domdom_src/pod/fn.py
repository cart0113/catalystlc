import exceptions

import typed

class PodFnError(exceptions.BaseException):
    pass

class fn(typed.TypedExpression):
    
    def __init__(self, *args):
        typed.TypedExpression.__init__(self)
        if len(args) > 0 and not isinstance(args[0], typed.TypedExpression):
            raise PodFnError, "You can only use functions on typed columns . . . "
        self.fn_args = []
        for arg in args:
            if arg is not None:
                self.fn_args.append("'" + arg + "'" if isinstance(arg, str) else arg)
        
    def get_my_sql(self, head):
        head.expression += self.__class__.__name__ + "("
        for arg in self.fn_args:
            self.process_arg(head = head, value = arg, left = True)
            head.expression += ", "
        if len(self.fn_args) > 0:
            head.expression = head.expression[:-2]
        head.expression = head.expression + ")"
       
""" scalar functions """ 
class abs(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class length(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class lower(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class upper(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class ltrim(fn):
    def __init__(self, col,pattern = None):
        fn.__init__(self,col,pattern)
class rtrim(fn):
    def __init__(self, col,pattern = None):
        fn.__init__(self,col,pattern)
class trim(fn):
    def __init__(self, col,pattern = None):
        fn.__init__(self,col,pattern)
class min(fn):
    def __init__(self, col,min_value = None):
        fn.__init__(self,col,min_value)
class max(fn):
    def __init__(self, col,max_value = None):
        fn.__init__(self,col,max_value)
class replace(fn):
    def __init__(self, col, find, replace):
        fn.__init__(self,col,find,replace)
class random(fn):
    def __init__(self):
        fn.__init__(self)
class substr(fn):
    def __init__(self, col,start,stop = None):
        fn.__init__(self,col,start,stop)

    
""" fn functions """
class count(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class avg(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class sum(fn):
    def __init__(self, col):
        fn.__init__(self,col)
class total(fn):
    def __init__(self, col):
        fn.__init__(self,col)
