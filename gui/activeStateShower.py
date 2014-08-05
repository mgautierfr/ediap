
import tkinter
import tkinter.ttk

class ActiveStateShower(tkinter.Frame):
    def __init__(self, parent, program):
        tkinter.Frame.__init__(self, parent)
        self.canvas = tkinter.Canvas(self, bg="white")
        self.canvas.pack(side="top")
        self.canvasState = tkinter.ttk.Treeview(self, columns=('value',))
        self.canvasState.pack()
        self.variables = tkinter.ttk.Treeview(self, columns=('value',))
        self.variables.pack()
        self.program = program
        self.program.connect("token_changed", self.on_token_changed)
        self.program.connect("activeStep_changed", self.update)
        self.program.connect("current_changed", self.on_currentChanged)
        self.idle_handle = None

    def on_stepChanged(self, *args):
        if self.idle_handle is not None:
            self.after_cancel(self.idle_handle)
        self.idle_handle = self.after(0, self.on_token_changed)

    def get_current_token(self, namespace):
        line, pos = self.program.current
        if line is None:
            return None
        try:
            parsed = self.program.source[line-1].parsed
        except IndexError:
            return None
        if parsed is None:
            return None
        token = parsed.get_token_at_pos(pos)
        try:
            node = token.get_node(namespace) if token else None
        except KeyError:
            # Node cannot be resolved in the namespace.
            # (Case where token name is in a function body
            #   but namespace is not corresponding to the function.)
            node = None
        return node

    def on_currentChanged(self):
        state = self.program.steps[self.program.displayedStep].state
        if not self.program.to_many_step():
            self.canvas.delete('helpers')
            token = self.get_current_token(state.namespace)
            for shape in state.shapes:
                if token in shape.depend():
                    try:
                        self.canvas.tkraise(shape.shapeid, 'helpers')
                    except tkinter.TclError:
                        pass
                    shape.draw_helper(token, self.canvas)
        else:
            self.canvas.delete('all')

    def on_token_changed(self):
        state = self.program.steps[self.program.displayedStep].state
        if not self.program.to_many_step():
            self.canvas.delete('helpers')
            token = self.get_current_token(state.namespace)
            for shape in state.shapes:
                shape.update(self.canvas)
                try:
                    self.canvas.tkraise(shape.shapeid, 'helpers')
                except tkinter.TclError:
                    pass
                if token in shape.depend():
                    shape.draw_helper(token, self.canvas)
        else:
            self.canvas.delete('all')
        self.update_hiddenstate(state)
        self.update_namespace(state)

    def place(self):
        self.pack(side="right")

    def update(self, *args):
        state = self.program.steps[self.program.displayedStep].state
        self.idle_handle = None
        self.canvas.delete('all')
        if not self.program.to_many_step():
            token = self.get_current_token(state.namespace)
            for shape in state.shapes:
                shape.draw(self.canvas)
                if token in shape.depend():
                    shape.draw_helper(token, self.canvas)
        self.update_hiddenstate(state)
        self.update_namespace(state)


    def update_hiddenstate(self, state):
        for child in self.canvasState.get_children():
            self.canvasState.delete(child)
        for key in sorted(state.hiddenState.keys()):
            value = state.hiddenState[key]()
            self.canvasState.insert("", "end", key, text=key, value=value, tags=(key,))
            if key == "fillColor":
                self.canvasState.tag_configure("fillColor", background=value, foreground=state.hiddenState[key].opositColor)


    def update_namespace(self, state):
        for child in self.variables.get_children():
            self.variables.delete(child)
        for key in sorted(state.namespace.keys()):
            value = state.namespace[key].get()
            if value is None:
                value = ""
            else:
                value = value()
            self.variables.insert("", "end", key, text=key, value=value, tags=(key,))

