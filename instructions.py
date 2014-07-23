
import functions

class Instruction:
    @property
    def klass(self):
        return self.__class__.__name__
        

class Call(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __call__(self, context):
        function = getattr(functions, self.name.v)
        return function(context, self.level, *self.args)
        

class Assignement(Instruction):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self, context):
        return functions._setter(context, self.level, self.name, self.value)

class If(Instruction):
    def __init__(self, test):
        self.test = test

    def __call__(self, context):
        return functions._if(context, self.level, self.test)

class While(If):
    def __call__(self, context):
        return functions._while(context, self.level, self.test)
