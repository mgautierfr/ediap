

class FunctionDefinition:
    def __init__(self, name, args):
        self.name = name,
        self.args = args

class Variable:
    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def clone(self):
        clone = Variable()
        clone.value = self.value
        return clone
