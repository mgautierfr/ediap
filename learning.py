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
  fill(a*10, b, 100)
  ellipse(x*a, b, 10, 10)
  x = 5
  ellipse(x*a, b, 10, 10)
x = 11
view(0, 0, 100, 100)
fill(0, 0, 255)
ellipse(1, 1, 10, 10)
rectangle(20, 20+x*9, 15, 5)
fill(255, 255, 0)
if x == 11
  fill(0, 0, 255)
test(1, 20)
house(10, 10, 10, 20)
quad(10,10, 10,20, 20,20, 20,10)
x = 0
while x < 3
  rectangle(50+11*x, 10+1*x, 10, 10)
  x = x + 1
x=0
while x < 5
  y = 0
  test(5, 5)
  while y < 5
    fill(25*x, 25*y, 0)
    rectangle(50+5*x, 50+5*y, 3, 3)
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

