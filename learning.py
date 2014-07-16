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

class Tagger:
    def __init__(self):
        self.context = []

    def tag(self, node):
        sub_executor = getattr(self, "tag_%s"%node.klass)
        return sub_executor(node)

    def tag_Program(self, node):
        for part in node.parts:
            self.tag(part)

    def tag_Call(self, node):
        function_name = node.name.v
        self.tag_function(function_name, node.name._start.row, node.name.start, node.name.end)
        for index, argument in enumerate(node.args):
            self.context.append(node)
            self.tag_argument(function_name, index, argument)
            self.context.pop()
        

    def tag_function(self, function_name, lineno, start_index, end_index):
        tag_name = "%s_%d_call"%(function_name, lineno)
        text.tag_add(tag_name, start_index, end_index)
        text.tag_configure(tag_name, foreground="red")
        text.tag_bind(tag_name, "<Enter>", lambda e: helpv.set(functions[function_name].help))

    def tag_argument(self, function_name, index, node):
        visitor_name = "tag_arg_%s"%node.klass
        if hasattr(self, visitor_name):
            return getattr(self, visitor_name)(function_name, index, node)

    def tag_arg_Int(self, function_name, index, node):
        def on_enter(event):
            global target
            print("setting target")
            target = NodeChanger(node, tag_name, event.x, functions[function_name].arguments[index].scale)
            text["cursor"] = "sb_h_double_arrow"
            helpv.set(functions[function_name].arguments[index].help)
        def on_leave(event):
            global target
            print("unset target")
            target = None
            text["cursor"] = ""
        tag_name = "%s_%d_arg_%d"%(function_name, node._start.row, index)
        start_index = node.start
        end_index = node.end
        text.tag_add(tag_name, start_index, end_index)
        text.tag_bind(tag_name, "<Enter>", on_enter)
        text.tag_bind(tag_name, "<Leave>", on_leave)
        text.tag_configure(tag_name, foreground="blue")

    def visit_Num(self, node, neg=False):
        if self.context[-1][0] == 'Call':
            return self.visit_arg_Num(self.context[-1][1], self.context[-1][2], node)
        def on_enter(event):
            global target
            print("setting target")
            target = NodeChanger(node, tag_name, event.x, int_scale)
            text["cursor"] = "sb_h_double_arrow"
        def on_leave(event):
            global target
            print("unset target")
            target = None
            text["cursor"] = ""
        tag_name = "num_%d_%d"%(node.lineno, node.col_offset)
        start_index = "%d.%d"%(node.lineno, node.col_offset)
        val = node.n
        if neg:
            start_index = "%s - 1c"%start_index
            val *= -1
        end_index = "%s + %d c"%(start_index, len("%d"%val))
        text.tag_add(tag_name, start_index, end_index)
        text.tag_bind(tag_name, "<Enter>", on_enter)
        text.tag_bind(tag_name, "<Leave>", on_leave)
        text.tag_configure(tag_name, foreground="blue")


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
        execute_tree()
        return "break"
        

helpv = None
text = None
label = None
target = None
canvas = None
tree = None

context = {'fillColor': "#000000", 'x_canvas_range':[0, 100], 'y_canvas_range':[0, 100]}

class Executor:
    def __init__(self, namespace=None):
        if namespace is None:
            namespace = {}
        self.namespace = namespace

    def execute(self, node):
        sub_executor = getattr(self, "execute_%s"%node.klass)
        return sub_executor(node)

    def execute_Program(self, node):
        for part in node.parts:
            self.execute(part)

    def execute_Call(self, node):
        function = self.namespace[node.name.v]
        args = [self.execute(n) for n in node.args]
        return function(*args)


    def execute_Int(self, node):
        return node.v

    def execute_Float(self, node):
        return node.v
    

def on_keyRelease(*args):
    update_from_text()

def update_from_text():
    global tree
    content = text.get("1.0", "end")
    try:
        tree = grammar.parse(content)
    except picoparse.NoMatch:
        tree = tokens.Program([], picoparse.text.Pos(0, 0), picoparse.text.Pos(0, 0))
    tag_text_from_tree()
    execute_tree()

def execute_tree():
    canvas.delete("all")
    Executor(functions).execute(tree)

def tag_text_from_tree():
    [text.tag_remove(n, "1.0", "end") for n in text.tag_names()]
    Tagger().tag(tree)

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
ellipse(10, -10, 10, 10)
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
