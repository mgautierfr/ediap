
import utils
from language import grammar
from picoparse import NoMatch

class Line:
    def __init__(self, lineno, lineText):
        self.lineno = lineno
        self.update_text(lineText)

    @property
    def valid(self):
        return self.parsed is not None

    def update_text(self, text):
        self.text = text
        self.level = grammar.get_level(text)
        try:
            self.parsed = grammar.parse_instruction(self.text)
        except NoMatch:
            self.parsed = None

    def __bool__(self):
        return bool(self.text) and not self.text.isspace()

    def __str__(self):
        return self.text

class Instruction:
    def __init__(self, line, actor):
        self.line = line
        self.actor = actor

    @property
    def lineno(self):
        return self.line.lineno

    @property
    def level(self):
        return self.line.level

    @property
    def klass(self):
        return self.actor.klass

class Step:
    def __init__(self, instruction, state):
        self.instruction = instruction
        self.state = state
        self.help = {}

    @property
    def lineno(self):
        return self.instruction.lineno

    def add_help(self, lineno, content):
        self.help[lineno] = content

class ExtendList(list):
    def __getitem__(self, index):
        if index is None:
            return Step(None, list.__getitem__(self,-1).state)
        return list.__getitem__(self, index)

class Program(utils.EventSource):
    def __init__(self, lib):
        utils.EventSource.__init__(self)
        self.lib = lib
        self.source        = []
        self.actors        = []
        self.init_steps()
        self.current       = (None, None)
        self.watchdog      = 1000
        self.fileName      = None

    def to_many_step(self):
        return len(self.steps) >= self.watchdog

    def init_steps(self):
        self.steps = ExtendList()
        self._displayedStep = None

    def load_file(self, fileName):
        self.fileName = fileName
        self.source = []
        try:
            with open(fileName, 'r') as f:
                lines = f.readlines()
                if lines[-1] == "\n":
                    lines = lines[:-1]
                for lineno, line in enumerate(lines, 1):
                    self.source.append(Line(lineno, line[:-1]))
        except FileNotFoundError:
            pass

    def set_source(self, lines):
        self.source = []
        for lineno, line in enumerate(lines, 1):
            self.source.append(Line(lineno, line))

    def update_text(self, index, text):
        if index < len(self.source):
            if text != self.source[index].text:
                self.source[index].update_text(text)
        else:
            self.source.append(Line(index+1, text))

    def clean_after(self, index):
        self.source[index+1:] = []

    @property
    def displayedStep(self):
        return self._displayedStep

    @displayedStep.setter
    def displayedStep(self, value):
        if value is not None:
            value = min(value,  len(self.steps)-1)
            if value == -1:
                value = None
        self._displayedStep = value
        self.event("activeStep_changed")(value)

    def set_current(self, current):
        self.current = current
        self.event("current_changed")()

