import shapes as _shapes
import nodes as _nodes

class _ColorNode(_nodes.Node):
    def __init__(self, r, v, b):
        _nodes.Node.__init__(self)
        self.r, self.v, self.b = r, v, b
        r.add_ref(self)
        v.add_ref(self)
        b.add_ref(self)

    def depend(self):
        return self.r.depend()|self.v.depend()|self.b.depend()

    def get_value(self):
        r = min(max(self.r(), 0), 255)
        v = min(max(self.v(), 0), 255)
        b = min(max(self.b(), 0), 255)
        self.opositColor = "#%02x%02x%02x"%(255-r,255-v,255-b)
        return "#%02x%02x%02x"%(r,v,b)

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

class _FunctionDefinition:
    def __init__(self, name, args):
        self.name = name,
        self.args = args

class _Actor:
    def __init__(self, level):
        self.level = level

    @property
    def klass(self):
        return self.__class__.__name__

class rectangle(_Actor):
    help = "Draw a rectangle"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the rectangle"),
                 _IntArgument("height of the rectangle")
                ]
    
    def __init__(self, level, x, y, w, h):
        _Actor.__init__(self, level)
        self.x, self.y, self.w, self.h = x, y, w, h

    def get_bounding_rect(self, state):
        x0 = self.x.get_node(state.namespace)
        y0 = self.y.get_node(state.namespace)
        x0 = _nodes.Operator('-', x0, state.hiddenState['view_left'])
        y0 = _nodes.Operator('-', y0, state.hiddenState['view_top'])
        x1 = _nodes.Operator('+', x0, self.w.get_node(state.namespace))
        y1 = _nodes.Operator('+', y0, self.h.get_node(state.namespace))

        x0 = _nodes.Operator('/', x0, state.hiddenState['view_width'])
        x1 = _nodes.Operator('/', x1, state.hiddenState['view_width'])
        y0 = _nodes.Operator('/', y0, state.hiddenState['view_height'])
        y1 = _nodes.Operator('/', y1, state.hiddenState['view_height'])
        return x0, y0, x1, y1

    def __call__(self, state):
        x0, y0, x1, y1 = self.get_bounding_rect(state)
        x, y, w, h = (t.get_node(state.namespace) for t in (self.x, self.y, self.w, self.h))
        state.shapes.append(_shapes.Rectangle(state.lineno, x0, y0, x1, y1, x, y, w, h, state.hiddenState['fillColor']))

class ellipse(rectangle):
    help = "Draw a ellipse"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the ellipse"),
                 _IntArgument("height of the ellipse")
                ]

    def __call__(self, state):
        x0, y0, x1, y1 = self.get_bounding_rect(state)
        x, y, w, h = (t.get_node(state.namespace) for t in (self.x, self.y, self.w, self.h))
        state.shapes.append(_shapes.Ellipse(state.lineno, x0, y0, x1, y1, x, y, w, h, state.hiddenState['fillColor']))

class _polygon(_Actor):
    @staticmethod
    def update_coord(point, state):
        x, y = point
        x = x.get_node(state.namespace)
        y = y.get_node(state.namespace)
        x = _nodes.Operator('-', x, state.hiddenState['view_left'])
        y = _nodes.Operator('-', y, state.hiddenState['view_top'])
        x = _nodes.Operator('/', x, state.hiddenState['view_width'])
        y = _nodes.Operator('/', y, state.hiddenState['view_height'])
        return x, y

class quad(_polygon):
    help = "Draw a quad"
    arguments = [_IntArgument("x position of the top first corner"),
                 _IntArgument("y position of the top first corner"),
                 _IntArgument("x position of the top second corner"),
                 _IntArgument("y position of the top second corner"),
                 _IntArgument("x position of the top third corner"),
                 _IntArgument("y position of the top third corner"),
                 _IntArgument("x position of the top fourth corner"),
                 _IntArgument("y position of the top fourth corner"),
                ]

    def __init__(self, level, x0,y0, x1,y1, x2,y2, x3,y3):
        _polygon.__init__(self, level)
        self.p0 = x0, y0
        self.p1 = x1, y1
        self.p2 = x2, y2
        self.p3 = x3, y3

    def __call__(self, state):
        p0 = self.update_coord(self.p0, state)
        p1 = self.update_coord(self.p1, state)
        p2 = self.update_coord(self.p2, state)
        p3 = self.update_coord(self.p3, state)
        state.shapes.append(_shapes.Polygon(state.lineno, state.hiddenState['fillColor'], (p0+p1+p2+p3)))

class triangle(_polygon):
    help = "Draw a quad"
    arguments = [_IntArgument("x position of the top first corner"),
                 _IntArgument("y position of the top first corner"),
                 _IntArgument("x position of the top second corner"),
                 _IntArgument("y position of the top second corner"),
                 _IntArgument("x position of the top third corner"),
                 _IntArgument("y position of the top third corner")
                ]

    def __init__(self, level, x0,y0, x1,y1, x2,y2):
        _polygon.__init__(self, level)
        self.p0 = x0, y0
        self.p1 = x1, y1
        self.p2 = x2, y2

    def __call__(self, state):
        p0 = self.update_coord(self.p0, state)
        p1 = self.update_coord(self.p1, state)
        p2 = self.update_coord(self.p2, state)
        state.shapes.append(_shapes.Polygon(state.lineno, state.hiddenState['fillColor'], (p0+p1+p2)))

class fill(_Actor):
    help = "Change the color of the fill parameter"
    arguments = [_IntArgument("red", (0, 255), 10),
                 _IntArgument("green", (0, 255), 10),
                 _IntArgument("blue", (0, 255), 10)
                ]

    def __init__(self, level, r, v, b):
        _Actor.__init__(self, level)
        self.r, self.v, self.b = r, v, b

    def __call__(self, state):
        r, v, b = (token.get_node(state.namespace) for token in (self.r, self.v, self.b))
        state.hiddenState['fillColor'] = _ColorNode(r, v, b)


class view(_Actor):
    help = "Change the view of the canvas"
    arguments = [_IntArgument("left of the view"),
                 _IntArgument("top of the view"),
                 _IntArgument("right of the view"),
                 _IntArgument("bottom of the view")
                ]

    def __init__(self, level, left, top, width, height):
        _Actor.__init__(self, level)
        self.left, self.top, self.width, self.height = left, top, width, height

    def __call__(self, state):
        state.hiddenState['view_left'] = self.left.get_node(state.namespace)
        state.hiddenState['view_top'] = self.top.get_node(state.namespace)
        state.hiddenState['view_width'] = self.width.get_node(state.namespace)
        state.hiddenState['view_height'] = self.height.get_node(state.namespace)


class _setter(_Actor):
    def __init__(self, level, name, value):
        _Actor.__init__(self, level)
        self.name = name
        self.value = value

    def __call__(self, state):
        state.namespace[self.name.v] = self.value.get_node(state.namespace)

class _if(_Actor):
    def __init__(self, level, test):
        _Actor.__init__(self, level)
        self.test = test

    def __call__(self, state):
        test_node = self.test.get_node(state.namespace)
        return test_node()

class _while(_if):
    pass

class _functionDef(_Actor):
    def __init__(self, level, name, args):
        _Actor.__init__(self, level)
        self.name = name
        self.args = args

    def __call__(self, state):
        state.functions[self.name.v] = _FunctionDefinition(self.name.v, [arg.v for arg in self.args])

class _functionCall(_Actor):
    def __init__(self, level, name, args):
        _Actor.__init__(self, level)
        self.name = name
        self.args = args

    def __call__(self, state):
        functionDef = state.functions[self.name.v]
        for argName, arg in zip(functionDef.args, self.args):
            state.namespace.dict[argName] = arg.get_node(state.namespace)

