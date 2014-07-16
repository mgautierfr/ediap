

class Token:
    def __init__(self, start, end):
        self._start = start
        self._end   = end

    @property
    def klass(self):
        return self.__class__.__name__


    @property
    def start(self):
        return "%d.%d"%(self._start.row, self._start.col-1)

    @property
    def end(self):
        return "%d.%d"%(self._end.row, self._end.col-1)

class Program(Token):
    def __init__(self, parts, start, end):
        Token.__init__(self, start, end)
        self.parts = parts

class Call(Token):
    def __init__(self, name, args, start, end):
        Token.__init__(self, start, end)
        self.name = name
        self.args = args

class Value(Token):
    def __init__(self, value, start, end):
        Token.__init__(self, start, end)
        self.v  = value

class Identifier(Value):
    pass

class Int(Value):
    pass

class Float(Value):
    pass
