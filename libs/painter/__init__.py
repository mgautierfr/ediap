
import tkinter

from .actors import *
from language import nodes


class Context:
    def __init__(self, other=None):
        if other is None:
            self.fillColor = nodes.Value("#000000")
            self.fillColor.opositColor = "#FFFFFF"
            self.shapes = []
        else:
            self.fillColor = other.fillColor
            self.shapes = other.shapes[:]

    def __str__(self):
        return "<PainterContext\n%s\n%s>"%(self.fillColor, self.shapes)

class ContextShower(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.canvas = tkinter.Canvas(self, bg="white")
        self.canvas['height'] = self.canvas['width']
        self.canvas.pack(side="top")
        self.canvasState = tkinter.ttk.Treeview(self, columns=('value',))
        self.canvasState['height'] = 1
        self.canvasState.pack()

    def delete(self, what):
        self.canvas.delete(what)

    def draw(self, context, token, shape_=True):
        for shape in context.shapes:
            if shape_:
                shape.draw(self.canvas)
            elif shape_ is False:
                shape.update(self.canvas)
            if token in shape.depend():
                shape.draw_helper(token, self.canvas)

    def update_hiddenstate(self, context):
        for child in self.canvasState.get_children():
            self.canvasState.delete(child)
        value = context.fillColor()
        self.canvasState.insert("", "end", "fillColor", text="fillColor", value=value, tags=("fillColor",))
        self.canvasState.tag_configure("fillColor", background=value, foreground=context.fillColor.opositColor)

