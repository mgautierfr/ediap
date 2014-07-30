
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

        self.vScrollbar['command'] = self.steps.yview
        self.hScrollbar['command'] = self.steps.xview
        self.steps['yscrollcommand'] = self.vScrollbar.set
        self.steps['xscrollcommand'] = self.hScrollbar.set
        self.helpers = (None, None)
        self.text = text
        self.program = program
        self.program.connect("steps_modified", self.update)
        self.program.connect("displayedStepChange", self.on_displayedStepChanged)
        self.changing = False

    def place(self):
        self.pack(fill="both", expand=1, side="right")

    def on_displayedStepChanged(self, step):
        if self.oldStep is not None:
            self.steps.itemconfig("step_%d"%self.oldStep, fill="black")
        self.oldStep = self.program.displayedStep
        if not self.changing:
            self.steps.xview_moveto(max(0, self.oldStep-5)/self.nbSteps)
        self.steps.itemconfig("step_%d"%self.oldStep , fill="red")

    def update(self, *args):
        self.steps.delete('all')
        for nb, step in enumerate(self.program.steps):
            pos = self.text.bbox("%d.0"%(step.lineno))
            if pos:
                id_ = self.steps.create_oval(pos[3]*nb, pos[1], pos[3]*(nb+1), pos[1]+pos[3], fill="black", tags=["step_%d"%nb])
                self.steps.tag_bind(id_, "<Enter>", get_enter_callback(self, nb))
        self.nbSteps = nb
        width = max(self.steps.bbox('all')[2], self.steps.winfo_width()-10)
        for line in self.program.source:
            pos = self.text.bbox("%d.0"%(line.lineno))
            if pos:
                self.steps.create_line(0, pos[1]+pos[3], width, pos[1]+pos[3])
        self.steps['scrollregion'] = self.steps.bbox('all')
        self.steps['xscrollincrement'] = 1.0/nb

