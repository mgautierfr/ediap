
import tkinter

class CanvasOutput(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.canvas = tkinter.Canvas(self, bg="white")
        self.canvas.pack(side="top")
        self.fillColor = tkinter.Label(self, text="fillColor")
        self.fillColor.pack()
        self.helpers = (None, None)
        self.shownState = None

    def place(self):
        self.pack(side="right")
        
    def update(self, state=None):
        if state is None:
            state = self.shownState
        if state is None:
            return
        self.shownState = state
        self.canvas.delete('all')
        for shape in state.shapes:
            shape.draw(self.canvas)
            if shape.lineno == self.helpers[0]:
                shape.draw_helper(self.helpers[1], self.canvas)
        self.fillColor['bg'] = state.hiddenState['fillColor']()

    def show_helper(self, lineno, index):
        self.helpers = (lineno, index)
        self.update()

    def hide_helpers(self):
        self.helpers = (None, None)
        self.update()
