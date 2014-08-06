
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

