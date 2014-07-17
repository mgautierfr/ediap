#!/usr/bin/env python3


import tkinter
import functions as func_module
from pprint import pprint
import grammar
from collections import ChainMap

def int_scale(value, neg):
    return value + (1-2*neg)

class LineTagger:
    def __init__(self, functions, textWidget, lineno):
        self.functions = functions
        self.textWidget = textWidget
        self.lineno = lineno
        self.directChild = False
        self.context = []

    def tag(self, node):
        sub_executor = getattr(self, "tag_%s"%node.klass, None)
        if sub_executor:
            return sub_executor(node)

    def tag_Assignement(self, node):
        self.tag(node.value)

    def tag_Call(self, node):
        function_name = node.name.v
        self.tag_functionIdentifier(node.name)
        for index, argument in enumerate(node.args):
            self.context.append(self.functions[function_name].arguments[index])
            self.tag_argument(function_name, index, argument)
            self.context.pop()
        

    def tag_functionIdentifier(self, node):
        tag_name = "%s_%d_call"%(node.v, self.lineno)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textWidget.tag_add(tag_name, start_index, end_index)
        self.textWidget.tag_configure(tag_name, foreground="red")
        self.textWidget.tag_bind(tag_name, "<Enter>", lambda e: context.helpv.set(self.functions[node.v].help))

    def tag_argument(self, function_name, index, node):
        local_context = self.context[:]
        def on_enter(event):
            context.helpv.set(local_context[-1].help)
            #[actor.show_helper(index) for actor in actors[self.lineno]]
        def on_leave(event):
            context.helpv.set("")
            #[actor.hide_helper() for actor in actors[self.lineno]]
        tag_name = "%s_%d_arg_%d"%(function_name, self.lineno, index)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textWidget.tag_add(tag_name, start_index, end_index)
        self.textWidget.tag_bind(tag_name, "<Enter>", on_enter)
        self.textWidget.tag_bind(tag_name, "<Leave>", on_leave)
        self.textWidget.tag_configure(tag_name, background="#CCFFCC")
        self.directChild = True
        self.tag(node)
        self.directChild = False

    def tag_Paren(self, node):
        self.tag(node.v)

    def tag_BinaryOp(self, node):
        self.directChild = False
        [self.tag(n) for n in node.args]

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


class NodeChanger:
    def __init__(self, lineno, node, tag_name, mouse_coord, modifier):
        self.lineno = lineno
        self.node = node
        self.tag_name = tag_name
        self.x = mouse_coord
        self.modifier = modifier

    def __call__(self, event):
        dx = event.x - self.x
        self.x = event.x
        if not dx:
            return "break"

        val = self.modifier(self.node.v, dx<0)
        self.node.v = val
        start_index = "%d.%d"%(self.lineno, self.node.start)
        end_index = "%d.%d"%(self.lineno, self.node.end)
        print("replace", start_index, end_index, val, self.tag_name)
        context.text.replace(start_index, end_index, val, self.tag_name)
        self.node.end = self.node.start + len("%s"%val)
        [actor.update() for actor in actors[self.lineno]]
        return "break"
        
class Context:
    pass


target = None
canvas = None
tree = None
context = Context()

class State:
    def __init__(self):
        self.shapes = []
        self.hiddenState = ChainMap({})
        self.namespace = ChainMap({})
        self.child = None

    def new_child(self):
        child = State()
        child.shapes = self.shapes[:]
        child.hiddenState = self.hiddenState.new_child()
        child.namespace = self.namespace.new_child()
        self.child = child
        return child

def on_keyRelease(*args):
    update_from_text()

def update_from_text():
    prog = []
    content = context.text.get("1.0", "end")
    lines = content.split('\n')
    for lineno, line in enumerate(lines):
        if not line or line.isspace():
            continue
        print("|%s|"%line)
        node = grammar.parse_instruction(line)
        LineTagger(functions, context.text, lineno+1).tag(node)
        print(node)
        actor = None
        if node.klass == "Call":
            function = functions[node.name.v]
            actor = function(context, *node.args)
        if node.klass == "Assignement":
            actor = func_module._setter(context, node.name.v, node.value)
        if node:
            prog.append((lineno, actor))

    pc = 0
    state = State()
    states = [state]
    state.hiddenState.update({'fillColor': "#000000", 'x_canvas_range':[0, 100], 'y_canvas_range':[0, 100]})
    while pc < len(prog):
        lineno, actor = prog[pc]
        state = state.new_child()
        actor.act(state)
        states.append(state)
        pc += 1

    context.canvas.delete('all')
    for shape in state.shapes:
        shape.draw(context.canvas)
        
def on_motion(event):
    if target is None:
        print("target is none")
        return "break"
    return target(event)

def on_release(event):
    global target
    target = None
    update_from_text()

def main():
    global functions
    root = tkinter.Tk()
    context.canvas = canvas = tkinter.Canvas(root, bg="white")
    canvas.pack(side="right", fill="y")
    context.text = text = tkinter.Text(root)
    text.pack()
    text.bind("<KeyRelease>", on_keyRelease)
    text.bind("<Button1-Motion>", on_motion)
    text.bind("<Button1-ButtonRelease>", on_release)
    text.insert("1.0", """x = 5
view(0, 0, 100, 100)
fill(0, 0, 255)
ellipse(10, 10+10, 10, 10)
fill(255, 0, 0)
ellipse(50, x*10, 50, 30)
""")
    context.helpv = tkinter.StringVar()
    label = tkinter.Label(root, textvariable=context.helpv)
    label.pack()
    functions = { k:v for k,v in func_module.__dict__.items() if not k.startswith("_") }
    root.after(100, on_keyRelease)
    root.mainloop()


if __name__ == '__main__':
    main()