#/usr/bin/python

class Scytale(Toplevel):
    
    def __init__(self, parent):
        
        Toplevel.__init__(self, parent)
        
        self.transient(parent)
        
        self.title('Scytale')
        
        self.parent = parent
        
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        
        self.buttonbox()
        
        self.grab_set()
        
        if not self.initial_focus:
            self.initial_focus = self
            
        self.protocol('WM_DELETE_WINDOW', self.cancel)
        
        self.geometry('+%d+%d' % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.initial_focus.focus_set()
        
        self.wait_window(self)

    def body(self, master):
        
        self.frame = Frame(master, bd=2, relief=RIDGE)
        self.frame.pack(side=LEFT, fill=Y)

        self.title = Label(self.frame, text='Scytale Transposition', width=21, relief=RAISED)
        self.title.grid(row=0, column=0, columnspan=3)

        self.label = Label(self.frame, text='Letters per wrap', width=21)
        self.label.grid(row=1, column=0, columnspan=3)

        self.pr = IntVar()

        self.radio2 = Radiobutton(self.frame, text='2', variable=self.pr, value=0, command=self.scytaleshift)
        self.radio2.grid(row=3, column=0, sticky=W)

        self.radio3 = Radiobutton(self.frame, text='3', variable=self.pr, value=1, command=self.scytaleshift)
        self.radio3.grid(row=3, column=1, sticky=W)

        self.radio4 = Radiobutton(self.frame, text='4', variable=self.pr, value=2, command=self.scytaleshift)
        self.radio4.grid(row=3, column=2, sticky=W)

        self.radio5 = Radiobutton(self.frame, text='5', variable=self.pr, value=3, command=self.scytaleshift)
        self.radio5.grid(row=4, column=0, sticky=W)

        self.radio6 = Radiobutton(self.frame, text='6', variable=self.pr, value=4, command=self.scytaleshift)
        self.radio6.grid(row=4, column=1, sticky=W)

        self.radio7 = Radiobutton(self.frame, text='7', variable=self.pr, value=5, command=self.scytaleshift)
        self.radio7.grid(row=4, column=2, sticky=W)

        self.radio8 = Radiobutton(self.frame, text='8', variable=self.pr, value=6, command=self.scytaleshift)
        self.radio8.grid(row=5, column=0, sticky=W)

        self.radio9 = Radiobutton(self.frame, text='9', variable=self.pr, value=7, command=self.scytaleshift)
        self.radio9.grid(row=5, column=1, sticky=W)

        self.radio10 = Radiobutton(self.frame, text='10', variable=self.pr, value=8, command=self.scytaleshift)
        self.radio10.grid(row=5, column=2, sticky=W)

    def buttonbox(self):
        
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):
        global working_text
        global change_text
        
        working_text = change_text
        working_text_box.delete(1.0, END)
        working_text_box.insert(END, working_text)
        
        self.parent.focus_set()
        self.destroy()
        
    def cancel(self, event=None):
        global working_text
        global change_text
        
        change_text = working_text
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        self.parent.focus_set()
        self.destroy()
    
    def newmatrix(self, W, H):
        return [ [ [] for i in range(W) ] for j in range(H) ]    
        
    def scytaleshift(self):
        global working_text
        global change_text
    
        change_text = working_text
        self.scytale = []        
        self.matrix = self.newmatrix(15, 1)    
    
        for c in change_text:
            self.scytale.append(c)

        for c in self.scytale:
        
            for s in range(self.pr.get() + 1, -1, -1):
            
                try:
                    self.matrix[0][s].extend([str(self.scytale.pop(s))])
            
                except IndexError:
                    self.matrix[0][s].extend([str(self.scytale.pop())])
                
        change_text_box.delete(1.0, END)
        
        for s in range(0, 15):
            change_text_box.insert(END, ''.join(self.matrix[0][s]))
        
        change_text = change_text_box.get(1.0, END)