
class Shape:
    """Represent a actor"""
    def __init__(self, lineno):
        self.lineno = lineno
        self.helper = None

    def draw(self, canvas):
        pass

    def draw_helper(self, index, canvas):
        pass


class Rectangle(Shape):
    def __init__(self, lineno, x0, y0, x1, y1, fillColor):
        Shape.__init__(self, lineno)
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.fillColor = fillColor

    def depend(self):
        return self.x0.depend()|self.y0.depend()|self.x1.depend()|self.y1.depend()|self.fillColor.depend()

    def draw(self, canvas):
        x0 = self.x0()*canvas.winfo_width()
        y0 = self.y0()*canvas.winfo_height()
        x1 = self.x1()*canvas.winfo_width()
        y1 = self.y1()*canvas.winfo_height()
        self.shapeid = canvas.create_rectangle(x0, y0, x1, y1, fill=self.fillColor())

    def update(self, canvas):
        x0 = self.x0()*canvas.winfo_width()
        y0 = self.y0()*canvas.winfo_height()
        x1 = self.x1()*canvas.winfo_width()
        y1 = self.y1()*canvas.winfo_height()
        canvas.coords(self.shapeid, x0, y0, x1, y1)
        canvas.item_config(self.shapeid, fill=self.fillColor())

    def draw_helper(self, index, canvas):
        if index == 0:
            coords = self.get_x_helper_coords(canvas)
        if index == 1:
            coords = self.get_y_helper_coords(canvas)
        if index == 2:
            coords = self.get_w_helper_coords(canvas)
        if index == 3:
            coords = self.get_h_helper_coords(canvas)
        canvas.create_line(*coords, fill="red", tags="helpers")

    def get_x_helper_coords(self, canvas):
        y0 = self.y0()*canvas.winfo_height()
        return 0, y0, self.x0()*canvas.winfo_width(), y0

    def get_y_helper_coords(self, canvas):
        x0 = self.x0()*canvas.winfo_width()
        return x0, 0, x0, self.y0()*canvas.winfo_height()

    def get_h_helper_coords(self, canvas):
        middle_x = (self.x0()+self.x1())/2*canvas.winfo_width()
        return middle_x, self.y0()*canvas.winfo_height(), middle_x, self.y1()*canvas.winfo_height()

    def get_w_helper_coords(self, canvas):
        middle_y = (self.y0()+self.y1())/2*canvas.winfo_height()
        return self.x0()*canvas.winfo_width(), middle_y, self.x1()*canvas.winfo_width(), middle_y

class Ellipse(Rectangle):
    def draw(self, canvas):
        x0 = self.x0()*canvas.winfo_width()
        y0 = self.y0()*canvas.winfo_height()
        x1 = self.x1()*canvas.winfo_width()
        y1 = self.y1()*canvas.winfo_height()
        canvas.create_oval(x0, y0, x1, y1, fill=self.fillColor())

    def get_x_helper_coords(self, canvas):
        middle_y = (self.y0()+self.y1())/2*canvas.winfo_height()
        return 0, middle_y, self.x0()*canvas.winfo_width(), middle_y

    def get_y_helper_coords(self, canvas):
        middle_x = (self.x0()+self.x1())/2*canvas.winfo_width()
        return middle_x, 0, middle_x, self.y0()*canvas.winfo_height()

