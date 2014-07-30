
from program import Instruction, Step
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
        return child

    def __str__(self):
        return "<State %d\n%s\n%s\n%s\n>"%(self.lineno,self.shapes, self.hiddenState, self.namespace)

class Interpreter:
    def __init__(self, program):
        self.program = program
        self.program.connect("source_modified", self.on_source_modified)
        self.state = None
        self.watchdog = 10000

    def on_source_modified(self, directChange):
        if not directChange:
            #This is not a direct change from textTagger.
            # => Need to parse all text again
            self.parse_text()
            if self.valid:
                self.run_prog()

        if self.valid:
            self.program.event("steps_modified")()

    def new_state(self, lineno, state):
        if not state:
            state = State(lineno)
            state.hiddenState.update({'fillColor'       : nodes.Value("#000000"),
                                      'view_left'       : nodes.Value(0),
                                      'view_width'      : nodes.Value(100),
                                      'view_top'        : nodes.Value(0),
                                      'view_height'     : nodes.Value(100)
                                 })
        else:
            state = state.new_child(lineno)
        return state

    def parse_text(self):
        self.program.actors = []
        self.valid = True
        for line in self.program.source:
            if not line:
                continue
            if line.valid:
                actor = line.parsed()
                self.program.actors.append(Instruction(line, actor))
            else:
                self.valid = False

    def pass_level(self, level, pc):
        while pc < len(self.program.actors) and self.program.actors[pc].level >= level:
            pc += 1
        return pc

    def run_level(self, state, level, pc):
        while pc < len(self.program.actors):
            instruction = self.program.actors[pc]
            self.watchdog -= 1
            if not self.watchdog:
                raise ToManyInstruction()
            if instruction.level < level:
                break
            if instruction.level > level:
                raise InvalidIndent(pc, instruction.level, level)
            pc += 1
            if instruction.klass in ("_if", "_while"):
                result = instruction.actor(state)
                self.program.steps.append(Step(instruction, state))
                while result:
                    pc_, state = self.run_level(state, self.program.actors[pc].level, pc)
                    if instruction.klass == "_if":
                        pc = pc_
                        break
                    result = instruction.actor(state)
                    self.program.steps.append(Step(instruction, state))
                else:
                    pc = self.pass_level(self.program.actors[pc].level, pc)
            else:
                #print(self.source[lineno-1])
                state = self.new_state(instruction.lineno, state)
                instruction.actor(state)
                self.program.steps.append(Step(instruction, state))
                #print(state)

        return pc, state
    
    def run_prog(self):
        self.program.init_steps()
        _, state = self.run_level(None, 0, 0)
        self.program.event("steps_modified")()
        self.program.displayedStep = len(self.program.steps)-1

