
import functions

class Instruction:
    @property
    def klass(self):
        return self.__class__.__name__
        

class Call(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __call__(self):
        function = getattr(functions, self.name.v, None)
        if function is not None:
            return function(self.level, *self.args)
        else:
            return functions._functionCall(self.level, self.name, self.args)
        

class Assignement(Instruction):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self):
        return functions._setter(self.level, self.name, self.value)

class If(Instruction):
    def __init__(self, test):
        self.test = test

    def __call__(self):
        return functions._if(self.level, self.test)

class While(If):
    def __call__(self):
        return functions._while(self.level, self.test)


class FunctionDef(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __call__(self):
        return functions._functionDef(self.level, self.name, self.args)
