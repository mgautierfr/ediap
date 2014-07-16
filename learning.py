#!/usr/bin/env python3


import tkinter
import functions as func_module
import parser
from pprint import pprint
import grammar
import tokens
import picoparse
import picoparse.text

def int_scale(value, neg):
    return value + (1-2*neg)

class Visitor:
    def __init__(self, namespace=None):
        if namespace is None:
            namespace = {}
        self.namespace = namespace
        self.context = []
        self.directChild = False

    def visit(self, node):
        sub_executor = getattr(self, "visit_%s"%node.klass)
        return sub_executor(node)

    def execute(self, node):
        sub_executor = getattr(self, "execute_%s"%node.klass)
        return sub_executor(node)

    def visit_Program(self, node):
        for part in node.parts:
            self.visit(part)

    def visit_Call(self, node):
        actor = self.execute(node)
        if actor:
            actors.setdefault(node._start.row, []).append(actor)
        function_name = node.name.v
        self.tag_function(function_name, node.name._start.row, node.name.start, node.name.end)
        for index, argument in enumerate(node.args):
            self.context.append((actor, self.namespace[function_name].arguments[index]))
            self.visit_argument(function_name, index, argument)
            self.context.pop()
        

    def tag_function(self, function_name, lineno, start_index, end_index):
        tag_name = "%s_%d_call"%(function_name, lineno)
        text.tag_add(tag_name, start_index, end_index)
        text.tag_configure(tag_name, foreground="red")
        text.tag_bind(tag_name, "<Enter>", lambda e: helpv.set(functions[function_name].help))

    def visit_argument(self, function_name, index, node):
        local_context = self.context[:]
        def on_enter(event):
            helpv.set(local_context[-1][1].help)
            [actor.show_helper(index) for actor in actors[node._start.row]]
        def on_leave(event):
            helpv.set("")
            [actor.hide_helper() for actor in actors[node._start.row]]
        tag_name = "%s_%d_arg_%d"%(function_name, node._start.row, index)
        start_index = node.start
        end_index = node.end
        text.tag_add(tag_name, start_index, end_index)
        text.tag_bind(tag_name, "<Enter>", on_enter)
        text.tag_bind(tag_name, "<Leave>", on_leave)
        text.tag_configure(tag_name, background="#CCFFCC")
        self.directChild = True
        self.visit(node)
        self.directChild = False

    def visit_Paren(self, node):
        self.visit(node.v)

    def visit_BinaryOp(self, node):
        self.directChild = False
        [self.visit(n) for n in node.args]

    def visit_Int(self, node):
        def on_enter(event):
            global target
            target = NodeChanger(node, tag_name, event.x, modifier)
            text["cursor"] = "sb_h_double_arrow"
        def on_leave(event):
            global target
            target = None
            text["cursor"] = ""
        tag_name = "num_%d_%d"%(node._start.row, node._start.col)
        start_index = node.start
        end_index = node.end
        modifier = int_scale
        if self.directChild:
            modifier = self.context[-1][1].scale
        text.tag_add(tag_name, start_index, end_index)
        text.tag_bind(tag_name, "<Enter>", on_enter, add="+")
        text.tag_bind(tag_name, "<Leave>", on_leave, add="+")
        text.tag_configure(tag_name, foreground="blue")

    def execute_Call(self, node):
        function = self.namespace[node.name.v]
        return function(*node.args)


class NodeChanger:
    def __init__(self, node, tag_name, mouse_coord, modifier):
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
        print("replace", self.node.start, self.node.end, val, self.tag_name)
        text.replace(self.node.start, self.node.end, val, self.tag_name)
        self.node._end.col = self.node._start.col + len("%s"%val)
        [actor.update() for actor in actors[self.node._start.row]]
        return "break"
        

helpv = None
text = None
label = None
target = None
canvas = None
tree = None

context = {'fillColor': "#000000", 'x_canvas_range':[0, 100], 'y_canvas_range':[0, 100]}


def on_keyRelease(*args):
    update_from_text()

def update_from_text():
    global tree
    content = text.get("1.0", "end")
    tree = grammar.parse(content)
    #try:
    #    tree = grammar.parse(content)
    #except picoparse.NoMatch:
    #    tree = tokens.Program([], picoparse.text.Pos(0, 0), picoparse.text.Pos(0, 0))
    execute_tree()

def execute_tree():
    global actors
    canvas.delete("all")
    [text.tag_remove(n, "1.0", "end") for n in text.tag_names()]
    actors = {}
    Visitor(functions).visit(tree)
    [actor.act() for linenb in sorted(actors.keys()) for actor in actors[linenb]]

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
    global text
    global label
    global helpv
    global canvas
    global functions
    root = tkinter.Tk()
    canvas = tkinter.Canvas(root, bg="white")
    canvas.pack(side="right", fill="y")
    text = tkinter.Text(root)
    text.pack()
    text.bind("<KeyRelease>", on_keyRelease)
    text.bind("<Button1-Motion>", on_motion)
    text.bind("<Button1-ButtonRelease>", on_release)
    text.insert("1.0", """view(0, 0, 100, 100)
fill(0, 0, 255)
ellipse(10, 10+10, 10, 10)
fill(255, 0, 0)
ellipse(50, 50, 50, 30)
""")
    helpv = tkinter.StringVar()
    label = tkinter.Label(root, textvariable=helpv)
    label.pack()
    context['canvas'] = canvas
    functions = { k:v(context) for k,v in func_module.__dict__.items() if not k.startswith("_") }
    root.after(100, on_keyRelease)
    root.mainloop()


if __name__ == '__main__':
    main()
