#!/usr/bin/env python3


import tkinter, tkinter.font
import functions
from pprint import pprint
import interpreter
import gui
from textTagger import TextTagger
        

interpretor = None

def main():
    global interpretor
    root = tkinter.Tk()
    
    helpv = tkinter.StringVar()
    
    text = gui.TextInput(root, helpv)
    
    canvas = gui.CanvasOutput(root)

    stepOutput = gui.StepOutput(root, text)
    
    textTagger = TextTagger(text, canvas)

    interpretor = interpreter.Interpreter(text, textTagger)
    canvas.interpretor = interpretor
    interpretor.add_follower(canvas)
    stepOutput.interpretor = interpretor
    interpretor.add_follower(stepOutput)


    text.insert("1.0", """x = 11
view(0, 0, 1000, 1000)
fill(0, 0, 255)
ellipse(10, 10, 100, 100)
rectangle(200, 200+x*9, 150, 50)
fill(255, 255, 0)
x = 0
while x < 3
  rectangle(500+110*x, 100+10*x, 100, 100)
  x = x + 1
x=0
while x < 1
  y = 0
  while y < 1
    fill(25*x, 25*y, 0)
    rectangle(500+50*x, 500+50*y, 30, 30)
    y = y + 1
  x = x + 1""")

    canvas.place()
    label = tkinter.Label(root, textvariable=helpv)
    label.pack(side="bottom", anchor="s")

    stepOutput.place()
    text.place()
    

    text.edit_modified(True)
    root.after_idle(interpretor.on_modified)
    root.mainloop()


if __name__ == '__main__':
    main()

