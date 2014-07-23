#!/usr/bin/env python3


import tkinter, tkinter.font
import functions
from pprint import pprint
import grammar, interpreter


def int_scale(value, neg):
    return value + (1-2*neg)

class LineTagger:
    def __init__(self, textWidget, lineno):
        self.textWidget = textWidget
        self.lineno = lineno
        self.directChild = False
        self.context = []

    def tag(self, node):
        sub_executor = getattr(self, "tag_%s"%node.klass, None)
        if sub_executor:
            return sub_executor(node)

    def tag_Assignement(self, node):
        tag_name = "%s_assign"%(node.name.v)
        start_index = "%d.%d"%(self.lineno, node.name.start)
        end_index = "%d.%d"%(self.lineno, node.name.end)
        self.textWidget.tag_add(tag_name, start_index, end_index)
        self.tag(node.value)

    def tag_Call(self, node):
        function_name = node.name.v
        self.tag_functionIdentifier(node.name)
        for index, argument in enumerate(node.args):
            self.context.append(getattr(functions, function_name).arguments[index])
            self.tag_argument(function_name, index, argument)
            self.context.pop()

    def tag_functionIdentifier(self, node):
        tag_name = "%s_%d_call"%(node.v, self.lineno)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textWidget.tag_add(tag_name, start_index, end_index)
        self.textWidget.tag_bind(tag_name, "<Enter>", lambda e: context.helpv.set(getattr(functions,node.v).help))

    def tag_argument(self, function_name, index, node):
        local_context = self.context[:]
        def on_enter(event):
            context.helpv.set(local_context[-1].help)
            shapes = interpretor.state.shapes
            for shape in shapes:
                if shape.lineno == self.lineno:
                    shape.show_helper(index, context.canvas)
        def on_leave(event):
            context.helpv.set("")
            shapes = interpretor.state.shapes
            for shape in shapes:
                if shape.lineno == self.lineno:
                    shape.hide_helper(context.canvas)
        tag_name = "%s_%d_arg_%d"%(function_name, self.lineno, index)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textWidget.tag_add(tag_name, start_index, end_index)
        self.textWidget.tag_bind(tag_name, "<Enter>", on_enter)
        self.textWidget.tag_bind(tag_name, "<Leave>", on_leave)
        self.directChild = True
        self.tag(node)
        self.directChild = False

    def tag_Identifier(self, node):
        def on_enter(event):
            context.text.tag_configure("%s_assign"%node.v, foreground="red")
        def on_leave(event):
            context.text.tag_configure("%s_assign"%node.v, foreground="")
        tag_name = "%s_%d"%(node.v, self.lineno)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textWidget.tag_bind(tag_name, "<Enter>", on_enter)
        self.textWidget.tag_bind(tag_name, "<Leave>", on_leave)
        self.textWidget.tag_add(tag_name, start_index, end_index)

    def tag_Paren(self, node):
        self.tag(node.v)

    def tag_BinaryOp(self, node):
        self.directChild = False
        self.tag(node.x)
        self.tag(node.y)

    def tag_Int(self, node):
        def on_enter(event):
            global target
            target = NodeChanger(self.lineno, node, tag_name, event.x, modifier)
            self.textWidget["cursor"] = "sb_h_double_arrow"
        def on_leave(event):
            global target
            target = None
            self.textWidget["cursor"] = ""
        tag_name = "num_%d_%d"%(self.lineno, node.start)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        modifier = int_scale
        if self.directChild:
            modifier = self.context[-1].scale
        self.textWidget.tag_add(tag_name, start_index, end_index)
        self.textWidget.tag_bind(tag_name, "<Enter>", on_enter, add="+")
        self.textWidget.tag_bind(tag_name, "<Leave>", on_leave, add="+")
        self.textWidget.tag_configure(tag_name, foreground="blue")

    def tag_If(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 2c"%(start_index)
        self.textWidget.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)

    def tag_While(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 5c"%(start_index)
        self.textWidget.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)


class NodeChanger:
    def __init__(self, lineno, token, tag_name, mouse_coord, modifier):
        self.lineno = lineno
        self.token = token
        self.tag_name = tag_name
        self.x = mouse_coord
        self.modifier = modifier

    def __call__(self, event):
        dx = event.x - self.x
        self.x = event.x
        if not dx:
            return "break"

        val = self.modifier(self.token.v, dx<0)
        self.token.v = val
        self.token._node.v = val
        start_index = "%d.%d"%(self.lineno, self.token.start)
        end_index = "%d.%d"%(self.lineno, self.token.end)
        context.text.replace(start_index, end_index, val, self.tag_name)
        self.token.end = self.token.start + len("%s"%val)

        draw_state(interpretor.state)
        return "break"
        
class Context:
    pass


target = None
context = Context()
prog = []
source = []
interpretor = None
everythingGenerated = set()

def on_keyRelease(*args):
    update_from_text()

def update_from_text():
    global prog
    global source
    global interpretor
    if not context.text.edit_modified():
        return
    prog = []
    content = context.text.get("1.0", "end")
    source = list(enumerate(content.split('\n'), 1))
    [context.text.tag_remove(n, "1.0", "end") for n in context.text.tag_names()]
    for lineno, line in source:
        if not line or line.isspace():
            continue
        instruction = grammar.parse_instruction(line)
        actor = instruction(context)
        LineTagger(context.text, lineno).tag(instruction)
        prog.append((lineno, actor))

    interpretor = interpreter.Interpreter(prog, source)
    state = interpretor.run_prog()

    draw_state(state)

    context.text.edit_modified(False)

def draw_state(state):
    context.canvas.delete('all')
    for shape in state.shapes:
        shape.draw(context.canvas)
        
def on_motion(event):
    if target is None:
        return "break"
    return target(event)

def on_release(event):
    global target
    target = None
    update_from_text()

def main():
    root = tkinter.Tk()
    context.canvas = canvas = tkinter.Canvas(root, bg="white")
    canvas.pack(side="right", fill="y")
    context.text = text = tkinter.Text(root)
    text.pack()
    text.bind("<KeyRelease>", on_keyRelease)
    text.bind("<Button1-Motion>", on_motion)
    text.bind("<Button1-ButtonRelease>", on_release)
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
while x < 10
  y = 0
  while y < 10
    fill(25*x, 25*y, 0)
    rectangle(500+50*x, 500+50*y, 30, 30)
    y = y + 1
  x = x + 1""")
    font = tkinter.font.Font(font=text['font'])
    font.configure(weight='bold')
    text.tag_configure("keyword", foreground="darkgreen", font=font)
    context.helpv = tkinter.StringVar()
    label = tkinter.Label(root, textvariable=context.helpv)
    label.pack()
    root.after(100, on_keyRelease)
    root.mainloop()


if __name__ == '__main__':
    main()

