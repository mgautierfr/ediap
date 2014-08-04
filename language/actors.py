from . import objects

class Actor:
    def __init__(self, level):
        self.level = level

    @property
    def klass(self):
        return self.__class__.__name__

class var_creator(Actor):
    def __init__(self, level, type_, name):
        Actor.__init__(self, level)
        self.type_ = type_
        self.name = name

    def __call__(self, state):
        if self.type_ == "var":
            var = objects.Variable()
        state.namespace[self.name] = var

class setter(Actor):
    def __init__(self, level, name, value):
        Actor.__init__(self, level)
        self.name = name
        self.value = value

    def __call__(self, state):
        state.namespace[self.name.v].set(self.value.get_node(state.namespace))

class _if(Actor):
    def __init__(self, level, test):
        Actor.__init__(self, level)
        self.test = test

    def __call__(self, state):
        test_node = self.test.get_node(state.namespace)
        return test_node()

class _while(_if):
    pass

class functionDef(Actor):
    def __init__(self, level, name, args):
        Actor.__init__(self, level)
        self.name = name
        self.args = args

    def __call__(self, state):
        state.functions[self.name.v] = objects.FunctionDefinition(self.name.v, [(t, a.v) for t,a in self.args])

class functionCall(Actor):
    def __init__(self, level, name, args):
        Actor.__init__(self, level)
        self.name = name
        self.args = args

    def __call__(self, state):
        functionDef = state.functions[self.name.v]
        for argTypeName, arg in zip(functionDef.args, self.args):
            argType, argName = argTypeName
            if argType == "var":
                var = objects.Variable()
            state.namespace.dict[argName] = var
            var.set(arg.get_node(state.namespace))
