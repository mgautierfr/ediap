#!/usr/bin/env python3


import tkinter, tkinter.font
import functions
from pprint import pprint
import interpreter
import gui
from program import Program, Line

default_source = """x = 11
view(0, 0, 1000, 1000)
fill(0, 0, 255)
ellipse(10, 10, 100, 100)
rectangle(200, 200+x*9, 150, 50)
fill(255, 255, 0)
if x == 11
  fill(0, 0, 255)
x = 0
while x < 3
  rectangle(500+110*x, 100+10*x, 100, 100)
  x = x + 1
x=0
while x < 5
  y = 0
  while y < 5
    fill(25*x, 25*y, 0)
    rectangle(500+50*x, 500+50*y, 30, 30)
    y = y + 1
  x = x + 1"""


def main():
    root = tkinter.Tk()
    
    helpv = tkinter.StringVar()

    program = Program()

    program.set_source(default_source.split('\n'))

    stepChanger = gui.StepChanger(root, program)
    
    text = gui.TextInput(root, helpv, program)
    
    canvas = gui.ActiveStateShower(root, program)

    stepOutput = gui.StepOutput(root, text, program)

    interpretor = interpreter.Interpreter(program)

    stepChanger.place()

    canvas.place()
    label = tkinter.Label(root, textvariable=helpv)
    label.pack(side="bottom", anchor="s")

    stepOutput.place()
    text.place()

    root.after(500, lambda : program.event("source_changed")())
    root.mainloop()


if __name__ == '__main__':
    main()

