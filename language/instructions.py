from . import actors

class Instruction:
    @property
    def klass(self):
        return self.__class__.__name__

    def get_token_at_pos(self, pos):
        return None


class Comment(Instruction):
    def __init__(self, text):
        self.text = text

    def __call__(self):
        return None

class Use(Instruction):
    def __init__(self, type_, name):
        self.type_ = type_
        self.name = name

    def __call__(self):
        return actors.var_creator(self.level, self.type_.v, self.name.v)


class Assignement(Instruction):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self):
        return actors.setter(self.level, self.name, self.value)

    def get_token_at_pos(self, pos):
        if self.value.start <= pos <= self.value.end:
            return self.value.get_token_at_pos(pos)
        return None

class If(Instruction):
    def __init__(self, test):
        self.test = test

    def __call__(self):
        return actors._if(self.level, self.test)

    def get_token_at_pos(self, pos):
        if self.test.start <= pos <= self.test.end:
            return self.test.get_token_at_pos(pos)
        return None

class While(If):
    def __call__(self):
        return actors._while(self.level, self.test)


class FunctionDef(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __call__(self):
        return actors.functionDef(self.level, self.name, self.args)

class Builtin(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __call__(self, lib):
        function = getattr(lib, self.name.v)
        # this is a builtin call
        return function(self.level, *self.args)

    def get_token_at_pos(self, pos):
        for arg in self.args:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

class Call(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __call__(self):
        return actors.functionCall(self.level, self.name, self.args)

    def get_token_at_pos(self, pos):
        for arg in self.args:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

