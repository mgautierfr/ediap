
import tkinter

class HelpShower(tkinter.Label):
    def __init__(self, parent, program):
        self.helpv = tkinter.StringVar()
        tkinter.Label.__init__(self, parent, textvariable=self.helpv)
        self.program = program
        program.connect("current_changed", self.on_current_changed)
        program.connect("activeStep_changed", self.on_activeStep_changed)

    def on_current_changed(self):
        line, pos = self.program.current
        try:
            parsed = self.program.source[line-1].parsed
        except IndexError:
            return

        self.helpv.set("")
        if parsed is None or parsed.klass != "Call":
            return

        function_name = parsed.name.v
        try:
            functionDef = getattr(self.program.lib, function_name)
        except AttributeError:
            return

        if parsed.name.start <= pos <= parsed.name.end:
            self.helpv.set(functionDef.help)
            return

        for index, arg in enumerate(parsed.args):
            if arg.start <= pos <= arg.end:
                break
        else:
            index = None
        if index is not None:
            self.helpv.set(functionDef.arguments[index].help)
            return

    def on_activeStep_changed(self,step):
        help = self.program.steps[self.program.displayedStep].help
        lineno =  self.program.steps[self.program.displayedStep].lineno
        self.helpv.set("")
        try:
            self.helpv.set(help[lineno])
        except KeyError:
            pass
