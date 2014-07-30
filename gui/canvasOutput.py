
import tkinter

class CanvasOutput(tkinter.Frame):
    def __init__(self, parent, program):
        tkinter.Frame.__init__(self, parent)
        self.canvas = tkinter.Canvas(self, bg="white")
        self.canvas.pack(side="top")
        self.fillColor = tkinter.Label(self, text="fillColor")
        self.fillColor.pack()
        self.program = program
        self.program.connect("steps_modified", self.on_stepChanged)
        self.program.connect("displayedStepChange", self.on_stepChanged)

    def on_stepChanged(self, *args):
        self.update(self.program.steps[self.program.displayedStep].state)

    def place(self):
        self.pack(side="right")
        
    def update(self, state):
        self.canvas.delete('all')
        for shape in state.shapes:
            shape.draw(self.canvas)
            if shape.lineno == self.program.helpers[0]:
                shape.draw_helper(self.program.helpers[1], self.canvas)
        self.fillColor['bg'] = state.hiddenState['fillColor']()

