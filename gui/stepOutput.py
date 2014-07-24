
import tkinter

class StepOutput(tkinter.Frame):
    def __init__(self, parent, text):
        tkinter.Frame.__init__(self, parent)
        self.hScrollbar = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
        self.hScrollbar.grid(column=0,
                             row=1,
                             sticky="nsew"
                            )
        self.vScrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        self.vScrollbar.grid(column=1,
                             row=0,
                             sticky="nsew")
        self.steps = tkinter.Canvas(self, bg="white")
        self.steps.grid(column=0,
                        row=0,
                        sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.vScrollbar['command'] = self.steps.yview
        self.hScrollbar['command'] = self.steps.xview
        self.steps['yscrollcommand'] = self.vScrollbar.set
        self.steps['xscrollcommand'] = self.hScrollbar.set
        self.helpers = (None, None)
        self.text = text

    def place(self):
        self.pack(fill="both", expand=1, side="right")

    def update(self):
        self.steps.delete('all')
        for nb, state in enumerate(self.interpretor.states):
            pos = self.text.bbox("%d.0"%(state.lineno))
            if pos:
                self.steps.create_oval(pos[3]*nb, pos[1], pos[3]*(nb+1), pos[1]+pos[3], fill="black")
            print(state)
        width = max(self.steps.bbox('all')[2], self.steps.winfo_width()-10)
        for lineno ,line in self.interpretor.source:
            pos = self.text.bbox("%d.0"%(lineno))
            if pos:
                self.steps.create_line(0, pos[1]+pos[3], width, pos[1]+pos[3])
        self.steps['scrollregion'] = self.steps.bbox('all')
            #pass
            #print (nb, state.lineno)

