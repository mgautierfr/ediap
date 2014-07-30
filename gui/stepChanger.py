
import tkinter

class StepChanger(tkinter.Scale):
    def __init__(self, parent, program):
        self.activeStep = tkinter.IntVar(parent)
        tkinter.Scale.__init__(self, parent, variable=self.activeStep,
                                             orient=tkinter.HORIZONTAL)
        self.program = program
        self.program.connect("steps_modified", self.on_stepModified)
        self.program.connect("displayedStepChange", self.on_displayedStepChanged)
        self.activeStep.trace("w", self.showStep)

    def place(self):
        self.pack(side="top", fill="x", expand=1)

    def on_stepModified(self):
        self['to'] = len(self.program.steps)-1

    def on_displayedStepChanged(self, step):
        self.activeStep.set(step)

    def showStep(self, *args):
        self.program.displayedStep = self.activeStep.get()
