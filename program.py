
import utils
import grammar
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

    def __true__(self):
        return line and not line.isspace()

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

    @property
    def lineno(self):
        return self.instruction.lineno

class ExtendList(list):
    def __getitem__(self, index):
        if index is None:
            return Step(None, self[-1].state)
        return list.__getitem__(self, index)

class Program(utils.EventSource):
    def __init__(self):
        utils.EventSource.__init__(self)
        self.source        = []
        self.actors        = []
        self.init_steps()
        self.helpers       = (None, None)

    def init_steps(self):
        self.steps = ExtendList()
        self._displayedStep = None

    def set_source(self, lines):
        self.source = []
        for lineno, line in enumerate(lines, 1):
            self.source.append(Line(lineno, line))

    def update_text(self, lineno, text, do_event):
        self.source[lineno].update_text(text)
        if do_event:
            self.event("source_changed")()

    @property
    def displayedStep(self):
        return self._displayedStep

    @displayedStep.setter
    def displayedStep(self, value):
        self._displayedStep = value
        self.event("activeStep_changed")(value)

    def show_helper(self, lineno, index):
        self.helpers = (lineno, index)
        self.event("activeStep_changed")(self._displayedStep)

    def hide_helpers(self):
        self.helpers = (None, None)
        self.event("activeStep_changed")(self._displayedStep)
