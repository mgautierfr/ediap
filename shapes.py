

class Rectangle:
    def __init__(self, x0, y0, x1, y1, fillColor):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.fillColor = fillColor

    def draw(self, canvas):
        return canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill=self.fillColor)

class Ellipse(Rectangle):
    def __init__(self, x0, y0, x1, y1, fillColor):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.fillColor = fillColor

    def draw(self, canvas):
        return canvas.create_oval(self.x0, self.y0, self.x1, self.y1, fill=self.fillColor)
