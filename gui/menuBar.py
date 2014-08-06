

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

