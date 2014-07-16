
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
    binary_ops = {
        '+' : lambda x, y : x+y,
        '-' : lambda x, y : x-y,
        '/' : lambda x, y : x/y,
        '*' : lambda x, y : x*y,
        }
    def __init__(self, name, args, start, end):
        Call.__init__(self, name, args, start, end)
        print("binop %s %s %s %s"%(self.name, self.args, self._start, self._end))

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

    def execute(self):
        args = [n.execute() for n in self.args]
        return BinaryOp.binary_ops[self.name.v](*args)

    def __str__(self):
        return "%s %s %s %s"%(self.name, self.args, self._start, self._end)

class Value(Token):
    def __init__(self, value, start, end):
        Token.__init__(self, start, end)
        self.v  = value

    def execute(self):
        return self.v

class Paren(Value):
    def execute(self):
        return self.v.execute()

class Identifier(Value):
    pass

class Int(Value):
    pass

class Float(Value):
    pass

