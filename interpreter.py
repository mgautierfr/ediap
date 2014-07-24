
import grammar
from picoparse import NoMatch
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
    def __init__(self, textInput, textTagger, canvas, stepOutput):
        self.textInput = textInput
        self.textTagger = textTagger
        self.canvas = canvas
        self.stepOutput = stepOutput
        self.textInput.bind("<<Modified>>", self.on_modified, add="+")
        self.steps = []
        self.state = None
        self.activeState = None
        self.watchdog = 10000

    def on_modified(self, *args):
        if not self.textInput.edit_modified():
            return
        self.textInput.edit_modified(False)

        if not self.textTagger.changing:
            #This is not a direct change from textTagger.
            # => Need to parse all text again
            self.parse_text()
            if self.valid:
                self.run_prog()

        if self.valid:
            self.canvas.update(self.activeState)
            self.stepOutput.update(self)

    def set_activeState(self, state):
        self.activeState = state
        self.canvas.update(state)

    def new_state(self, lineno):
        if not self.state:
            self.state = State(lineno)
            self.state.hiddenState.update({'fillColor'       : nodes.Value("#000000"),
                                      'view_left'       : nodes.Value(0),
                                      'view_width'      : nodes.Value(100),
                                      'view_top'        : nodes.Value(0),
                                      'view_height'     : nodes.Value(100)
                                 })
        else:
            self.state = self.state.new_child(lineno)
        return self.state

    def parse_text(self):
        self.prog = []
        self.source = self.textInput.get_source()
        self.textInput.clean_tags()
        self.valid = True
        for lineno, line in self.source:
            if not line or line.isspace():
                continue
            try:
                instruction = grammar.parse_instruction(line)
                self.textTagger.tag_line(lineno, instruction)
            except NoMatch:
                level = grammar.get_level(line)
                self.textInput.tag_add("invalidSyntax", "%d.%d"%(lineno, level), "%d.0 lineend"%lineno)
                self.valid = False
                continue
            if self.valid:
                actor = instruction()
                self.prog.append((lineno, actor))

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
            if actor.klass in ("_if", "_while"):
                result = actor(self.state)
                self.steps.append((lineno, self.state))
                while result:
                    pc_ = self.run_level(self.prog[pc][1].level, pc)
                    if actor.klass == "_if":
                        pc = pc_
                        break
                    result = actor(self.state)
                    self.steps.append((lineno, self.state))
                else:
                    pc = self.pass_level(self.prog[pc][1].level, pc)
            else:
                #print(self.source[lineno-1])
                state = self.new_state(lineno)
                actor(state)
                self.steps.append((lineno, self.state))
                #print(state)
            
    
        return pc
    
    def run_prog(self):
        self.state = None
        self.steps = []
        self.run_level(0, 0)
        self.activeState = self.state
        return self.state
