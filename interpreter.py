
from program import Instruction, Step
from language import nodes

class InvalidIndent(Exception):
    pass

class ToManyInstruction(Exception):
    pass

class NamespaceDict:
    def __init__(self, parent = None):
        self.parent = parent
        self.dict   = {}

    def __getitem__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            if self.parent is None:
                raise
            return self.parent[name]

    def __setitem__(self, name, value):
        if self.parent and name in self.parent:
            self.parent[name] = value
        self.dict[name] = value

    def __contains__(self, name):
        if name in self.dict:
            return True
        if self.parent and name in self.parent:
            return True
        return False

    def keys(self):
        for key in sorted(self.dict.keys()):
            yield key
        if self.parent:
            for key in self.parent.keys():
                if key not in self.dict:
                    yield key

    def clone(self):
        clone = NamespaceDict()
        if self.parent:
            clone.parent = self.parent.clone()
        clone.dict.update({k:v.clone() for k,v in self.dict.items()})
        return clone

class State:
    def __init__(self, lineno):
        self.lineno = lineno
        self.shapes = []
        self.hiddenState = {}
        self.namespace = NamespaceDict()
        self.functions = {}

    def clone(self, lineno):
        clone = State(lineno)
        clone.shapes = self.shapes[:]
        clone.hiddenState = dict(self.hiddenState)
        clone.namespace = self.namespace.clone()
        clone.functions = dict(self.functions)
        return clone

    def child(self):
        child = State(self.lineno)
        child.shapes = self.shapes
        child.hiddenState = self.hiddenState
        child.namespace = NamespaceDict(self.namespace)
        child.functions = dict(self.functions)
        return child

    def __str__(self):
        return "<State %d\n%s\n%s\n%s\n>"%(self.lineno,self.shapes, self.hiddenState, self.namespace)

class Interpreter:
    def __init__(self, program):
        self.program = program
        self.program.connect("source_changed", self.on_source_changed)
        self.state = None

    def on_source_changed(self):
        self.parse_text()
        if self.valid:
            self.run_prog()

    def new_state(self, lineno, state):
        if not state:
            state = State(lineno)
            state.hiddenState.update({'fillColor'       : nodes.Value("#000000"),
                                      'view_left'       : nodes.Value(0),
                                      'view_width'      : nodes.Value(100),
                                      'view_top'        : nodes.Value(0),
                                      'view_height'     : nodes.Value(100)
                                 })
            state.hiddenState['fillColor'].opositColor = "#FFFFFF"
        else:
            state = state.clone(lineno)
        return state

    def parse_text(self):
        self.program.actors = []
        self.valid = True
        for line in self.program.source:
            if not line:
                continue
            if line.valid:
                if line.parsed.klass == "Builtin":
                    try:
                        actor = line.parsed(self.program.lib)
                    except KeyError:
                        self.valid = False
                        continue
                else:
                    actor = line.parsed()
                if actor:
                    self.program.actors.append(Instruction(line, actor))
            else:
                self.valid = False

    def pass_level(self, level, pc):
        while pc < len(self.program.actors) and self.program.actors[pc].level >= level:
            pc += 1
        return pc

    def set_help_run_level(self, level, pc, step):
        text = "Do this..."
        while pc < len(self.program.actors) and self.program.actors[pc].level >= level:
            step.add_help(self.program.actors[pc].lineno, text)
            text = "... and this"
            pc += 1

    def run_level(self, state, level, pc):
        while pc < len(self.program.actors):
            instruction = self.program.actors[pc]
            if instruction.level < level:
                break
            if instruction.level > level:
                raise InvalidIndent(pc, instruction.level, level, str(instruction.line))
            pc += 1
            try:
                if instruction.klass in ("_if", "_while"):
                    result = instruction.actor(state)
                    step = Step(instruction, state)
                    self.program.steps.append(step)
                    while result:
                        step.add_help(instruction.lineno, "cause %s is true..."%instruction.actor.get_help_text(state))
                        self.set_help_run_level(self.program.actors[pc].level, pc, step)
                        pc_, state = self.run_level(state, self.program.actors[pc].level, pc)
                        if instruction.klass == "_if":
                            pc = pc_
                            break
                        result = instruction.actor(state)
                        step = Step(instruction, state)
                        self.program.steps.append(step)
                    else:
                        step.add_help(instruction.lineno, "cause %s is false..."%instruction.actor.get_help_text(state))
                        pc = self.pass_level(self.program.actors[pc].level, pc)
                        step.add_help(self.program.actors[pc].lineno, "... go here")
                elif instruction.klass == "functionDef":
                    state = self.new_state(instruction.lineno, state)
                    instruction.actor(state)
                    state.functions[instruction.actor.name.v].pc = pc
                    step = Step(instruction, state)
                    self.program.steps.append(step)
                    step.add_help(instruction.lineno, "create the function %s"%instruction.actor.name.v)
                    pc = self.pass_level(self.program.actors[pc].level, pc)
                elif instruction.klass == "functionCall":
                    state = self.new_state(instruction.lineno, state)
                    step = Step(instruction, state)
                    step.add_help(instruction.lineno, "call the function %s..."%instruction.actor.name.v)
                    self.program.steps.append(step)
                    newState = state.child()
                    instruction.actor(newState)
                    pc_ = newState.functions[instruction.actor.name.v].pc
                    step.add_help(self.program.actors[pc_].lineno, "... so go here")
                    _, state_ = self.run_level(newState, self.program.actors[pc_].level, pc_)
                    state.hiddenState = state_.hiddenState
                    state.shapes = state_.shapes
                    state.namespace = state_.namespace.parent
                    step = Step(instruction, state)
                    step.add_help(instruction.lineno, "returning from function %s"%instruction.actor.name.v)
                    self.program.steps.append(step)
                else:
                    state = self.new_state(instruction.lineno, state)
                    instruction.actor(state)
                    step = Step(instruction, state)
                    step.add_help(instruction.lineno, instruction.actor.get_help(state))
                    self.program.steps.append(step)
            except KeyError as e:
                if not hasattr(e, "handled"):
                    e.handled = True
                    step = Step(instruction, state)
                    step.add_help(instruction.lineno, "%s is not a declared variable."%e.args)
                    self.program.steps.append(step)
                raise
            if self.program.to_many_step():
                help.add(instruction.lineno, "To many instruction at line %d"%instruction.lineno)
                raise ToManyInstruction()

        return pc, state
    
    def run_prog(self):
        self.program.init_steps()
        try:
            _, state = self.run_level(None, 0, 0)
        except ToManyInstruction:
            print("to many instruction")
        except:
            pass
        self.program.event("steps_changed")()
        self.program.displayedStep = len(self.program.steps)-1

