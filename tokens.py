
operators = ['-','+','*','/']


class Token:
    precedence = 1000
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    @property
    def klass(self):
        return self.__class__.__name__

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
        print("binop %s %s %s %s"%(self.name, self.args, self.start, self.end))

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

    def execute(self, namespace):
        args = [n.execute(namespace) for n in self.args]
        return BinaryOp.binary_ops[self.name.v](*args)

    def __str__(self):
        return "%s %s %s %s"%(self.name, self.args, self.start, self.end)

class Assignement(Token):
    def __init__(self, name, value, start, end):
        Token.__init__(self, start, end)
        self.name = name
        self.value = value

class Value(Token):
    def __init__(self, value, start, end):
        Token.__init__(self, start, end)
        self.v  = value

    def execute(self, namespace):
        return self.v

class Paren(Value):
    def execute(self, namespace):
        return self.v.execute(namespace)

class Identifier(Value):
    def execute(self, namespace):
        return namespace[self.v]

class Int(Value):
    pass

class Float(Value):
    pass

