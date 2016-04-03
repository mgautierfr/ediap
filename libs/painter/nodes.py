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


__all__ = ['Color']

import language.nodes as _nodes
from .arguments import *

class Color(_nodes.Node):
    help = "Create a color object"
    arguments_order = ['red', 'green', 'blue']
    arguments = {'red'  : IntArgument("red", (0, 255), 10),
                 'green': IntArgument("green", (0, 255), 10),
                 'blue' : IntArgument("blue", (0, 255), 10)
                }

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


