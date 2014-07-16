import actors as _actors

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
        self.arguments = [_IntArgument("x position of the top left corner"),
                          _IntArgument("y position of the top left corner"),
                          _IntArgument("width of the ellipse"),
                          _IntArgument("height of the ellipse")
                         ]
        

    def __call__(self, x, y, w, h):
        return _actors.Ellipse(self.context, x, y, w, h)


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
        return _actors.Rectangle(self.context, x, y, w, h)

class fill:
    help = "Change the color of the fill parameter"
    
    def __init__(self, context):
        self.context = context
        self.arguments = [_IntArgument("red", (0, 255), 10),
                          _IntArgument("green", (0, 255), 10),
                          _IntArgument("blue", (0, 255), 10)
                         ]
        

    def __call__(self, r, v, b):
        return _actors.Fill(self.context, r, v, b)


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
        return _actors.View(self.context, left, top, width, height)
