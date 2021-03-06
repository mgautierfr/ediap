# This file is part of Edia.
#
# Ediap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Edia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edia.  If not, see <http://www.gnu.org/licenses/>

# Copyright 2014 Matthieu Gautier dev@mgautier.fr


import utils
from language import grammar
from picoparse import NoMatch

class Line:
    def __init__(self, lineno, lineText):
        self.lineno = lineno
        self.update_text(lineText)

    def update_text(self, text):
        self.text = text
        self.empty = not bool(self.text) or self.text.isspace()
        self.level = None
        self.parsed = None
        if not self.empty:
            self.level = grammar.get_level(text)
            try:
                self.parsed = grammar.parse_instruction(self.text)
            except NoMatch:
                self.parsed = None

    def __bool__(self):
        raise NotImplemented

    def __str__(self):
        return self.text

    @property
    def is_nop(self):
        if self.parsed is None:
            return True
        return self.parsed.is_nop

    @property
    def klass(self):
        if self.parsed is None:
            return None
        return self.parsed.klass

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

