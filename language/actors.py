class _FunctionDefinition:
    def __init__(self, name, args):
        self.name = name,
        self.args = args

class Actor:
    def __init__(self, level):
        self.level = level

    @property
    def klass(self):
        return self.__class__.__name__

class setter(Actor):
    def __init__(self, level, name, value):
        Actor.__init__(self, level)
        self.name = name
        self.value = value

    def __call__(self, state):
        state.namespace[self.name.v] = self.value.get_node(state.namespace)

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
        state.functions[self.name.v] = _FunctionDefinition(self.name.v, [arg.v for arg in self.args])

class functionCall(Actor):
    def __init__(self, level, name, args):
        Actor.__init__(self, level)
        self.name = name
        self.args = args

    def __call__(self, state):
        functionDef = state.functions[self.name.v]
        for argName, arg in zip(functionDef.args, self.args):
            state.namespace.dict[argName] = arg.get_node(state.namespace)
