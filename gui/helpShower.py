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


import tkinter

class HelpShower(tkinter.Label):
    def __init__(self, parent, program):
        self.helpv = tkinter.StringVar()
        tkinter.Label.__init__(self, parent, textvariable=self.helpv)
        self.program = program
        program.connect("current_changed", self.on_current_changed)

    def on_current_changed(self):
        line, pos = self.program.current
        try:
            parsed = self.program.source[line-1].parsed
        except IndexError:
            return

        self.helpv.set("")
        if parsed is None or parsed.klass != "Builtin":
            return

        function_name = parsed.name.v
        try:
            functionDef = getattr(self.program.lib, function_name)
        except AttributeError:
            return

        if parsed.name.start <= pos <= parsed.name.end:
            self.helpv.set(functionDef.help)
            return

        for index, arg in enumerate(parsed.arguments):
            if arg.start <= pos <= arg.end:
                break
        else:
            index = None
        if index is not None:
            self.helpv.set(functionDef.arguments[index].help)
            return

