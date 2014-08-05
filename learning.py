#!/usr/bin/env python3


import tkinter, tkinter.font
from pprint import pprint
import interpreter
import gui
from program import Program, Line

default_source = """#Ceci est une fonction qui dessine une maison
define house(var x, var y, var w, var h)
  use var ratio
  ratio = 0.3
  draw_triangle(x,y+h*ratio, x+w,y+h*ratio, x+w/2,y)
  draw_rectangle(x, y+h*ratio, w, h*(1-ratio))

define test(var a, var b)
  draw_ellipse(x*a, b, 10, 10)
  x = 5
  draw_ellipse(x*a, b+10, 10, 10)

use var x
use var y

# On attribue 1 la variable x
x = 1
change_color(0, 0, 255)
draw_ellipse(5, 5, 10, 10)
draw_rectangle(20, 5+x*2, 15, 5)

change_color(255, 255, 0)
do test(5, 20)
draw_rectangle(20, 5+x*2, 15, 5)

change_color(255, 0, 255)
do house(15, 50, 15, 35)

change_color(0, 255, 0)
draw_quad(50,10, 50,20, 60,20, 60,10)

change_color(0, 255, 255)
x = 0
while x < 3
  draw_rectangle(50+10*x, 25+2*x, 10, 10)
  x = x + 1

x=0
while x < 10
  y = 0
  while y < 5
    change_color(25*x, 50*y, 0)
    draw_rectangle(50+5*x, 50+5*y, 3, 3)
    y = y + 1
  x = x + 1"""


def main():
    root = tkinter.Tk()
    from libs import painter

    program = Program(painter)
    program.set_source(default_source.split('\n'))

    #Create the gui widgets
    stepChanger = gui.StepChanger(root, program)
    text = gui.TextInput(root, program)
    activeStateShower = gui.ActiveStateShower(root, program)
    stepOutput = gui.StepOutput(root, text, program)
    textHelp = gui.TextHelp(root, text, program)
    help = gui.HelpShower(root, program)

    #Place them in the rigth order
    root.grid_propagate(True)
    stepChanger.grid(row=0, column=0, columnspan=4, sticky="nesw")
    text.grid(row=1, column=0, sticky="nesw")
    textHelp.grid(row=1, column=1, sticky="nesw")
    stepOutput.grid(row=1, column=2, sticky="nesw")
    activeStateShower.grid(row=1, column=3, sticky="nesw")
    help.grid(row=2, column=0, columnspan=4, sticky="nesw")
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=0)
    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=0)

    # create the interpretor and go, go, go
    interpretor = interpreter.Interpreter(program)
    root.after(500, lambda : program.event("source_changed")())
    root.mainloop()


if __name__ == '__main__':
    main()

