
from program import Step
from language import objects

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
    def __init__(self, lineno, context):
        self.lineno = lineno
        self.context = context
        self.namespace = NamespaceDict()
        self.functions = {}

    def clone(self, lineno):
        clone = State(lineno, self.context.__class__(self.context))
        clone.namespace = self.namespace.clone()
        clone.functions = dict(self.functions)
        return clone

    def child(self):
        child = State(self.lineno, self.context)
        child.namespace = NamespaceDict(self.namespace)
        child.functions = dict(self.functions)
        return child

    def __str__(self):
        return "<State %d\n%s\n%s\n>"%(self.lineno,self.context, self.namespace)

class Interpreter:
    def __init__(self, program):
        self.program = program
        self.program.connect("source_changed", self.run_prog)
        self.state = None

    def new_state(self, lineno, state):
        if not state:
            newContext = self.program.lib.Context()
            state = State(lineno, newContext)
        else:
            state = state.clone(lineno)
        return state

    def block_runner(self, pc):
        try:
            while self.program.source[pc].is_nop:
                pc += 1
            level = self.program.source[pc].level
            while True:
                if self.program.source[pc].is_nop:
                    pc += 1
                    continue
                if self.program.source[pc].level < level:
                    break
                newpc = yield pc
                if newpc is not None:
                    pc = newpc
                else:
                    pc += 1
        except IndexError:
            raise StopIteration

    def pass_level(self, pc):
        runner = self.block_runner(pc)
        for pc in runner:
            pass
        #pc is the last of the block, get next
        pc += 1
        try:
            while self.program.source[pc].is_nop:
                pc += 1
        except IndexError:
            pass
        return pc

    def set_help_run_level(self, pc, step):
        text = "Do this..."
        runner = self.block_runner(pc)
        for pc in runner:
            step.add_help(self.program.source[pc].lineno, [('text', text)])
            text = "... and this"

    def run(self, pc, state):
        runner = self.block_runner(pc)
        level = None
        pc = next(runner)
        while True:
            instruction = self.program.source[pc]
            if level is None:
                level = instruction.level
            if instruction.level > level:
                raise InvalidIndent(pc, instruction.level, level, str(instruction))
            try:
                pc, state = Interpreter.instruction_mapping[instruction.klass](self, instruction, pc, state)
                try:
                    pc = runner.send(pc)
                except StopIteration:
                    break
            except KeyError as e:
                if not hasattr(e, "handled"):
                    e.handled = True
                    step = Step(instruction, state)
                    step.add_help(instruction.lineno, [('error', "%s is not a declared variable."%e.args)])
                    self.program.steps.append(step)
                raise
            if self.program.to_many_step():
                step.add_help(instruction.lineno, [('error', "To many instruction at line %d"%instruction.lineno)])
                raise ToManyInstruction()

        return pc, state

    def do_if(self, instruction, pc, state):
        step = Step(instruction, state)
        self.program.steps.append(step)
        result_node = instruction.parsed.test.get_node(state.namespace)
        result = result_node()
        if result:
            step.add_help(instruction.lineno, [('text', "%s is true so ..."%instruction.parsed.test.get_help_text(state.namespace))])
            self.set_help_run_level(pc+1, step)
            pc, state = self.run(pc+1, state)
        else:
            step.add_help(instruction.lineno, [('text', "%s is false so..."%instruction.parsed.test.get_help_text(state.namespace))])
            pc = self.pass_level(pc+1)
            try:
                step.add_help(self.program.source[pc].lineno, [('text', "... go here")])
            except IndexError:
                pass
        return pc, state

    def do_while(self, instruction, pc, state):
        step = Step(instruction, state)
        self.program.steps.append(step)
        result_node = instruction.parsed.test.get_node(state.namespace)
        result = result_node()
        while result:
            step.add_help(instruction.lineno, [('text', "%s is true so ..."%instruction.parsed.test.get_help_text(state.namespace))])
            self.set_help_run_level(pc+1, step)
            pc_, state = self.run(pc+1, state)
            result_node = instruction.parsed.test.get_node(state.namespace)
            result = result_node()
            step = Step(instruction, state)
            self.program.steps.append(step)
        else:
            step.add_help(instruction.lineno, [('text', "%s is false so ..."%instruction.parsed.test.get_help_text(state.namespace))])
            pc = self.pass_level(pc+1)
            try:
                step.add_help(self.program.source[pc].lineno, [('text', "... go here")])
            except IndexError:
                pass
        return pc, state

    def do_create_subprogram(self, instruction, pc, state):
        state = self.new_state(instruction.lineno, state)
        state.functions[instruction.parsed.name.v] = objects.FunctionDefinition(instruction.parsed.name.v, [(t.v, a.v) for t,a in instruction.parsed.args])
        state.functions[instruction.parsed.name.v].pc = pc+1
        step = Step(instruction, state)
        self.program.steps.append(step)
        step.add_help(instruction.lineno, [('text', "create the function %s"%instruction.parsed.name.v)])
        pc = self.pass_level(pc+1)
        return pc, state

    def do_do_subprogram(self, instruction, pc, state):
        step = Step(instruction, state)
        self.program.steps.append(step)
        step.add_help(instruction.lineno, [('text', "call the function %s..."%instruction.parsed.name.v)])

        #This will be the state after the subprogram call.
        state = self.new_state(instruction.lineno, state)
        #This will be the state the subprogram will receive
        newState = state.child()
        functionDef = newState.functions[instruction.parsed.name.v]
        for argTypeName, arg in zip(functionDef.args, instruction.parsed.args):
            argType, argName = argTypeName
            if argType == "var":
                var = objects.Variable()
            newState.namespace.dict[argName] = var
            var.set(arg.get_node(newState.namespace))

        step.add_help(self.program.source[functionDef.pc].lineno, [('text', "... so go here")])
        _, state_ = self.run(functionDef.pc, newState)
        #Update our final state with data return from subprogram
        state.context = state_.context
        state.namespace = state_.namespace.parent
        step = Step(instruction, state)
        step.add_help(instruction.lineno, [('text', "returning from function %s"%instruction.parsed.name.v)])
        self.program.steps.append(step)
        return pc+1, state

    def do_create(self, instruction ,pc, state):
        state = self.new_state(instruction.lineno, state)
        if instruction.parsed.type_.v == "var":
            var = objects.Variable()
        state.namespace[instruction.parsed.name.v] = var
        step = Step(instruction, state)
        step.add_help(instruction.lineno, [('text', "create variable %s"%instruction.parsed.name.v)])
        self.program.steps.append(step)
        return pc+1, state

    def do_set(self, instruction, pc, state):
        state = self.new_state(instruction.lineno, state)
        state.namespace[instruction.parsed.name.v].set(instruction.parsed.value.get_node(state.namespace))
        step = Step(instruction, state)
        step.add_help(instruction.lineno, [('text', "set variable %s to %s"%(instruction.parsed.name.v, instruction.parsed.value.get_help_text(state.namespace)))])
        self.program.steps.append(step)
        return pc+1, state

    def do_builtin(self, instruction, pc, state):
        state = self.new_state(instruction.lineno, state)
        builtinClass = getattr(self.program.lib, instruction.parsed.name.v)
        # this is a builtin call
        builtin = builtinClass(state, *instruction.parsed.args)
        builtin.act()
        step = Step(instruction, state)
        step.add_help(instruction.lineno, builtin.get_help())
        self.program.steps.append(step)
        return pc+1, state

    def nop(self, instruction, pc, state):
        return pc+1, state
    
    def run_prog(self):
        previous_activeStep = self.program.displayedStep
        last = (previous_activeStep == len(self.program.steps)-1)
        self.program.init_steps()
        try:
            _, state = self.run(0, None)
        except:
            previous_activeStep = len(self.program.steps)-1
            raise
        self.program.event("steps_changed")()
        if previous_activeStep is None or last:
            previous_activeStep = len(self.program.steps)-1
        self.program.displayedStep = previous_activeStep

    instruction_mapping = {
     'If'                : do_if,
     'While'             : do_while,
     'Create_subprogram' : do_create_subprogram,
     'Do_subprogram'     : do_do_subprogram,
     'Create'            : do_create,
     'Set'               : do_set,
     'Builtin'           : do_builtin,
     'Comment'           : nop,
     None                : nop
    }

