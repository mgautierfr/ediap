

import tkinter


class TextHelp(tkinter.Canvas):
    def __init__(self, parent, text, program):
        tkinter.Canvas.__init__(self, parent, width=150)
        self.text = text
        self.program = program
        self.program.connect("activeStep_changed", self.on_activeStep_changed)

    def place(self):
        self.pack(side="right", fill="y")

    
    def on_activeStep_changed(self, step):
        self.delete('all')
        step = self.program.steps[self.program.displayedStep]
        for lineno, text in step.help.items():
            pos = self.text.bbox("%d.0"%(lineno))
            if pos:
                self.create_text(0, pos[1], fill="black", text=text, anchor="nw", width=150, justify="right")
