
import functions

def int_scale(value, neg):
    return value + (1-2*neg)

class LineTagger:
    def __init__(self, textTagger, lineno):
        self.textTagger = textTagger
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
        self.textTagger.text.tag_add(tag_name, start_index, end_index)
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
        self.textTagger.text.tag_add(tag_name, start_index, end_index)
        self.textTagger.text.tag_bind(tag_name, "<Enter>", lambda e: self.textTagger.text.helpv.set(getattr(functions,node.v).help))

    def tag_argument(self, function_name, index, node):
        local_context = self.context[:]
        def on_enter(event):
            self.textTagger.text.helpv.set(local_context[-1].help)
            self.textTagger.canvas.show_helper(self.lineno, index)
        def on_leave(event):
            self.textTagger.text.helpv.set("")
            self.textTagger.canvas.hide_helpers()
        tag_name = "%s_%d_arg_%d"%(function_name, self.lineno, index)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textTagger.text.tag_add(tag_name, start_index, end_index)
        self.textTagger.text.tag_bind(tag_name, "<Enter>", on_enter)
        self.textTagger.text.tag_bind(tag_name, "<Leave>", on_leave)
        self.directChild = True
        self.tag(node)
        self.directChild = False

    def tag_Identifier(self, node):
        def on_enter(event):
            self.textTagger.text.tag_configure("%s_assign"%node.v, foreground="red")
        def on_leave(event):
            self.textTagger.text.tag_configure("%s_assign"%node.v, foreground="")
        tag_name = "%s_%d"%(node.v, self.lineno)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.textTagger.text.tag_bind(tag_name, "<Enter>", on_enter)
        self.textTagger.text.tag_bind(tag_name, "<Leave>", on_leave)
        self.textTagger.text.tag_add(tag_name, start_index, end_index)

    def tag_Paren(self, node):
        self.tag(node.v)

    def tag_BinaryOp(self, node):
        self.directChild = False
        self.tag(node.x)
        self.tag(node.y)

    def tag_Int(self, node):
        def on_enter(event):
            self.textTagger.text.target = NodeChanger(self.textTagger, self.lineno, node, tag_name, event.x, modifier)
            self.textTagger.text["cursor"] = "sb_h_double_arrow"
        def on_leave(event):
            self.textTagger.text.target = None
            self.textTagger.text["cursor"] = ""
        tag_name = "num_%d_%d"%(self.lineno, node.start)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        modifier = int_scale
        if self.directChild:
            modifier = self.context[-1].scale
        self.textTagger.text.tag_add(tag_name, start_index, end_index)
        self.textTagger.text.tag_bind(tag_name, "<Enter>", on_enter, add="+")
        self.textTagger.text.tag_bind(tag_name, "<Leave>", on_leave, add="+")
        self.textTagger.text.tag_configure(tag_name, foreground="blue")

    tag_Float = tag_Int

    def tag_If(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 2c"%(start_index)
        self.textTagger.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)

    def tag_While(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 5c"%(start_index)
        self.textTagger.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)


class NodeChanger:
    def __init__(self, textTagger, lineno, token, tag_name, mouse_coord, modifier):
        self.textTagger = textTagger
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

        self.textTagger.changing = True
        val = self.modifier(self.token.v, dx<0)
        self.token.v = val
        self.token._node.v = val
        self.token._node.clean_cache()
        start_index = "%d.%d"%(self.lineno, self.token.start)
        end_index = "%d.%d"%(self.lineno, self.token.end)
        self.textTagger.text.replace(start_index, end_index, val, self.tag_name)
        self.token.end = self.token.start + len("%s"%val)
        self.textTagger.changing = False

        return "break"

class TextTagger:
    def __init__(self, text, canvas):
        self.text = text
        self.canvas = canvas
        self.changing = False

    def tag_line(self, lineno, instruction):
        LineTagger(self, lineno).tag(instruction)
