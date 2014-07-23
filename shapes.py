
class Shape:
    """Represent a actor"""
    def __init__(self, lineno):
        self.lineno = lineno
        self.helper = None

    def show_helper(self, index, canvas):
        pass

    def hide_helper(self, canvas):
        if self.helper is not None:
            canvas.delete(self.helper[1])
        self.helper = None

    def update(self, canvas):
        pass


class Rectangle(Shape):
    def __init__(self, lineno, x0, y0, x1, y1, fillColor):
        Shape.__init__(self, lineno)
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.fillColor = fillColor

    def depend(self):
        return self.x0.depend()|self.y0.depend()|self.x1.depend()|self.y1.depend()|self.fillColor.depend()

    def draw(self, canvas):
        canvas.create_rectangle(self.x0(), self.y0(), self.x1(), self.y1(), fill=self.fillColor())
        if self.helper is not None:
            canvas.delete(self.helper[1])
            self.show_helper(self.helper[0], canvas)

    def show_helper(self, index, canvas):
        if index == 0:
            coords = self.get_x_helper_coords()
        if index == 1:
            coords = self.get_y_helper_coords()
        if index == 2:
            coords = self.get_w_helper_coords()
        if index == 3:
            coords = self.get_h_helper_coords()
        self.helper = (index, canvas.create_line(*coords, fill="red"))

    def get_x_helper_coords(self):
        y0 = self.y0()
        return 0, y0, self.x0(), y0

    def get_y_helper_coords(self):
        x0 = self.x0()
        return x0, 0, x0, self.y0()

    def get_h_helper_coords(self):
        middle_x = (self.x0()+self.x1())/2
        return middle_x, self.y0(), middle_x, self.y1()

    def get_w_helper_coords(self):
        middle_y = (self.y0()+self.y1())/2
        return self.x0(), middle_y, self.x1(), middle_y

class Ellipse(Rectangle):
    def draw(self, canvas):
        canvas.create_oval(self.x0(), self.y0(), self.x1(), self.y1(), fill=self.fillColor())
        if self.helper is not None:
            canvas.delete(self.helper[1])
            self.show_helper(self.helper[0], canvas)

    def get_x_helper_coords(self):
        middle_y = (self.y0()+self.y1())/2
        return 0, middle_y, self.x0(), middle_y

    def get_y_helper_coords(self):
        middle_x = (self.x0()+self.x1())/2
        return middle_x, 0, middle_x, self.y0()
