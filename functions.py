def _update_coord(x, y, context):
    cwidth, cheight = context['canvas'].winfo_width(), context['canvas'].winfo_height()
    return x/context['x_canvas_range'][1]*cwidth, y/context['y_canvas_range'][1]*cheight

class _IntArgument:
    def __init__(self, help, range=(None, None), step=1):
        self.help = help
        self.start, self.stop = range
        self.step = step

    def scale(self, value, neg):
        value += self.step*(1-2*neg)
        if self.start is not None:
            value = max(self.start, value)
        if self.stop is not None:
            value = min(self.stop, value)
        return value

class ellipse:
    help = "Draw a ellipse"
    
    def __init__(self, context):
        self.context = context
        self.arguments = [_IntArgument("x position at the center"),
                          _IntArgument("y position at the center"),
                          _IntArgument("width of the ellipse"),
                          _IntArgument("height of the ellipse")
                         ]
        

    def __call__(self, x, y, w, h):
        left = x - w/2 - self.context['x_canvas_range'][0]
        right = x + w/2 - self.context['x_canvas_range'][0]
        top = y - h/2 - self.context['y_canvas_range'][0]
        bottom = y + h/2 - self.context['y_canvas_range'][0]
        left, top = _update_coord(left, top, self.context)
        right, bottom = _update_coord(right, bottom, self.context)
        print("drowing at", left, top, right, bottom)
        item = self.context['canvas'].create_oval(left, top, right, bottom, fill=self.context['fillColor'])


class rectangle:
    help = "Draw a rectangle"
    
    def __init__(self, context):
        self.context = context
        self.arguments = [_IntArgument("x position of the top left corner"),
                          _IntArgument("y position of the top left corner"),
                          _IntArgument("width of the rectangle"),
                          _IntArgument("height of the rectangle")
                         ]
        

    def __call__(self, x, y, w, h):
        cwidth, cheight = self.context['canvas'].winfo_width(), self.context['canvas'].winfo_height()
        left = x
        right = x+w
        top = y
        bottom = y+h
        left, top = _update_coord(left, top, self.context)
        right, bottom = _update_coord(right, bottom, self.context)
        print("drowing at", left, top, right, bottom)
        item = self.context['canvas'].create_rectangle(left, top, right, bottom, fill=self.context['fillColor'])

class fill:
    help = "Change the color of the fill parameter"
    
    def __init__(self, context):
        self.context = context
        self.arguments = [_IntArgument("red", (0, 255), 10),
                          _IntArgument("green", (0, 255), 10),
                          _IntArgument("blue", (0, 255), 10)
                         ]
        

    def __call__(self, r, v, b):
        self.context['fillColor'] = "#%02x%02x%02x"%(r,v,b)


class view:
    help = "Change the view of the canvas"

    def __init__(self, context):
        self.context = context
        self.arguments = [_IntArgument("left of the view"),
                          _IntArgument("top of the view"),
                          _IntArgument("right of the view"),
                          _IntArgument("bottom of the view")
                         ]

    def __call__(self, left, top, width, height):
        self.context['x_canvas_range'][0] = left
        self.context['y_canvas_range'][0] = top
        self.context['x_canvas_range'][1] = width
        self.context['y_canvas_range'][1] = height
