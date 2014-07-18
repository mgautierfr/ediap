import shapes as _shapes

def _update_coord(x, y, context, state):
    cwidth, cheight = context.canvas.winfo_width(), context.canvas.winfo_height()
    return x/state.hiddenState['x_canvas_range'][2][1]*cwidth, y/state.hiddenState['y_canvas_range'][2][1]*cheight

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
        x0 -= state.hiddenState['x_canvas_range'][2][0]
        y0 -= state.hiddenState['y_canvas_range'][2][0]
        x1 = x0+self.w.execute(state.namespace)
        y1 = y0+self.h.execute(state.namespace)
        x0, y0 = _update_coord(x0, y0, self.context, state)
        x1, y1 = _update_coord(x1, y1, self.context, state)
        return x0, y0, x1, y1

    def act(self, state):
        x0, y0, x1, y1 = self.get_bounding_rect(state)
        depend = set([self.x, self.y, self.w, self.h])
        depend |= set.union(self.x.depend(state),self.y.depend(state),self.w.depend(state),self.h.depend(state), state.hiddenState['x_canvas_range'][1], state.hiddenState['y_canvas_range'][1], state.hiddenState['fillColor'][1])
        state.shapes.append((state, depend, _shapes.Rectangle(x0, y0, x1, y1, state.hiddenState['fillColor'][2])))

    def update(self, state, shape):
        shape.x0, shape.y0, shape.x1, shape.y1 = self.get_bounding_rect(state)
        shape.fillColor = state.hiddenState['fillColor'][2]

class ellipse(rectangle):
    help = "Draw a ellipse"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the ellipse"),
                 _IntArgument("height of the ellipse")
                ]

    def act(self, state):
        x0, y0, x1, y1 = self.get_bounding_rect(state)
        depend = set([self.x, self.y, self.w, self.h])
        depend |= set.union(self.x.depend(state),self.y.depend(state),self.w.depend(state),self.h.depend(state), state.hiddenState['x_canvas_range'][1], state.hiddenState['y_canvas_range'][1], state.hiddenState['fillColor'][1])
        state.shapes.append((state, depend, _shapes.Ellipse(x0, y0, x1, y1, state.hiddenState['fillColor'][2])))

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
        depend = set([self.r, self.v, self.b])
        depend |= set.union(self.r.depend(state), self.v.depend(state), self.b.depend(state))
        r = min(max(self.r.execute(state.namespace), 0), 255)
        v = min(max(self.v.execute(state.namespace), 0), 255)
        b = min(max(self.b.execute(state.namespace), 0), 255)
        value = "#%02x%02x%02x"%(r,v,b)
        state.hiddenState['fillColor'] = (state, depend, value)

    def update(self,state, v):
        return self.act(state)


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
        left = self.left.execute(state.namespace)
        top  = self.top.execute(state.namespace)
        width = self.width.execute(state.namespace)
        height = self.height.execute(state.namespace)
        depend = set([self.left, self.top, self.width, self.height])
        depend |= set.union(self.left.depend(state), self.top.depend(state), self.width.depend(state), self.height.depend(state))

        state.hiddenState['x_canvas_range'] = (state, depend, [left, width])
        state.hiddenState['y_canvas_range'] = (state, depend, [top, height])

    def update(self,state, v):
        return self.act(state)


class _setter:
    def __init__(self, context, name, value):
        self.context = context
        self.name = name
        self.value = value

    def act(self, state):
        depend = set([self.value])|self.value.depend(state)
        state.namespace[self.name] = (state, depend, self.value.execute(state.namespace))

    def update(self,state, v):
        return self.act(state)

class _if:
    def __init__(self, context, test):
        self.context = context
        self.test = test

    def act(self, state):
        return self.test.execute(state.namespace)

    def update(self,state, v):
        return self.act(state)

class _while(_if):
    pass
