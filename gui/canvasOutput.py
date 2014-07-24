
import tkinter

class CanvasOutput(tkinter.Canvas):
    def __init__(self, parent):
        tkinter.Canvas.__init__(self, parent, bg="white")
        self.helpers = (None, None)
        self.saveState = None

    def place(self):
        self.pack(side="right")
        

    def update(self,):
        state = self.interpretor.state
        self.saveState = state
        self.delete('all')
        for shape in state.shapes:
            shape.draw(self)
            if shape.lineno == self.helpers[0]:
                shape.draw_helper(self.helpers[1], self)

    def show_helper(self, lineno, index):
        self.helpers = (lineno, index)
        self.update()

    def hide_helpers(self):
        self.helpers = (None, None)
        self.update()
