
import tkinter
from libs.painter import actors

def int_scale(value, neg):
    return value + (1-2*neg)

class LineTagger:
    def __init__(self, text, lineno):
        self.text = text
        self.lineno = lineno

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
        for argument in node.args:
            self.tag(argument)

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
        self.tag(node.x)
        self.tag(node.y)

    def tag_Int(self, node):
        start_index = "%d.%d"%(self.lineno, node.start)
        end_index = "%d.%d"%(self.lineno, node.end)
        self.text.tag_add("number", start_index, end_index)

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

    def tag_FunctionDef(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + 8c"%(start_index)
        self.text.tag_add("keyword", start_index, end_index)

    def tag_Comment(self, instruction):
        self.text.tag_add("comment", "%d.0"%self.lineno, "%d.0 lineend"%self.lineno)


class TextModifier:
    def __init__(self, program, text):
        self.program = program
        self.text = text
        self.token = None
        self.changing = False

    def on_enter(self, event):
        self.text["cursor"] = "sb_h_double_arrow"
        current = self.text.index("current")
        self.lineno, pos = (int(i) for i in current.split('.'))
        parsed = self.program.source[self.lineno-1].parsed
        self.token = parsed.get_token_at_pos(pos)
        self.x = event.x
        self.modifier = int_scale
        if parsed.klass == "Call" and hasattr(actors, parsed.name.v):
            functionDef = getattr(actors, parsed.name.v)
            if self.token in parsed.args:
                self.modifier = functionDef.arguments[parsed.args.index(self.token)].scale

    def on_leave(self, event):
        self.text["cursor"] = ""
        self.token = None

    def on_move(self, event):
        if self.token is None:
            return "break"
        dx = event.x - self.x
        self.x = event.x
        if not dx:
            return "break"

        self.changing = True
        val = self.modifier(self.token.v, dx<0)
        self.token.v = val
        self.token._node.v = val
        self.token._node.clean_cache()
        start_index = "%d.%d"%(self.lineno, self.token.start)
        end_index = "%d.%d"%(self.lineno, self.token.end)
        self.text.replace(start_index, end_index, val, "number")
        self.token.end = self.token.start + len("%s"%val)
        self.program.event("token_changed")()
        return "break"

    def on_release(self, event):
        if self.changing:
            self.token = None
            self.changing = False
            self.program.event("source_changed")()

class TextInput(tkinter.Text):
    def __init__(self, parent, program):
        tkinter.Text.__init__(self, parent)
        self.program = program

        font = tkinter.font.Font(font=self['font'])
        font.configure(weight='bold')
        self.tag_configure("keyword", foreground="darkgreen", font=font)
        self.tag_configure("invalidSyntax", background="#FFBBBB")
        self.tag_configure("highlihgt", background="#FFFF99")
        self.tag_configure("number", foreground="blue")
        self.tag_configure("comment", foreground="grey")

        self.textModifier = TextModifier(self.program, self)
        self.tag_bind("number", "<Enter>", self.textModifier.on_enter)
        self.tag_bind("number", "<Leave>", self.textModifier.on_leave)
        self.bind("<Button1-Motion>", self.textModifier.on_move)
        self.bind("<Button1-ButtonRelease>", self.textModifier.on_release)

        self.program.connect("source_changed", self.on_modified)
        self.program.connect("activeStep_changed", self.on_activeStep_changed)
        for line in program.source:
            self.insert("end", str(line)+"\n")

        self.edit_modified(False)
        self.bind("<<Modified>>", self.on_textModified)
        self.bind("<Motion>", self.on_motion)

    def on_motion(self, event):
        current = self.index("current")
        current = [int(i) for i in current.split('.')]
        self.program.set_current(current)

    def on_textModified(self, event):
        self.edit_modified(False)
        if not self.textModifier.changing:
            lines = self.get("1.0", "end").split("\n")
            for lineno, line in enumerate(lines):
                self.program.update_text(lineno, line)
            self.program.clean_after(lineno)
            self.program.event("source_changed")()

    def on_modified(self):
        self.clean_tags()
        for line in self.program.source:
            if line.valid:
                self.tag_line(line)
            else:
                self.tag_add("invalidSyntax", "%d.%d"%(line.lineno, line.level), "%d.0 lineend"%line.lineno)

    def on_activeStep_changed(self, step):
        self.tag_remove("highlihgt", "1.0", "end")
        self.tag_add("highlihgt", "%d.0"%self.program.steps[step].lineno, "%d.0 +1l"%self.program.steps[step].lineno)

    def place(self):
        self.pack(side="left", fill="y", expand=0)

    def clean_tags(self):
        [self.tag_remove(n, "1.0", "end") for n in self.tag_names()]

    def tag_line(self, line):
        LineTagger(self, line.lineno).tag(line.parsed)

