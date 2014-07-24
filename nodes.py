
class Node:
    def __init__(self):
        self.referers = set()
        self.cached = None

    def __call__(self):
        if self.cached is None:
            self.cached = self.get_value()
        return self.cached

    def clean_cache(self):
        self.cached = None
        for ref in self.referers:
            ref.clean_cache()

    def add_ref(self, ref):
        self.referers.add(ref)

class Value(Node):
    def __init__(self, v):
        Node.__init__(self)
        self.v = v

    def get_value(self):
        return self.v

    def depend(self):
        return set([self])


class Operator(Node):
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
        Node.__init__(self)
        self.op = op
        self.x, self.y = x, y
        x.add_ref(self)
        y.add_ref(self)

    def get_value(self):
        return Operator.binary_ops[self.op](self.x(), self.y())

    def depend(self):
        return set([self])|self.x.depend()|self.y.depend()


