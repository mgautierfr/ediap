from . import shapes as _shapes
from language import nodes as _nodes
from language.actors import Actor

__all__ = ['draw_rectangle', 'draw_ellipse', 'draw_quad', 'draw_triangle' , 'change_color']

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

class draw_rectangle(Actor):
    help = "Draw a rectangle"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the rectangle"),
                 _IntArgument("height of the rectangle")
                ]
    
    def __init__(self, level, x, y, w, h):
        Actor.__init__(self, level)
        self.x, self.y, self.w, self.h = x, y, w, h

    def __call__(self, state):
        x, y, w, h = (t.get_node(state.namespace) for t in (self.x, self.y, self.w, self.h))
        state.shapes.append(_shapes.Rectangle(state.lineno, x, y, w, h, state.hiddenState['fillColor']))

    def get_help(self, state):
        namespace = state.namespace
        return [('text' , "Draw a "),
                ('shape', 'rectangle'),
                ('text' , " at %sx%s"%(self.x.get_node(namespace)(),self.y.get_node(namespace)())),
                ('text' , " with size %sx%s"%(self.w.get_node(namespace)(), self.h.get_node(namespace)()))
               ]

class draw_ellipse(draw_rectangle):
    help = "Draw a ellipse"
    arguments = [_IntArgument("x position of the top left corner"),
                 _IntArgument("y position of the top left corner"),
                 _IntArgument("width of the ellipse"),
                 _IntArgument("height of the ellipse")
                ]

    def __call__(self, state):
        x, y, w, h = (t.get_node(state.namespace) for t in (self.x, self.y, self.w, self.h))
        state.shapes.append(_shapes.Ellipse(state.lineno, x, y, w, h, state.hiddenState['fillColor']))

    def get_help(self, state):
        namespace = state.namespace
        return [('text' , "Draw a "),
                ('shape', 'ellipse'),
                ('text' , " at %sx%s"%(self.x.get_node(namespace)(),self.y.get_node(namespace)())),
                ('text' , " with size %sx%s"%(self.w.get_node(namespace)(), self.h.get_node(namespace)()))
               ]

class _polygon(Actor):
    @staticmethod
    def update_coord(point, state):
        x, y = point
        x = x.get_node(state.namespace)
        y = y.get_node(state.namespace)
        return x, y

class draw_quad(_polygon):
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

    def get_help(self, state):
        namespace = state.namespace
        return [('text', "Draw a "),
                ('shape', 'quad'),
                ('text', " with points "),
                ('text', "%sx%s "%(self.p0[0].get_node(namespace)(), self.p0[1].get_node(namespace)())),
                ('text', "%sx%s "%(self.p1[0].get_node(namespace)(), self.p1[1].get_node(namespace)())),
                ('text', "%sx%s "%(self.p2[0].get_node(namespace)(), self.p2[1].get_node(namespace)())),
                ('text', "%sx%s "%(self.p3[0].get_node(namespace)(), self.p3[1].get_node(namespace)()))
               ]

class draw_triangle(_polygon):
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

    def get_help(self, state):
        namespace = state.namespace
        return [ ('text', "Draw a "),
                 ('shape', 'triangle'),
                 ('text', " with points "),
                 ('text', "%sx%s "%(self.p0[0].get_node(namespace)(), self.p0[1].get_node(namespace)())),
                 ('text', "%sx%s "%(self.p1[0].get_node(namespace)(), self.p1[1].get_node(namespace)())),
                 ('text', "%sx%s "%(self.p2[0].get_node(namespace)(), self.p2[1].get_node(namespace)())),
               ]

class change_color(Actor):
    help = "Change the color of the fill parameter"
    arguments = [_IntArgument("red", (0, 255), 10),
                 _IntArgument("green", (0, 255), 10),
                 _IntArgument("blue", (0, 255), 10)
                ]

    def __init__(self, level, r, v, b):
        Actor.__init__(self, level)
        self.r, self.v, self.b = r, v, b

    def __call__(self, state):
        r, v, b = (token.get_node(state.namespace) for token in (self.r, self.v, self.b))
        state.hiddenState['fillColor'] = _ColorNode(r, v, b)

    def get_help(self, state):
        r, v, b = (token.get_node(state.namespace) for token in (self.r, self.v, self.b))
        r, v, b = (min(max(c(), 0), 255) for c in (r,v,b))
        return [('text', "Change current color to "),
                ('color', "#%02x%02x%02x"%(r, v, b))
               ]
