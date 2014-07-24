
import tkinter

class TextInput(tkinter.Text):
    def __init__(self, parent, helpv):
        tkinter.Text.__init__(self, parent)
        self.bind("<Button1-Motion>", self.on_motion)
        self.bind("<Button1-ButtonRelease>", self.on_release)
        font = tkinter.font.Font(font=self['font'])
        font.configure(weight='bold')
        self.tag_configure("keyword", foreground="darkgreen", font=font)
        self.tag_configure("invalidSyntax", background="#FFBBBB")
        self.target = None
        self.helpv = helpv

    def place(self):
        self.pack(side="left", fill="y", expand=0)

    def on_motion(self, event):
        if self.target is None:
            return "break"
        return self.target(event)
    
    def on_release(self, event):
        self.target = None
        self.edit_modified(True)

    def get_source(self):
        return list(enumerate(self.get("1.0", "end").split("\n"), 1))

    def clean_tags(self):
        [self.tag_remove(n, "1.0", "end") for n in self.tag_names()]

