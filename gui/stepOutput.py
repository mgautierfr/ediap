
import tkinter

def get_enter_callback(stepOutput, step):
    def callback(event):
        stepOutput.changing = True
        stepOutput.program.displayedStep = step
        stepOutput.changing = False
    return callback

class StepOutput(tkinter.Frame):
    def __init__(self, parent, text, program):
        tkinter.Frame.__init__(self, parent)
        self.oldStep = None
        #self.hScrollbar = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
        #self.hScrollbar.grid(column=0,
        #                     row=1,
        #                     sticky="nsew"
        #                    )
        self.steps = tkinter.Canvas(self, bg="white")
        self.steps.grid(column=0,
                        row=0,
                        sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        #self.hScrollbar['command'] = self.steps.xview
        #self.steps['xscrollcommand'] = self.hScrollbar.set
        self.text = text
        self.program = program
        self.program.connect("steps_changed", self.on_steps_changed)
        self.program.connect("activeStep_changed", self.on_activeStep_changed)
        self.changing = False
        self.nbSteps = 0

    def on_activeStep_changed(self, step):
        if self.oldStep is not None:
            self.steps.itemconfig("step_%d"%self.oldStep, fill="black")
        self.oldStep = self.program.displayedStep
        if not self.changing and self.nbSteps:
            self.steps.xview_moveto(max(0, self.oldStep-5)/self.nbSteps)
        if self.oldStep is not None:
            self.steps.itemconfig("step_%d"%self.oldStep , fill="red")

    def on_steps_changed(self, *args):
        step_size = 14
        self.steps.delete('all')
        if not self.program.steps:
            self.nbSteps = 0
        else:
            for nb, step in enumerate(self.program.steps):
                pos = self.text.bbox("%d.0"%(step.lineno))
                if pos:
                    fill = "red" if nb == self.program.displayedStep else "black"
                    id_ = self.steps.create_oval(step_size*nb, pos[1] ,step_size*(nb+1), pos[1]+step_size, fill=fill, tags=["step_%d"%nb])
                    self.steps.tag_bind(id_, "<Enter>", get_enter_callback(self, nb))
            self.nbSteps = nb + 1
            width = max(self.steps.bbox('all')[2], self.steps.winfo_width()-10)
            for lineno in range(len(self.program.source)):
                pos = self.text.bbox("%d.0"%(lineno))
                if pos:
                    self.steps.create_line(0, pos[1]+pos[3], width, pos[1]+pos[3])
            _, _, xEnd, _ = self.steps.bbox('all')
            self.steps['scrollregion'] = 0, 0, xEnd, self.steps.canvasy(self.steps.winfo_height())
            if self.nbSteps:
                self.steps['xscrollincrement'] = 1.0/self.nbSteps

