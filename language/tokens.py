from . import nodes

operators = ['<', '<=', '>', '>=', '!=', '==', '-','+','*','/']

class Token:
    precedence = 1000
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    @property
    def klass(self):
        return self.__class__.__name__

    def get_token_at_pos(self, pos):
        return None

class Value(Token):
    def __init__(self, value, start, end):
        Token.__init__(self, start, end)
        self.v  = value
        self._node = nodes.Value(value)

    def get_node(self, namespace):
        return self._node

    def get_token_at_pos(self, pos):
        return self

class Int(Value):
    pass

class Float(Value):
    pass

class Paren(Value):
    def get_node(self, namespace):
        return self.v.get_node(namespace)

    def get_token_at_pos(self, pos):
        return self.v.get_token_at_pos(pos)

class Identifier(Value):
    def get_node(self, namespace):
        return namespace[self.v].get()

class BinaryOp(Token):
    def __init__(self, name, x, y, start, end):
        Token.__init__(self, start, end)
        self.name = name
        self.x, self.y = x, y

    def get_node(self, namespace):
        return nodes.Operator(self.name.v, self.x.get_node(namespace), self.y.get_node(namespace))

    @property
    def precedence(self):
        return operators.index(self.name.v)

    def merge(self):
        right = self.y
        if self.precedence >= right.precedence:
            self.y = right.x
            right.x = self
            return right
        else:
            return self

    def __str__(self):
        return "%s %s %s"%(self.name, self.start, self.end)

    def get_token_at_pos(self, pos):
        if self.x.start <= pos <= self.x.end:
            return self.x.get_token_at_pos(pos)
        if self.y.start <= pos <= self.y.end:
            return self.y.get_token_at_pos(pos)
        return None

