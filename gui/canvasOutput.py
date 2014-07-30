
import tkinter

class CanvasOutput(tkinter.Frame):
    def __init__(self, parent, program):
        tkinter.Frame.__init__(self, parent)
        self.canvas = tkinter.Canvas(self, bg="white")
        self.canvas.pack(side="top")
        self.fillColor = tkinter.Label(self, text="fillColor")
        self.fillColor.pack()
        self.program = program
        self.program.connect("token_changed", self.on_stepChanged)
        self.program.connect("displayedStepChange", self.on_stepChanged)
        self.idle_handle = None

    def on_stepChanged(self, *args):
        if self.idle_handle is not None:
            self.after_cancel(self.idle_handle)
        self.idle_handle = self.after(0, self.update)

    def place(self):
        self.pack(side="right")
        
    def update(self):
        state = self.program.steps[self.program.displayedStep].state
        self.idle_handle = None
        self.canvas.delete('all')
        for shape in state.shapes:
            shape.draw(self.canvas)
            if shape.lineno == self.program.helpers[0]:
                shape.draw_helper(self.program.helpers[1], self.canvas)
        self.fillColor['bg'] = state.hiddenState['fillColor']()

