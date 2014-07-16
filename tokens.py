
operators = ['-','+','*','/']


class Token:
    precedence = 1000
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

class BinaryOp(Call):
    @property
    def precedence(self):
        return operators.index(self.name.v)

    def merge(self):
        left = self.args[0]
        right = self.args[1]
        if self.precedence >= right.precedence:
            self.args[1] = right.args[0]
            right.args[0] = self
            return right
        else:
            return self

class Value(Token):
    def __init__(self, value, start, end):
        Token.__init__(self, start, end)
        self.v  = value

class Paren(Value):
    pass

class Identifier(Value):
    pass

class Int(Value):
    pass

class Float(Value):
    pass

