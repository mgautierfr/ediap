
import tkinter
import functions

def int_scale(value, neg):
    return value + (1-2*neg)

class NodeChanger:
    def __init__(self, text, lineno, token, tag_name, mouse_coord, modifier):
        self.text = text
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

        self.text.changing = True
        val = self.modifier(self.token.v, dx<0)
        self.token.v = val
        self.token._node.v = val
        self.token._node.clean_cache()
        start_index = "%d.%d"%(self.lineno, self.token.start)
        end_index = "%d.%d"%(self.lineno, self.token.end)
        self.text.replace(start_index, end_index, val, self.tag_name)
        self.token.end = self.token.start + len("%s"%val)
        self.text.changing = False

        return "break"

class LineTagger:
    def __init__(self, text, lineno):
        self.text = text
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
        self.text.tag_add(tag_name, start_index, end_index)
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
        self.text.tag_add(tag_name, start_index, end_index)
        self.text.tag_bind(tag_name, "<Enter>", lambda e: self.text.helpv.set(getattr(functions,node.v).help))

    def tag_argument(self, function_name, index, node):
        local_context = self.context[:]
        def on_enter(event):
            self.text.helpv.set(local_context[-1].help)
            self.text.program.show_helper(self.lineno, index)
        def on_leave(event):
            self.text.helpv.set("")
            self.text.program.hide_helpers()
        tag_name = "%s_%d_arg_%d"%(function_name, self.lineno, index)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.text.tag_add(tag_name, start_index, end_index)
        self.text.tag_bind(tag_name, "<Enter>", on_enter)
        self.text.tag_bind(tag_name, "<Leave>", on_leave)
        self.directChild = True
        self.tag(node)
        self.directChild = False

    def tag_Identifier(self, node):
        def on_enter(event):
            self.text.tag_configure("%s_assign"%node.v, foreground="red")
        def on_leave(event):
            self.text.tag_configure("%s_assign"%node.v, foreground="")
        tag_name = "%s_%d"%(node.v, self.lineno)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.text.tag_bind(tag_name, "<Enter>", on_enter)
        self.text.tag_bind(tag_name, "<Leave>", on_leave)
        self.text.tag_add(tag_name, start_index, end_index)

    def tag_Paren(self, node):
        self.tag(node.v)

    def tag_BinaryOp(self, node):
        self.directChild = False
        self.tag(node.x)
        self.tag(node.y)

    def tag_Int(self, node):
        def on_enter(event):
            self.text.target = NodeChanger(self.text, self.lineno, node, tag_name, event.x, modifier)
            self.text["cursor"] = "sb_h_double_arrow"
        def on_leave(event):
            self.text.target = None
            self.text["cursor"] = ""
        tag_name = "num_%d_%d"%(self.lineno, node.start)
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        modifier = int_scale
        if self.directChild:
            modifier = self.context[-1].scale
        self.text.tag_add(tag_name, start_index, end_index)
        self.text.tag_bind(tag_name, "<Enter>", on_enter, add="+")
        self.text.tag_bind(tag_name, "<Leave>", on_leave, add="+")
        self.text.tag_configure(tag_name, foreground="blue")

    tag_Float = tag_Int

    def tag_If(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 2c"%(start_index)
        self.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)

    def tag_While(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 5c"%(start_index)
        self.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)

class TextInput(tkinter.Text):
    def __init__(self, parent, helpv, program):
        tkinter.Text.__init__(self, parent)
        self.program = program
        self.bind("<Button1-Motion>", self.on_motion)
        self.bind("<Button1-ButtonRelease>", self.on_release)
        font = tkinter.font.Font(font=self['font'])
        font.configure(weight='bold')
        self.tag_configure("keyword", foreground="darkgreen", font=font)
        self.tag_configure("invalidSyntax", background="#FFBBBB")
        self.tag_configure("highlihgt", background="#FFFF99")
        self.target = None
        self.helpv = helpv
        self.changing = False
        self.program.connect("source_modified", self.on_modified)
        self.program.connect("displayedStepChange", self.on_displayedStepChange)
        for line in program.source:
            self.insert("end", str(line)+"\n")

        self.edit_modified(False)
        self.bind("<<Modified>>", self.on_textModified)

    def on_textModified(self, event):
        lines = self.get("1.0", "end").split("\n")
        for lineno, line in enumerate(lines):
            try:
                if line != self.program.source[lineno].text:
                    self.program.update_text(lineno, line, self.changing)
            except IndexError:
                pass
        self.edit_modified(False)
            

    def on_modified(self, directChange):
        if directChange:
            return
        self.clean_tags()
        for line in self.program.source:
            if line.valid:
                pass
                self.tag_line(line)
            else:
                self.tag_add("invalidSyntax", "%d.%d"%(line.lineno, line.level), "%d.0 lineend"%line.lineno)

    def on_displayedStepChange(self, step):
        self.tag_remove("highlihgt", "1.0", "end")
        self.tag_add("highlihgt", "%d.0"%self.program.steps[step].lineno, "%d.0 +1l"%self.program.steps[step].lineno)

    def place(self):
        self.pack(side="left", fill="y", expand=0)

    def on_motion(self, event):
        if self.target is None:
            return "break"
        return self.target(event)
    
    def on_release(self, event):
        self.target = None
        self.program.event("source_modified")(False)

    def clean_tags(self):
        [self.tag_remove(n, "1.0", "end") for n in self.tag_names()]

    def tag_line(self, line):
        LineTagger(self, line.lineno).tag(line.parsed)
