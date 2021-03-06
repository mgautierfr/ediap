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

from . import shapes as _shapes
from language import nodes as _languagenodes
from . import nodes as _nodes
from .arguments import *
Value = _languagenodes.Value


class draw_line:
    help = "Draw a line"
    arguments_order = ['x1', 'y1', 'x2', 'y2', 'w', 'color']
    arguments = {'x1': IntArgument("x position of the first point"),
                 'y1': IntArgument("y position of the first point"),
                 'x2': IntArgument("x position of the second point"),
                 'y2': IntArgument("y position of the second point"),
                 'w' : IntArgument("width of the line"),
                 'color':ColorArgument("The color of the line")
                }

    def __init__(self, state, x1, y1, x2, y2, w=None, color=None):
        self.state = state
        self.x1, self.y1, self.x2, self.y2 = (t.get_node(state.namespace) for t in (x1, y1, x2, y2))
        self.w = w.get_node(state.namespace) if w else Value(1)
        self.color = color.get_node(state.namespace) if color else _nodes.Color(Value(0), Value(0), Value(0))

    def act(self):
        self.state.context.shapes.append(_shapes.Line(self.state.lineno, self.color, self.w, (self.x1, self.y1, self.x2, self.y2)))

    def get_help(self):
        return [('text' , "Draw a "),
                ('shape', 'line'),
                ('text' , " from %sx%s"%(self.x1(),self.y1())),
                ('text' , " to %sx%s"%(self.x2(), self.y2()))
               ]

class draw_rectangle:
    help = "Draw a rectangle"
    arguments_order = ['x', 'y', 'w', 'h']
    arguments = {'x': IntArgument("x position of the top left corner"),
                 'y': IntArgument("y position of the top left corner"),
                 'w': IntArgument("width of the rectangle"),
                 'h': IntArgument("height of the rectangle")
                }
    
    def __init__(self, state, x, y, w, h):
        self.state = state
        self.x, self.y, self.w, self.h = (t.get_node(state.namespace) for t in (x, y, w, h))

    def act(self):
        self.state.context.shapes.append(_shapes.Rectangle(self.state.lineno, self.x, self.y, self.w, self.h, self.state.context.fillColor))

    def get_help(self):
        return [('text' , "Draw a "),
                ('shape', 'rectangle'),
                ('text' , " at %sx%s"%(self.x(),self.y())),
                ('text' , " with size %sx%s"%(self.w(), self.h()))
               ]

class draw_ellipse(draw_rectangle):
    help = "Draw a ellipse"
    arguments = {'x': IntArgument("x position of the top left corner"),
                 'y': IntArgument("y position of the top left corner"),
                 'w': IntArgument("width of the ellipse"),
                 'h': IntArgument("height of the ellipse")
                }

    def act(self):
        self.state.context.shapes.append(_shapes.Ellipse(self.state.lineno, self.x, self.y, self.w, self.h, self.state.context.fillColor))

    def get_help(self):
        return [('text' , "Draw a "),
                ('shape', 'ellipse'),
                ('text' , " at %sx%s"%(self.x(),self.y())),
                ('text' , " with size %sx%s"%(self.w(), self.h()))
               ]

class _polygon:
    @staticmethod
    def update_coord(point, state):
        x, y = point
        x = x.get_node(state.namespace)
        y = y.get_node(state.namespace)
        return x, y

class draw_quad(_polygon):
    help = "Draw a quad"
    arguments_order = ['x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3']
    arguments = {'x0': IntArgument("x position of the top first corner"),
                 'y0': IntArgument("y position of the top first corner"),
                 'x1': IntArgument("x position of the top second corner"),
                 'y1': IntArgument("y position of the top second corner"),
                 'x2': IntArgument("x position of the top third corner"),
                 'y2': IntArgument("y position of the top third corner"),
                 'x3': IntArgument("x position of the top fourth corner"),
                 'y3': IntArgument("y position of the top fourth corner"),
                }

    def __init__(self, state, x0,y0, x1,y1, x2,y2, x3,y3):
        self.state = state
        self.p0 = self.update_coord((x0, y0), state)
        self.p1 = self.update_coord((x1, y1), state)
        self.p2 = self.update_coord((x2, y2), state)
        self.p3 = self.update_coord((x3, y3), state)

    def act(self):
        self.state.context.shapes.append(_shapes.Polygon(self.state.lineno, self.state.context.fillColor, (self.p0+self.p1+self.p2+self.p3)))

    def get_help(self):
        namespace = self.state.namespace
        return [('text', "Draw a "),
                ('shape', 'quad'),
                ('text', " with points "),
                ('text', "%sx%s "%(self.p0[0](), self.p0[1]())),
                ('text', "%sx%s "%(self.p1[0](), self.p1[1]())),
                ('text', "%sx%s "%(self.p2[0](), self.p2[1]())),
                ('text', "%sx%s "%(self.p3[0](), self.p3[1]()))
               ]

class draw_triangle(_polygon):
    help = "Draw a quad"
    arguments_order = ['x0', 'y0', 'x1', 'y1', 'x2', 'y2']
    arguments = {'x0': IntArgument("x position of the top first corner"),
                 'y0': IntArgument("y position of the top first corner"),
                 'x1': IntArgument("x position of the top second corner"),
                 'y1': IntArgument("y position of the top second corner"),
                 'x2': IntArgument("x position of the top third corner"),
                 'y2': IntArgument("y position of the top third corner")
                }

    def __init__(self, state, x0,y0, x1,y1, x2,y2):
        self.state = state
        self.p0 = self.update_coord((x0, y0), state)
        self.p1 = self.update_coord((x1, y1), state)
        self.p2 = self.update_coord((x2, y2), state)

    def act(self):
        self.state.context.shapes.append(_shapes.Polygon(self.state.lineno, self.state.context.fillColor, (self.p0+self.p1+self.p2)))

    def get_help(self):
        namespace = self.state.namespace
        return [('text', "Draw a "),
                ('shape', 'triangle'),
                ('text', " with points "),
                ('text', "%sx%s "%(self.p0[0](), self.p0[1]())),
                ('text', "%sx%s "%(self.p1[0](), self.p1[1]())),
                ('text', "%sx%s "%(self.p2[0](), self.p2[1]()))
               ]


class change_color:
    help = "Change the color of the fill parameter"
    arguments_order = ['r', 'v', 'b']
    arguments = {'r': IntArgument("red", (0, 255), 10),
                 'v': IntArgument("green", (0, 255), 10),
                 'b': IntArgument("blue", (0, 255), 10)
                }

    def __init__(self, state, r, v, b):
        self.state = state
        self.r, self.v, self.b = (token.get_node(state.namespace) for token in (r, v, b))

    def act(self):
        self.state.context.fillColor = _nodes.Color(self.r, self.v, self.b)

    def get_help(self):
        r, v, b = (min(max(c(), 0), 255) for c in (self.r,self.v,self.b))
        return [('text', "Change current color to "),
                ('color', "#%02x%02x%02x"%(r, v, b))
               ]
