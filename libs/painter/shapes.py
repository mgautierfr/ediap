# This file is part of Edia.
#
# Ediap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Edia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edia.  If not, see <http://www.gnu.org/licenses/>

# Copyright 2014 Matthieu Gautier dev@mgautier.fr

class Shape:
    """Represent a actor"""
    def __init__(self, lineno):
        self.lineno = lineno

    def draw(self, canvas):
        pass

    def draw_helper(self, index, canvas):
        pass

class Line(Shape):
    def __init__(self, lineno, fillColor, width, coords):
        Shape.__init__(self, lineno)
        self.fillColor = fillColor
        self.width = width
        self.coords = coords

    def depend(self):
        return self.fillColor.depend().union(*[c.depend() for c in self.coords])

    def draw(self, canvas):
        coords = (c()*(canvas.winfo_height() if i%2 else canvas.winfo_width()) for i,c in enumerate(self.coords))
        coords = [c/100 for c in coords]
        self.shapeid = canvas.create_line(*coords, fill=self.fillColor(), width=self.width())

    def update(self, canvas):
        coords = (c()*(canvas.winfo_height() if i%2 else canvas.winfo_width()) for i, c in enumerate(self.coords))
        coords = [c/100 for c in coords]
        canvas.coords(self.shapeid, *coords)
        canvas.itemconfig(self.shapeid, fill=self.fillColor(), width=self.width())

    def draw_helper(self, token, canvas):
        for index, coord in enumerate(self.coords):
            if token in coord.depend():
                if index%2:
                    coords = self.get_y_helper_coords(self.coords[index-1], self.coords[index], canvas)
                else:
                    coords = self.get_x_helper_coords(self.coords[index], self.coords[index+1], canvas)
                canvas.create_line(*coords, fill="red", tags="helpers")

    def get_x_helper_coords(self, x, y, canvas):
        y = y()*canvas.winfo_height()/100
        return 0, y, x()*canvas.winfo_width()/100, y

    def get_y_helper_coords(self, x, y, canvas):
        x = x()*canvas.winfo_width()/100
        return x, 0, x, y()*canvas.winfo_height()/100

class Polygon(Shape):
    def __init__(self, lineno, fillColor, coords):
        Shape.__init__(self, lineno)
        self.fillColor = fillColor
        self.coords = coords

    def depend(self):
        return self.fillColor.depend().union(*[c.depend() for c in self.coords])

    def draw(self, canvas):
        coords = (c()*(canvas.winfo_height() if i%2 else canvas.winfo_width()) for i, c in enumerate(self.coords))
        coords = [c/100 for c in coords]
        self.shapeid = canvas.create_polygon(*coords, fill=self.fillColor())

    def update(self, canvas):
        coords = (c()*(canvas.winfo_height() if i%2 else canvas.winfo_width()) for i, c in enumerate(self.coords))
        coords = [c/100 for c in coords]
        canvas.coords(self.shapeid, *coords)
        canvas.itemconfig(self.shapeid, fill=self.fillColor())

    def draw_helper(self, token, canvas):
        for index, coord in enumerate(self.coords):
            if token in coord.depend():
                if index%2:
                    coords = self.get_y_helper_coords(self.coords[index-1], self.coords[index], canvas)
                else:
                    coords = self.get_x_helper_coords(self.coords[index], self.coords[index+1], canvas)
                canvas.create_line(*coords, fill="red", tags="helpers")

    def get_x_helper_coords(self, x, y, canvas):
        y = y()*canvas.winfo_height()/100
        return 0, y, x()*canvas.winfo_width()/100, y

    def get_y_helper_coords(self, x, y, canvas):
        x = x()*canvas.winfo_width()/100
        return x, 0, x, y()*canvas.winfo_height()/100


class Rectangle(Shape):
    def __init__(self, lineno, x, y, w, h, fillColor):
        Shape.__init__(self, lineno)
        self.x, self.y, self.w, self.h = x, y, w, h
        self.fillColor = fillColor

    def depend(self):
        return self.x.depend()|self.y.depend()|self.w.depend()|self.h.depend()|self.fillColor.depend()

    def get_coords(self, canvas):
        x0 = self.x()
        y0 = self.y()
        x1 = x0 + self.w()
        y1 = y0 + self.h()
        x0 = x0*canvas.winfo_width()/100
        y0 = y0*canvas.winfo_height()/100
        x1 = x1*canvas.winfo_width()/100
        y1 = y1*canvas.winfo_height()/100
        return x0, y0, x1, y1

    def draw(self, canvas):
        self.shapeid = canvas.create_rectangle(*self.get_coords(canvas), fill=self.fillColor())

    def update(self, canvas):
        canvas.coords(self.shapeid, *self.get_coords(canvas))
        canvas.itemconfig(self.shapeid, fill=self.fillColor())

    def draw_helper(self, token, canvas):
        coords = None
        if token in self.x.depend():
            coords = self.get_x_helper_coords(canvas)
        if token in self.y.depend():
            coords = self.get_y_helper_coords(canvas)
        if token in self.w.depend():
            coords = self.get_w_helper_coords(canvas)
        if token in self.h.depend():
            coords = self.get_h_helper_coords(canvas)
        if coords:
            canvas.create_line(*coords, fill="red", tags="helpers")

    def get_x_helper_coords(self, canvas):
        x0, y0, x1, y1 = self.get_coords(canvas)
        return 0, y0, x0, y0

    def get_y_helper_coords(self, canvas):
        x0, y0, x1, y1 = self.get_coords(canvas)
        return x0, 0, x0, y0

    def get_h_helper_coords(self, canvas):
        x0, y0, x1, y1 = self.get_coords(canvas)
        middle_x = (x0+x1)/2
        return middle_x, y0, middle_x, y1

    def get_w_helper_coords(self, canvas):
        x0, y0, x1, y1 = self.get_coords(canvas)
        middle_y = (y0+y1)/2
        return x0, middle_y, x1, middle_y

class Ellipse(Rectangle):
    def draw(self, canvas):
        self.shapeid = canvas.create_oval(*self.get_coords(canvas), fill=self.fillColor())

    def get_x_helper_coords(self, canvas):
        x0, y0, x1, y1 = self.get_coords(canvas)
        middle_y = (y0+y1)/2
        return 0, middle_y, x0, middle_y

    def get_y_helper_coords(self, canvas):
        x0, y0, x1, y1 = self.get_coords(canvas)
        middle_x = (x0+x1)/2
        return middle_x, 0, middle_x, y0

