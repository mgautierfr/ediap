
from collections import ChainMap

class InvalidIndent(Exception):
    pass


class State:
    def __init__(self, lineno):
        self.lineno = lineno
        self.shapes = []
        self.hiddenState = ChainMap({})
        self.namespace = ChainMap({})
        self.child = None

    def new_child(self, lineno):
        child = State(lineno)
        child.shapes = self.shapes[:]
        child.hiddenState = self.hiddenState.new_child()
        child.namespace = self.namespace.new_child()
        self.child = child
        return child

class Interpreter:
    def __init__(self, prog):
        self.prog = prog
        self.states = []

    def new_state(self, lineno):
        state = self.states[-1].new_child(lineno)
        self.states.append(state)
        return state

    @property
    def state(self):
        return self.states[-1]

    def pass_level(self, level, pc):
        while pc < len(self.prog) and self.prog[pc][2].level >= level:
            pc += 1
        return pc

    def run_level(self, level, pc):
        while pc < len(self.prog):
            lineno, actor, node = self.prog[pc]
            if node.level < level:
                break
            if node.level > level:
                raise InvalidIndent(pc, node.level, level)
            pc += 1
            if node.klass == "If":
                result = actor.act(self.state)
                if result:
                    pc = self.run_level(self.prog[pc][2].level, pc)
                else:
                    pc = self.pass_level(self.prog[pc][2].level, pc)
            elif node.klass == "While":
                while actor.act(self.state):
                    self.run_level(self.prog[pc][2].level, pc)
                else:
                    pc = self.pass_level(self.prog[pc][2].level, pc)
            else:
                state = self.new_state(lineno)
                actor.act(state)
    
        return pc
    
    def run_prog(self):
        state = State(0)
        self.states = [state]
        state.hiddenState.update({'fillColor'       : (state, set(), "#000000"),
                                  'x_canvas_range'  : (state, set(), [0, 100]),
                                  'y_canvas_range'  : (state, set(), [0, 100])
                                 })
        self.run_level(0, 0)
        return self.state
