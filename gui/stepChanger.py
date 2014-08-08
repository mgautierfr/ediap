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


import tkinter

class StepChanger(tkinter.Scale):
    def __init__(self, parent, program):
        self.activeStep = tkinter.IntVar(parent)
        tkinter.Scale.__init__(self, parent, variable=self.activeStep,
                                             orient=tkinter.HORIZONTAL)
        self.program = program
        self.program.connect("steps_changed", self.on_steps_changed)
        self.program.connect("activeStep_changed", self.on_activeStep_changed)
        self.activeStep.trace("w", self.showStep)

    def on_steps_changed(self):
        if self.program.steps:
            self['from'] = 1
            self['to'] = len(self.program.steps)
        else:
            self['from'], self['to'] = 0, 0

    def on_activeStep_changed(self, step):
        if step is None:
            self.activeStep.set(0)
        else:
            self.activeStep.set(step+1)

    def showStep(self, *args):
        self.program.displayedStep = self.activeStep.get()-1

