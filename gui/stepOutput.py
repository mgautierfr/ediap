
import tkinter

def get_enter_callback(stepOutput, lineno, state, step):
    def callback(event):
        stepOutput.text.tag_add("highlihgt", "%d.0"%lineno, "%d.0 +1l"%lineno)
        stepOutput.interpretor.set_activeState(state)
        stepOutput.steps.itemconfig("step_%d"%stepOutput.oldStep , fill="black")      
        stepOutput.activeStep.set(step)
        stepOutput.steps.itemconfig("step_%d"%step, fill="red")
    return callback

class StepOutput(tkinter.Frame):
    def __init__(self, parent, text):
        tkinter.Frame.__init__(self, parent)
        self.activeStep = tkinter.IntVar(self)
        self.oldStep = None
        self.stepExplorer = tkinter.Scale(self, variable=self.activeStep,
                                                orient=tkinter.HORIZONTAL)
        self.stepExplorer.grid(column=0,
                             row=2,
                             sticky="nsew",
                             columnspan=2
                            )
        self.hScrollbar = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
        self.hScrollbar.grid(column=0,
                             row=1,
                             sticky="nsew"
                            )
        self.vScrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        self.vScrollbar.grid(column=1,
                             row=0,
                             sticky="nsew")
        self.steps = tkinter.Canvas(self, bg="white")
        self.steps.grid(column=0,
                        row=0,
                        sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.activeStep.trace("w", self.showStep)
        self.vScrollbar['command'] = self.steps.yview
        self.hScrollbar['command'] = self.steps.xview
        self.steps['yscrollcommand'] = self.vScrollbar.set
        self.steps['xscrollcommand'] = self.hScrollbar.set
        self.helpers = (None, None)
        self.text = text

    def place(self):
        self.pack(fill="both", expand=1, side="right")

    def showStep(self, *args):
        if self.oldStep:
            self.steps.itemconfig("step_%d"%self.oldStep, fill="black")
        self.oldStep = self.activeStep.get()
        self.steps.xview_moveto(max(0, self.oldStep-5)/self.nbSteps)
        self.steps.itemconfig("step_%d"%self.oldStep , fill="red")
        _, state = self.interpretor.steps[int(self.oldStep)]
        self.interpretor.set_activeState(state)

    def update(self, interpretor):
        self.steps.delete('all')
        for nb, lineno_state in enumerate(interpretor.steps):
            lineno, state = lineno_state
            pos = self.text.bbox("%d.0"%(lineno))
            if pos:
                id_ = self.steps.create_oval(pos[3]*nb, pos[1], pos[3]*(nb+1), pos[1]+pos[3], fill="black", tags=["step_%d"%nb])
                self.steps.tag_bind(id_, "<Enter>", get_enter_callback(self, lineno, state, nb))
                self.steps.tag_bind(id_, "<Leave>", lambda e, l=lineno :self.text.tag_remove("highlihgt", "1.0", "end"))
        self.nbSteps = nb
        width = max(self.steps.bbox('all')[2], self.steps.winfo_width()-10)
        for lineno ,line in interpretor.source:
            pos = self.text.bbox("%d.0"%(lineno))
            if pos:
                self.steps.create_line(0, pos[1]+pos[3], width, pos[1]+pos[3])
        self.steps['scrollregion'] = self.steps.bbox('all')
        self.steps['xscrollincrement'] = 1.0/nb
        self.stepExplorer['to'] = nb

