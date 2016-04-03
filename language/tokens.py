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

from . import nodes

operators = ['<', '<=', '>', '>=', '!=', '==', '-','+','*','/']

class Token:
    precedence = 1000
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    @property
    def klass(self):
        return self.__class__.__name__

    def get_token_at_pos(self, pos):
        return None

    def get_function_def(self, token):
        return None

class Value(Token):
    def __init__(self, value, start, end):
        Token.__init__(self, start, end)
        self.v  = value
        self._node = nodes.Value(value)

    def get_node(self, namespace):
        return self._node

    def get_token_at_pos(self, pos):
        return self

    def get_help_text(self, namespace):
        return self.v

class VarType(Token):
    def  __init__(self, type_, start, end):
        Token.__init__(self, start, end)
        self.v = type_

    def get_token_at_pos(self, pos):
        return self

class Int(Value):
    pass

class Float(Value):
    pass

class Paren(Value):
    def get_node(self, namespace):
        return self.v.get_node(namespace)

    def get_token_at_pos(self, pos):
        return self.v.get_token_at_pos(pos)

    def get_help_text(self, namespace):
        return "(%s)"%self.v.get_help_text(namespace)

class Identifier(Value):
    def get_node(self, namespace):
        return namespace[self.v].get()

    def get_help_text(self, namespace):
        return "%s(%s)"%(self.v, self.get_node(namespace)())

    def __repr__(self):
        return "<Indentifier %s>"%self.v

class BinaryOp(Token):
    def __init__(self, name, x, y, start, end):
        Token.__init__(self, start, end)
        self.name = name
        self.x, self.y = x, y

    def get_node(self, namespace):
        return nodes.Operator(self.name.v, self.x.get_node(namespace), self.y.get_node(namespace))

    @property
    def precedence(self):
        return operators.index(self.name.v)

    def merge(self):
        right = self.y
        if self.precedence >= right.precedence:
            self.y = right.x
            right.x = self
            return right
        else:
            return self

    def __str__(self):
        return "%s %s %s"%(self.name, self.start, self.end)

    def get_token_at_pos(self, pos):
        if self.x.start <= pos <= self.x.end:
            return self.x.get_token_at_pos(pos)
        if self.y.start <= pos <= self.y.end:
            return self.y.get_token_at_pos(pos)
        return None

    def get_help_text(self, namespace):
        return "%s %s %s"%(self.x.get_help_text(namespace), self.name.v, self.y.get_help_text(namespace))

class CustomToken(Token):
    def __init__(self, name, start, end, arguments, kwords):
        Token.__init__(self, start, end)
        self.name = name
        self.arguments = arguments
        self.kwords = kwords

    def get_node(self, namespace):
        return namespace.nodes[self.name.v](*(a.get_node(namespace) for a in self.arguments),
                                **{k:v.get_node(namespace) for k,v in self.kwords.items()})

    def __str__(self):
        return "CustomToken %s"%self.name

    def get_token_at_pos(self, pos):
        for arg in self.arguments:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        for arg in self.kwords.values():
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

    def get_help_text(self, namespace):
        return "Create a color"

    def get_function_def(self, token):
        if token in self.arguments:
            return self
        if token in self.kwords.values():
            return self
        for arg in self.arguments:
            fdef = arg.get_function_def(token)
            if fdef:
                return fdef
        for arg in self.kwords.values():
            fdef = arg.get_function_def(token)
            if fdef:
                return fdef
        return None

