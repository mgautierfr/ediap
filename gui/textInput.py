# This file is part of Edia.
#
# Ediap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Edia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edia.  If not, see <http://www.gnu.org/licenses/>

# Copyright 2014 Matthieu Gautier dev@mgautier.fr

import tkinter, tkinter.font
import re

def int_scale(value, neg):
    return value + (1-2*neg)

class LineTagger:
    def __init__(self, text, lineno, textValue):
        self.text = text
        self.lineno = lineno
        self.textValue = textValue

    def tag(self, node):
        sub_executor = getattr(self, "tag_%s"%node.klass, None)
        if sub_executor:
            return sub_executor(node)

    def tag_Set(self, node):
        tag_name = "%s_assign"%(node.name.v)
        start_index = "%d.%d"%(self.lineno, node.name.start)
        end_index = "%d.%d"%(self.lineno, node.name.end)
        self.text.tag_add(tag_name, start_index, end_index)
        self.tag(node.value)

    def tag_Do_subprogram(self, node):
        start_index = "%d.%d"%(self.lineno, node.level)
        end_index = "%s + 2c"%(start_index)
        self.text.tag_add("keyword", start_index, end_index)
        for argument in node.args:
            self.tag(argument)

    def tag_Builtin(self, node):
        start_index = "%d.%d"%(self.lineno, node.name.start)
        end_index = "%d.%d"%(self.lineno, node.name.end)
        self.text.tag_add("builtin", start_index, end_index)
        for argument in node.arguments:
            self.tag(argument)
        for argument in node.kwords.values():
            self.tag(argument)

    def tag_CustomToken(self, node):
        for argument in node.arguments:
            self.tag(argument)
        for argument in node.kwords.values():
            self.tag(argument)

    def tag_Identifier(self, node):
        def on_enter(event):
            self.text.tag_configure("%s_assign"%node.v, foreground="red")
            self.text.tag_configure("%s_decl"%node.v, foreground="red")
        def on_leave(event):
            self.text.tag_configure("%s_assign"%node.v, foreground="")
            self.text.tag_configure("%s_decl"%node.v, foreground="")
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
        end_index = "%s + %sc"%(start_index, len("if"))
        self.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)

    def tag_While(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + %dc"%(start_index, len("while"))
        self.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.test)

    def tag_Loop(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + %dc"%(start_index, len("loop"))
        self.text.tag_add("keyword", start_index, end_index)
        match = re.search(r"times", self.textValue)
        start_index = "%d.%d"%(self.lineno, match.start())
        end_index = "%d.%d"%(self.lineno, match.end())
        self.text.tag_add("keyword", start_index, end_index)
        self.tag(instruction.value)

    def tag_Create_subprogram(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%d.%d"%(self.lineno, instruction.name.start)
        #end_index = "%s + %dc"%(instruction.name.start, len("create"))
        self.text.tag_add("keyword", start_index, end_index)
        for (type_, arg) in instruction.args:
            tag_name = "%s_decl"%(arg.v)
            start_index = "%d.%d"%(self.lineno, arg.start)
            end_index = "%d.%d"%(self.lineno, arg.end)
            self.text.tag_add(tag_name, start_index, end_index)

    def tag_Comment(self, instruction):
        self.text.tag_add("comment", "%d.0"%self.lineno, "%d.0 lineend"%self.lineno)

    def tag_Create(self, instruction):
        start_index = "%d.%d"%(self.lineno, instruction.level)
        end_index = "%s + %dc"%(start_index, len("create"))
        self.text.tag_add("keyword", start_index, end_index)
        start_index = "%d.%d"%(self.lineno, instruction.type_.start)
        end_index = "%d.%d"%(self.lineno, instruction.type_.end)
        self.text.tag_add("keyword", start_index, end_index)
        tag_name = "%s_decl"%(instruction.name.v)
        start_index = "%d.%d"%(self.lineno, instruction.name.start)
        end_index = "%d.%d"%(self.lineno, instruction.name.end)
        self.text.tag_add(tag_name, start_index, end_index)


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
        if parsed.klass != "Builtin":
            return
        try:
            functionDef = getattr(self.program.lib, parsed.name.v)
        except AttributeError:
            return
        # does the token we are tagging is a "kwords one" ?
        for name, value in instructionNode.kwords.items():
            if self.token == value:
                break
        else:
            name = None

        if name :
            # the token is a "kwords one".
            self.modifier = functionDef.arguments[name].scale
        else:
            # this is a classical argument.
            index = 0
            for name in functionDef.arguments_order:
                if name in instructionNode.kwords:
                    continue
                value = instructionNode.arguments[index]
                if self.token == value:
                    self.modifier = functionDef.arguments[name].scale
                    break
                index += 1

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
            self.text.edit_modified(True)

class TextInput(tkinter.Text):
    def __init__(self, parent, program):
        tkinter.Text.__init__(self, parent)
        self.program = program

        font = tkinter.font.Font(font=self['font'])
        font.configure(weight='bold')
        self.tag_configure("keyword", foreground="darkgreen", font=font)
        self.tag_configure("builtin", foreground="darkgreen")
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
        for line in program.source[:-1]:
            self.insert("end", str(line)+"\n")
        self.insert("end", str(program.source[-1]))

        self.edit_modified(False)
        self.bind("<<Modified>>", self.on_textModified)
        self.bind("<Motion>", self.on_motion)
        self.bind("<FocusIn>", self.on_focus)

    def on_focus(self, event):
        self.program.displayedStep =  len(self.program.steps)

    def on_motion(self, event):
        current = self.index("current")
        current = [int(i) for i in current.split('.')]
        self.program.set_current(current)

    def on_textModified(self, event):
        if not self.edit_modified():
            return
        self.edit_modified(False)
        self.program.displayedStep =  len(self.program.steps)
        if not self.textModifier.changing:
            lines = self.get("1.0", "end").split("\n")
            for lineno, line in enumerate(lines):
                self.program.update_text(lineno, line)
            self.program.clean_after(lineno)
            self.program.event("source_changed")()

    def on_modified(self):
        self.clean_tags()
        for line in self.program.source:
            if line.empty:
                continue
            if line.parsed is not None:
                self.tag_line(line)
            else:
                self.tag_add("invalidSyntax", "%d.%d"%(line.lineno, line.level), "%d.0 lineend"%line.lineno)

    def on_activeStep_changed(self, step):
        self.tag_remove("highlihgt", "1.0", "end")
        try:
            self.tag_add("highlihgt", "%d.0"%self.program.steps[step].lineno, "%d.0 +1l"%self.program.steps[step].lineno)
        except IndexError:
            pass

    def clean_tags(self):
        [self.tag_remove(n, "1.0", "end") for n in self.tag_names()]

    def tag_line(self, line):
        LineTagger(self, line.lineno, line.text).tag(line.parsed)

