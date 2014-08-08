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

class Instruction:
    is_nop = False

    @property
    def klass(self):
        return self.__class__.__name__

    def get_token_at_pos(self, pos):
        return None

class Comment(Instruction):
    is_nop = True
    def __init__(self, text):
        self.text = text

class Create(Instruction):
    def __init__(self, type_, name):
        self.type_ = type_
        self.name = name


class Set(Instruction):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_token_at_pos(self, pos):
        if self.value.start <= pos <= self.value.end:
            return self.value.get_token_at_pos(pos)
        return None

class If(Instruction):
    def __init__(self, test):
        self.test = test

    def get_token_at_pos(self, pos):
        if self.test.start <= pos <= self.test.end:
            return self.test.get_token_at_pos(pos)
        return None

class While(If):
    pass


class Create_subprogram(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Builtin(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def get_token_at_pos(self, pos):
        for arg in self.args:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

class Do_subprogram(Instruction):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def get_token_at_pos(self, pos):
        for arg in self.args:
            if arg.start <= pos <= arg.end:
                return arg.get_token_at_pos(pos)
        return None

