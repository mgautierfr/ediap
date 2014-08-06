

import tkinter

canvas_size = 200

class CanvasCreator:
    def __init__(self, canvas, pos):
        self.canvas = canvas
        self.pos = pos
        self.elements = []

    def finish(self):
        if sum(self.canvas.bbox(el)[2] for el in self.elements) <= canvas_size:
            lines = [self.elements]
        else:
            current_size = 0
            lines = [[]]
            for element in self.elements:
                elem_pos = self.canvas.bbox(element)
                elem_size = elem_pos[2]-elem_pos[0]
                if current_size+elem_size>=canvas_size:
                    lines.append([])
                    current_size = 0
                lines[-1].append(element)
                current_size += elem_size
        for lineno, elements in enumerate(lines):
            spaceLeft = canvas_size
            for element in reversed(elements):
                elem_pos = self.canvas.bbox(element)
                spaceLeft -= (elem_pos[2]-elem_pos[0])
                self.canvas.move(element, spaceLeft, self.pos[1]+elem_pos[3]*lineno)

    def feed(self, type_, content):
        if type_ in ("text", "error"):
            self.elements.append(self.canvas.create_text(0, 0, text=content, anchor="nw", fill="red" if type_=="error" else "black"))
        elif type_=="color":
            self.elements.append(self.canvas.create_rectangle(0, 0, self.pos[3]*1.5, self.pos[3], fill=content))
        elif type_=="shape":
            if content == "rectangle":
                self.elements.append(self.canvas.create_rectangle(0, 0, self.pos[3]*1.5, self.pos[3]))
            elif content=="ellipse":
                self.elements.append(self.canvas.create_oval(0, 0, self.pos[3]*1.5, self.pos[3]))
            elif content=="quad":
                self.elements.append(self.canvas.create_polygon(0, 0, 0, self.pos[3], self.pos[3]*1.5, self.pos[3], self.pos[3], self.pos[3]/2))
            elif content=="triangle":
                self.elements.append(self.canvas.create_polygon(0, 0, 0, self.pos[3], self.pos[3]*1.5, self.pos[3]))


class TextHelp(tkinter.Canvas):
    def __init__(self, parent, text, program):
        tkinter.Canvas.__init__(self, parent, width=canvas_size, background="white")
        self.text = text
        self.program = program
        self.program.connect("activeStep_changed", self.on_activeStep_changed)


    def on_activeStep_changed(self, step):
        self.delete('all')
        if self.program.displayedStep is None:
            return
        step = self.program.steps[self.program.displayedStep]
        for lineno, what in step.help.items():
            pos = self.text.bbox("%d.0"%(lineno))
            if pos:
                creator = CanvasCreator(self, pos)
                for type_, content in what:
                    creator.feed(type_, content)
                creator.finish()
