import shapes as _shapes

def _update_coord(x, y, context, state):
    cwidth, cheight = context.canvas.winfo_width(), context.canvas.winfo_height()
    return x/state.hiddenState['x_canvas_range'][1]*cwidth, y/state.hiddenState['y_canvas_range'][1]*cheight

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

class rectangle:
    help = "Draw a rectangle"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the rectangle"),
                 _IntArgument("height of the rectangle")
                ]
    
    def __init__(self, context, x, y, w, h):
        self.context = context
        self.x, self.y, self.w, self.h = x, y, w, h

    def get_bounding_rect(self, state):
        x0, y0 = self.x.execute(state.namespace), self.y.execute(state.namespace)
        x0 -= state.hiddenState['x_canvas_range'][0]
        y0 -= state.hiddenState['y_canvas_range'][0]
        x1 = x0+self.w.execute(state.namespace)
        y1 = y0+self.h.execute(state.namespace)
        x0, y0 = _update_coord(x0, y0, self.context, state)
        x1, y1 = _update_coord(x1, y1, self.context, state)
        return x0, y0, x1, y1

    def act(self, state):
        x0, y0, x1, y1 = self.get_bounding_rect(state)
        state.shapes.append(_shapes.Rectangle(x0, y0, x1, y1, state.hiddenState['fillColor']))

class ellipse(rectangle):
    help = "Draw a ellipse"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the ellipse"),
                 _IntArgument("height of the ellipse")
                ]

    def act(self, state):
        x0, y0, x1, y1 = self.get_bounding_rect(state)
        state.shapes.append(_shapes.Ellipse(x0, y0, x1, y1, state.hiddenState['fillColor']))

class fill:
    help = "Change the color of the fill parameter"
    arguments = [_IntArgument("red", (0, 255), 10),
                 _IntArgument("green", (0, 255), 10),
                 _IntArgument("blue", (0, 255), 10)
                ]
    
    def __init__(self, context, r, v, b):
        self.context = context
        self.r, self.v, self.b = r, v, b

    def act(self, state):
        state.hiddenState['fillColor'] = "#%02x%02x%02x"%(self.r.execute(state.namespace),self.v.execute(state.namespace),self.b.execute(state.namespace))


class view:
    help = "Change the view of the canvas"
    arguments = [_IntArgument("left of the view"),
                 _IntArgument("top of the view"),
                 _IntArgument("right of the view"),
                 _IntArgument("bottom of the view")
                ]

    def __init__(self, context, left, top, width, height):
        self.context = context
        self.left, self.top, self.width, self.height = left, top, width, height

    def act(self, state):
        state.hiddenState['x_canvas_range'][0] = self.left.execute(state.namespace)
        state.hiddenState['y_canvas_range'][0] = self.top.execute(state.namespace)
        state.hiddenState['x_canvas_range'][1] = self.width.execute(state.namespace)
        state.hiddenState['y_canvas_range'][1] = self.height.execute(state.namespace)


class _setter:
    def __init__(self, context, name, value):
        self.context = context
        self.name = name
        self.value = value

    def act(self, state):
        state.namespace[self.name] = self.value.execute(state.namespace)
