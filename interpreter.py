
from collections import ChainMap
import nodes

class InvalidIndent(Exception):
    pass

class ToManyInstruction(Exception):
    pass

class State:
    def __init__(self, lineno):
        self.lineno = lineno
        self.shapes = []
        self.hiddenState = {}
        self.namespace = {}

    def new_child(self, lineno):
        child = State(lineno)
        child.shapes = self.shapes[:]
        child.hiddenState = dict(self.hiddenState)
        child.namespace = dict(self.namespace)
        self.child = child
        return child

    def __str__(self):
        return "<State \n%s\n%s\n%s\n>"%(self.shapes, self.hiddenState, self.namespace)

class Interpreter:
    def __init__(self, prog, source):
        self.prog = prog
        self.source = source
        self.states = []
        self.watchdog = 10000

    def new_state(self, lineno):
        state = self.states[-1].new_child(lineno)
        self.states.append(state)
        return state

    @property
    def state(self):
        return self.states[-1]

    def pass_level(self, level, pc):
        while pc < len(self.prog) and self.prog[pc][1].level >= level:
            pc += 1
        return pc

    def run_level(self, level, pc):
        while pc < len(self.prog):
            lineno, actor = self.prog[pc]
            self.watchdog -= 1
            if not self.watchdog:
                raise ToManyInstruction()
            if actor.level < level:
                break
            if actor.level > level:
                raise InvalidIndent(pc, actor.level, level)
            pc += 1
            if actor.klass == "_if":
                result = actor(self.state)
                if result:
                    pc = self.run_level(self.prog[pc][1].level, pc)
                else:
                    pc = self.pass_level(self.prog[pc][1].level, pc)
            elif actor.klass == "_while":
                while actor(self.state):
                    self.run_level(self.prog[pc][1].level, pc)
                else:
                    pc = self.pass_level(self.prog[pc][1].level, pc)
            else:
                #print(self.source[lineno-1])
                state = self.new_state(lineno)
                actor(state)
                #print(state)
    
        return pc
    
    def run_prog(self):
        state = State(0)
        self.states = [state]
        state.hiddenState.update({'fillColor'       : nodes.Value("#000000"),
                                  'view_left'       : nodes.Value(0),
                                  'view_width'      : nodes.Value(100),
                                  'view_top'        : nodes.Value(0),
                                  'view_height'     : nodes.Value(100)
                                 })
        self.run_level(0, 0)
        return self.state
