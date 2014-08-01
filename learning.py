#!/usr/bin/env python3


import tkinter, tkinter.font
import functions
from pprint import pprint
import interpreter
import gui
from program import Program, Line

default_source = """function house(x, y, w, h)
  ratio = 0.3
  triangle(x,y+h*ratio, x+w,y+h*ratio, x+w/2,y)
  rectangle(x, y+h*ratio, w, h*(1-ratio))

function test(a, b)
  ellipse(x*a, b, 10, 10)
  x = 5
  ellipse(x*a, b+10, 10, 10)

x = 1
fill(0, 0, 255)
ellipse(5, 5, 10, 10)
rectangle(20, 5+x*2, 15, 5)

fill(255, 255, 0)
test(5, 20)
rectangle(20, 5+x*2, 15, 5)

fill(255, 0, 255)
house(15, 50, 15, 35)

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
  while y < 10
    fill(25*x, 25*y, 0)
    rectangle(50+5*x, 50+5*y, 3, 3)
    y = y + 1
  x = x + 1"""


def main():
    root = tkinter.Tk()

    program = Program()
    program.set_source(default_source.split('\n'))

    #Create the gui widgets
    stepChanger = gui.StepChanger(root, program)
    text = gui.TextInput(root, program)
    canvas = gui.ActiveStateShower(root, program)
    stepOutput = gui.StepOutput(root, text, program)
    help = gui.HelpShower(root, program)

    #Place them in the rigth order
    stepChanger.place()
    help.place()
    canvas.place()
    stepOutput.place()
    text.place()

    # create the interpretor and go, go, go
    interpretor = interpreter.Interpreter(program)
    root.after(500, lambda : program.event("source_changed")())
    root.mainloop()


if __name__ == '__main__':
    main()

