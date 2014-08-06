

import tkinter

class CanvasCreator:
    def __init__(self, canvas, ySize, yDelta, xSize):
        self.canvas = canvas
        self.ySize = ySize
        self.yDelta = yDelta
        self.xSize = xSize
        self.elements = []

    def finish(self):
        if sum(self.canvas.bbox(el)[2] for el in self.elements) <= self.xSize:
            lines = [self.elements]
        else:
            current_size = 0
            lines = [[]]
            for element in self.elements:
                elem_pos = self.canvas.bbox(element)
                elem_size = elem_pos[2]-elem_pos[0]
                if current_size and current_size+elem_size>=self.xSize:
                    lines.append([])
                    current_size = 0
                lines[-1].append(element)
                current_size += elem_size
        for lineno, elements in enumerate(lines):
            spaceLeft = self.xSize
            for element in reversed(elements):
                elem_pos = self.canvas.bbox(element)
                spaceLeft -= (elem_pos[2]-elem_pos[0])
                self.canvas.move(element, spaceLeft, self.yDelta+elem_pos[3]*lineno)

    def feed(self, type_, content):
        if type_ in ("text", "error"):
            self.elements.append(self.canvas.create_text(0, 0, text=content, anchor="nw", fill="red" if type_=="error" else "black"))
        elif type_=="color":
            self.elements.append(self.canvas.create_rectangle(0, 0, self.ySize*1.5, self.ySize, fill=content))
        elif type_=="shape":
            if content == "rectangle":
                self.elements.append(self.canvas.create_rectangle(0, 0, self.ySize*1.5, self.ySize))
            elif content=="ellipse":
                self.elements.append(self.canvas.create_oval(0, 0, self.ySize*1.5, self.ySize))
            elif content=="quad":
                self.elements.append(self.canvas.create_polygon(0, 0, 0, self.ySize, self.ySize*1.5, self.ySize, self.ySize, self.ySize/2))
            elif content=="triangle":
                self.elements.append(self.canvas.create_polygon(0, 0, 0, self.ySize, self.ySize*1.5, self.ySize))


class TextHelp(tkinter.Canvas):
    def __init__(self, parent, text, program):
        tkinter.Canvas.__init__(self, parent, width=200, background="white")
        self.text = text
        self.program = program
        self.program.connect("activeStep_changed", self.on_activeStep_changed)

    def on_activeStep_changed(self, *args):
        self.delete('all')
        if self.program.displayedStep is None:
            return
        step = self.program.steps[self.program.displayedStep]
        for lineno, what in step.help.items():
            pos = self.text.bbox("%d.0"%(lineno))
            if pos:
                _, yDelta, _, ySize = pos
                xSize =self.canvasx(self.winfo_width())
                creator = CanvasCreator(self, ySize, yDelta, xSize)
                for type_, content in what:
                    creator.feed(type_, content)
                creator.finish()

