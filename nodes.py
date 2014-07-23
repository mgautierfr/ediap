
class Value:
    def __init__(self, v):
        self.v = v

    def __call__(self):
        return self.v

    def depend(self):
        return set([self])


class Operator:
    binary_ops = {
        '+' : lambda x, y : x+y,
        '-' : lambda x, y : x-y,
        '/' : lambda x, y : x/y,
        '*' : lambda x, y : x*y,
        '==': lambda x, y : x==y,
        '<' : lambda x, y : x<y,
        '>' : lambda x, y : x>y,
        '!=' : lambda x, y : x!=y,
        '<=' : lambda x, y : x<=y,
        '>=' : lambda x, y : x>=y
        }

    def __init__(self, op, x, y):
        self.op = op
        self.x, self.y = x, y

    def __call__(self):
        return Operator.binary_ops[self.op](self.x(), self.y())

    def depend(self):
        return set([self])|self.x.depend()|self.y.depend()


