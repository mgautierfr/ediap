
import tkinter
import tkinter.ttk

class ActiveStateShower(tkinter.Frame):
    def __init__(self, parent, program, contextShower):
        tkinter.Frame.__init__(self, parent, width=100)
        self.propagate(True)
        self.contextShower = contextShower
        self.contextShower.pack(in_=self)
        self.contextShower.lift()
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
        if self.program.displayedStep is None:
            return
        state = self.program.steps[self.program.displayedStep].state
        if not self.program.to_many_step():
            self.contextShower.delete('helpers')
            token = self.get_current_token(state.namespace)
            self.contextShower.draw(state.context, token, shape_=None)
        else:
            self.contextShower.delete('all')

    def on_token_changed(self):
        if self.program.displayedStep is None:
            return
        state = self.program.steps[self.program.displayedStep].state
        if not self.program.to_many_step():
            self.contextShower.delete('helpers')
            token = self.get_current_token(state.namespace)
            self.contextShower.draw(state.context, token, shape_=False)
        else:
            self.contextShower.delete('all')
        self.contextShower.update_hiddenstate(state.context)
        self.update_namespace(state)

    def update(self, *args):
        if self.program.displayedStep is None:
            return
        state = self.program.steps[self.program.displayedStep].state
        self.idle_handle = None
        self.contextShower.delete('all')
        if not self.program.to_many_step():
            token = self.get_current_token(state.namespace)
            self.contextShower.draw(state.context, token, shape_=True)
        self.contextShower.update_hiddenstate(state.context)
        self.update_namespace(state)

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

