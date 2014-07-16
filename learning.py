#!/usr/bin/env python3


import tkinter, ast
import functions as func_module
import parser
from pprint import pprint
from symbol import sym_name

def int_scale(value, neg):
    return value + (1-2*neg)


class PrintFunctionCall(ast.NodeVisitor):
    def __init__(self):
        self.context = []

    def tag_function(self, function_name, lineno, start_index, end_index):
        tag_name = "%s_%d_call"%(function_name, lineno)
        text.tag_add(tag_name, start_index, end_index)
        text.tag_configure(tag_name, foreground="red")
        text.tag_bind(tag_name, "<Enter>", lambda e: helpv.set(functions[function_name].help))

    def visit_argument(self, function_name, index, node):
        visitor_name = "visit_arg_%s"%node.__class__.__name__
        if hasattr(self, visitor_name):
            return getattr(self, visitor_name)(function_name, index, node)

    def visit_arg_UnaryOp(self, function_name, index, node):
        if node.op.__class__.__name__ != "USub" or node.operand.__class__.__name__ != "Num":
            return self.visit(node.operand)

        #This is a negative number
        return self.visit_arg_Num(function_name, index, node.operand, True)

    def visit_arg_Num(self, function_name, index, node, neg=False):
        def on_enter(event):
            global target
            print("setting target")
            target = Target(val, tag_name, start_index, event.x, functions[function_name].arguments[index].scale)
            text["cursor"] = "sb_h_double_arrow"
            helpv.set(functions[function_name].arguments[index].help)
        def on_leave(event):
            global target
            print("unset target")
            target = None
            text["cursor"] = ""
        tag_name = "%s_%d_arg_%d"%(function_name, node.lineno, index)
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

    def visit_UnaryOp(self, node):
        if node.op.__class__.__name__ != "USub" or node.operand.__class__.__name__ != "Num":
            return self.visit(node.operand)

        return self.visit_Num(node.operand, True)

    def visit_Num(self, node, neg=False):
        if self.context[-1][0] == 'Call':
            return self.visit_arg_Num(self.context[-1][1], self.context[-1][2], node)
        def on_enter(event):
            global target
            print("setting target")
            target = Target(val, tag_name, start_index, event.x, int_scale)
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

    def visit_Call(self, node):
        function_name = node.func.id
        start_index = "%d.%d"%(node.lineno, node.col_offset)
        end_index = "%s + %d c"%(start_index, len(function_name))
        self.tag_function(function_name, node.lineno, start_index, end_index)
        for index, argument in enumerate(node.args):
            self.context.append(('Call', node, index))
            self.visit_argument(function_name, index, argument)
            self.context.pop()

    def visit_Module(self, node):
        self.context.append(('Module', node))
        for n in node.body:
            self.visit(n)
        self.context.pop()


class Target:
    def __init__(self, value, tag_name, start_index, mouse_coord, modifier):
        self.value = value
        self.tag_name = tag_name
        self.start_index = start_index
        self.x = mouse_coord
        self.modifier = modifier

    def __call__(self, event):
        dx = event.x - self.x
        self.x = event.x
        if not dx:
            return "break"

        val = self.modifier(self.value, dx<0)
        end_index = "%s + %dc"%(self.start_index, len("%d"%self.value))
        self.value = val
        print("replace", self.start_index, end_index, val, self.tag_name)
        text.replace(self.start_index, end_index, val, self.tag_name)
        eval_content()
        return "break"
        

helpv = None
text = None
label = None
target = None
canvas = None

context = {'fillColor': "#000000", 'x_canvas_range':[0, 100], 'y_canvas_range':[0, 100]}

def on_keyRelease(*args):
    update_ast()
    eval_content()

def update_ast():
    print("text changed")
    content = text.get("1.0", "end")
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print("cannot parse text")
    else:
        [text.tag_remove(n, "1.0", "end") for n in text.tag_names()]
        #pprint(tree)
        #print(ast.dump(tree, include_attributes=True))
        PrintFunctionCall().visit(tree)

def on_motion(event):
    if target is None:
        print("target is none")
        return "break"
    return target(event)

def eval_content():
    canvas.delete("all")
    content = text.get("1.0", "end")
    exec(content, functions)

def on_release(event):
    global target
    target = None
    update_ast()
    eval_content()

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
ellipse(10, 10, 10, 10)
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
