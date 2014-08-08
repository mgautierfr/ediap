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
import tkinter.filedialog

class MenuBar(tkinter.Menu):
    def __init__(self, parent, program):
        tkinter.Menu.__init__(self, parent)
        self.program = program
        fileMenu = tkinter.Menu(self)
        self.add('cascade', label="File", menu=fileMenu)
        fileMenu.add('command', label="Open", command=self.on_open)
        fileMenu.add('command', label="Save", command=self.on_save)

    def on_open(self, *args, **kwords):
        fileToOpen = tkinter.filedialog.asksaveasfilename(title="Open a file", confirmoverwrite=False)
        if not fileToOpen:
            return
        self.program.load_file(fileToOpen)
        self.program.event("source_changed")()
        

    def on_save(self, *args, **kwords):
        fileToSave = self.program.fileName
        if fileToSave is None:
            fileToSave = tkinter.filedialog.asksaveasfilename(title="Save a file")
        if not fileToSave:
            return
        with open(fileToSave, 'w') as f:
            f.write("\n".join((str(l) for l in self.program.source)))

