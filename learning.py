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
  triangle(x,y+h*ratio, x+w,y+h*ratio, x+w/2,y)
  rectangle(x, y+h*ratio, w, h*(1-ratio))

define test(var a, var b)
  ellipse(x*a, b, 10, 10)
  x = 5
  ellipse(x*a, b+10, 10, 10)

use var x
use var y

# On attribue 1 à la variable x
x = 1
fill(0, 0, 255)
ellipse(5, 5, 10, 10)
rectangle(20, 5+x*2, 15, 5)

fill(255, 255, 0)
do test(5, 20)
rectangle(20, 5+x*2, 15, 5)

fill(255, 0, 255)
do house(15, 50, 15, 35)

fill(0, 255, 0)
quad(50,10, 50,20, 60,20, 60,10)

fill(0, 255, 255)
x = 0
while x < 3
  rectangle(50+10*x, 25+2*x, 10, 10)
  x = x + 1

x=0
while x < 10
  y = 0
  while y < 5
    fill(25*x, 50*y, 0)
    rectangle(50+5*x, 50+5*y, 3, 3)
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
    canvas = gui.ActiveStateShower(root, program)
    stepOutput = gui.StepOutput(root, text, program)
    textHelp = gui.TextHelp(root, text, program)
    help = gui.HelpShower(root, program)

    #Place them in the rigth order
    stepChanger.place()
    help.place()
    canvas.place()
    stepOutput.place()
    textHelp.place()
    text.place()

    # create the interpretor and go, go, go
    interpretor = interpreter.Interpreter(program)
    root.after(500, lambda : program.event("source_changed")())
    root.mainloop()


if __name__ == '__main__':
    main()

