

class Instruction:
    is_nop = False

    @property
    def klass(self):
        return self.__class__.__name__

    def get_token_at_pos(self, pos):
        return None

class Comment(Instruction):
    is_nop = True
    def __init__(self, text):
        self.text = text

class Create(Instruction):
    def __init__(self, type_, name):
        self.type_ = type_
        self.name = name


class Set(Instruction):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_token_at_pos(self, pos):
        if self.value.start <= pos <= self.value.end:
            return self.value.get_token_at_pos(pos)
        return None

class If(Instruction):
    def __init__(self, test):
        self.test = test

    def get_token_at_pos(self, pos):
        if self.test.start <= pos <= self.test.end:
            return self.test.get_token_at_pos(pos)
        return None

class While(If):
    pass


class Create_subprogram(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Builtin(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def get_token_at_pos(self, pos):
        for arg in self.args:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

class Do_subprogram(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def get_token_at_pos(self, pos):
        for arg in self.args:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

