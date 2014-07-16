
def _update_coord(x, y, context):
    cwidth, cheight = context['canvas'].winfo_width(), context['canvas'].winfo_height()
    return x/context['x_canvas_range'][1]*cwidth, y/context['y_canvas_range'][1]*cheight

class Actor:
    """Represent a actor"""
    def __init__(self, context):
        self.helper = None
        self.context = context

    def show_helper(self, index):
        pass

    def hide_helper(self):
        if self.helper is not None:
            self.context['canvas'].delete(self.helper[1])
        self.helper = None

    def update(self):
        pass

class Rectangle(Actor):
    def __init__(self, context, x, y, w, h):
        Actor.__init__(self, context)
        self.x, self.y, self.w, self.h = x, y, w, h

    def get_bounding_rect(self):
        x0, y0 = self.x.execute(), self.y.execute()
        x0 -= self.context['x_canvas_range'][0]
        y0 -= self.context['y_canvas_range'][0]
        x1 = x0+self.w.execute()
        y1 = y0+self.h.execute()
        x0, y0 = _update_coord(x0, y0, self.context)
        x1, y1 = _update_coord(x1, y1, self.context)
        return x0, y0, x1, y1

    def update(self):
        self.context['canvas'].coords(self.shape, *self.get_bounding_rect())
        if self.helper:
            index, helper = self.helper
            if index == 0:
                coords = self.get_x_helper_coords()
            if index == 1:
                coords = self.get_y_helper_coords()
            if index == 2:
                coords = self.get_w_helper_coords()
            if index == 3:
                coords = self.get_h_helper_coords()
            self.context['canvas'].coords(helper, *coords)

    def act(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        self.shape = self.context['canvas'].create_rectangle(x0, y0, x1, y1, fill=self.context['fillColor'])            

    def show_helper(self, index):
        if index == 0:
            coords = self.get_x_helper_coords()
        if index == 1:
            coords = self.get_y_helper_coords()
        if index == 2:
            coords = self.get_w_helper_coords()
        if index == 3:
            coords = self.get_h_helper_coords()
        self.helper = (index, self.context['canvas'].create_line(*coords, fill="red"))

    def get_x_helper_coords(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        return 0, y0, x1, y0

    def get_y_helper_coords(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        return x0, 0, x0, y1

    def get_h_helper_coords(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        middle_x = (x0+x1)/2
        return middle_x, y0, middle_x, y1

    def get_w_helper_coords(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        middle_y = (y0+y1)/2
        return x0, middle_y, x1, middle_y

class Ellipse(Rectangle):
    def __init__(self, *args):
        Rectangle.__init__(self, *args)

    def act(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        self.shape = self.context['canvas'].create_oval(x0, y0, x1, y1, fill=self.context['fillColor'])

    def get_x_helper_coords(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        middle_y = (y0+y1)/2
        return 0, middle_y, x0, middle_y

    def get_y_helper_coords(self):
        x0, y0, x1, y1 = self.get_bounding_rect()
        middle_x = (x0+x1)/2
        return middle_x, 0, middle_x, y0


class Fill(Actor):
    def __init__(self, context, r, v, b):
        Actor.__init__(self, context)
        self.r, self.v, self.b = r, v, b

    def act(self):
        self.context['fillColor'] = "#%02x%02x%02x"%(self.r.execute(),self.v.execute(),self.b.execute())


class View(Actor):
    def __init__(self, context, left, top, width, height):
        Actor.__init__(self, context)
        self.left, self.top, self.width, self.height = left, top, width, height

    def act(self):
        self.context['x_canvas_range'][0] = self.left.execute()
        self.context['y_canvas_range'][0] = self.top.execute()
        self.context['x_canvas_range'][1] = self.width.execute()
        self.context['y_canvas_range'][1] = self.height.execute()

