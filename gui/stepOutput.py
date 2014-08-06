
import tkinter

def get_enter_callback(stepOutput, step):
    def callback(event):
        stepOutput.changing = True
        stepOutput.program.displayedStep = step
        stepOutput.changing = False
    return callback

class StepOutput(tkinter.Canvas):
    def __init__(self, parent, text, program):
        tkinter.Canvas.__init__(self, parent, bg="white")
        self.oldStep = None
        self.text = text
        self.program = program
        self.program.connect("steps_changed", self.on_steps_changed)
        self.program.connect("activeStep_changed", self.on_activeStep_changed)
        self.changing = False
        self.nbSteps = 0

    def on_activeStep_changed(self, step):
        if self.oldStep is not None:
            self.itemconfig("step_%d"%self.oldStep, fill="black")
        self.oldStep = self.program.displayedStep
        if not self.changing and self.nbSteps:
            self.xview_moveto(max(0, self.oldStep-5)/self.nbSteps)
        if self.oldStep is not None:
            self.itemconfig("step_%d"%self.oldStep , fill="red")

    def on_steps_changed(self, *args):
        step_size = 14
        self.delete('all')
        if not self.program.steps:
            self.nbSteps = 0
        else:
            for nb, step in enumerate(self.program.steps):
                pos = self.text.bbox("%d.0"%(step.lineno))
                if pos:
                    fill = "red" if nb == self.program.displayedStep else "black"
                    id_ = self.create_oval(step_size*nb, pos[1] ,step_size*(nb+1), pos[1]+step_size, fill=fill, tags=["step_%d"%nb])
                    self.tag_bind(id_, "<Enter>", get_enter_callback(self, nb))
            self.nbSteps = nb + 1
            width = max(self.bbox('all')[2], self.winfo_width()-10)
            for lineno in range(len(self.program.source)):
                pos = self.text.bbox("%d.0"%(lineno))
                if pos:
                    self.create_line(0, pos[1]+pos[3], width, pos[1]+pos[3])
            _, _, xEnd, _ = self.bbox('all')
            self['scrollregion'] = 0, 0, xEnd, self.canvasy(self.winfo_height())
            if self.nbSteps:
                self['xscrollincrement'] = 1.0/self.nbSteps

