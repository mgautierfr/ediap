
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
