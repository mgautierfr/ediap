#!/usr/bin/env python3


import tkinter
import interpreter
import gui
from program import Program
import sys


def main():
    root = tkinter.Tk()
    from libs import painter

    program = Program(painter)
    try:
        fileToLoad = sys.argv[1]
    except IndexError:
        print("Ne file specified, opening first.lsa")
        fileToLoad = "first.lsa"
    program.load_file(fileToLoad)

    #Create the gui widgets
    menuBar = gui.MenuBar(root, program)
    stepChanger = gui.StepChanger(root, program)
    text = gui.TextInput(root, program)
    activeStateShower = gui.ActiveStateShower(root, program)
    stepOutput = gui.StepOutput(root, text, program)
    textHelp = gui.TextHelp(root, text, program)
    help = gui.HelpShower(root, program)

    #Place them in the rigth order
    root['menu'] = menuBar
    root.grid_propagate(True)
    stepChanger.grid(row=0, column=0, columnspan=50, sticky="nesw")
    vScrollbar = tkinter.Scrollbar(root, orient=tkinter.VERTICAL)
    vScrollbar.grid(row=1, column=0, sticky="nesw")
    text.grid(row=1, column=10, sticky="nesw")
    textHelp.grid(row=1, column=11, sticky="nesw")
    stepOutput.grid(row=1, column=12, sticky="nesw")
    activeStateShower.grid(row=1, column=13, sticky="nesw")
    help.grid(row=2, column=0, columnspan=50, sticky="nesw")
    root.columnconfigure(0, weight=0)
    root.columnconfigure(10, weight=2)
    root.columnconfigure(11, weight=1)
    root.columnconfigure(12, weight=2)
    root.columnconfigure(13, weight=0)
    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=0)

    def proxy_yview(*args, **kwords):
        text.yview(*args, **kwords)
        textHelp.on_activeStep_changed()
        stepOutput.on_steps_changed()

    def proxy_set(*args, **kwords):
        vScrollbar.set(*args, **kwords)
        textHelp.on_activeStep_changed()
        stepOutput.on_steps_changed()

    text['yscrollcommand'] = proxy_set
    vScrollbar['command'] = proxy_yview

    # create the interpretor and go, go, go
    interpretor = interpreter.Interpreter(program)
    root.after(500, lambda : program.event("source_changed")())
    root.mainloop()


if __name__ == '__main__':
    main()

