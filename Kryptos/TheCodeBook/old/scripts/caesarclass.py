#/usr/bin/python

class Caesar(Toplevel):
    
    def __init__(self, parent):
        
        self.let = []
        self.letindex = []
        self.chgindex = []
        self.chglet = []
    
        Toplevel.__init__(self, parent)
        self.transient(parent)
        
        self.title('Caesar Shift')
        
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
        global mono_font
        ###Create slider frame
        self.slider = Frame(master, width=300, bd=2, relief=RIDGE)
        self.slider.bind('<Button-4>', self.scaleforward)
        self.slider.bind('<Button-5>', self.scaleback)
        self.slider.pack(side=LEFT, fill=Y)

        ###Create caesar shift title
        self.label = Label(self.slider, text='Caesar Shift', width=26, relief=RAISED)
        self.label.grid(row=0, column=0)

        ###Create caesar spacer label
        self.spacer = Label(self.slider, text='Original = Red : Encoded = Blue ', width=26)
        self.spacer.grid(row=1, column=0)

        ###Create ceaser scale
        self.scale = Scale(self.slider, from_=0, to=25, orient=HORIZONTAL, tickinterval=13, length=210, command=self.caesarshift)
        self.scale.bind('<Button-4>', self.scaleforward)
        self.scale.bind('<Button-5>', self.scaleback)
        self.scale.grid(row=2, column=0)

        ###Create alphabetical 'original' letter label
        self.letters = Label(self.slider, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=mono_font, fg='blue', width=26)
        self.letters.bind('<Button-4>', self.scaleforward)
        self.letters.bind('<Button-5>', self.scaleback)
        self.letters.grid(row=3, column=0)

        ###Create caesar shifted 'encoded' letter label
        self.newletters = Label(self.slider, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=mono_font, fg='red', width=26)
        self.newletters.bind('<Button-4>',self.scaleforward)
        self.newletters.bind('<Button-5>', self.scaleback)
        self.newletters.grid(row=4, column=0)
        
    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, event=None):
        global working_text
        global change_text
        
        working_text = change_text
        working_text_box.delete(1.0, END)
        working_text_box.insert(1.0, working_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(1.0, working_text)
        change_text = ''
        
        collectstats()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        global working_text
        global change_text
        
        change_text = working_text
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, working_text)
        
        collectstats()
        
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    
    def caesarshift(self, event):
        global working_text
        global change_text

        change_text = working_text
        
        self.let = []
        self.letindex = []
        self.chgindex = []
        self.chglet = []
        
        ###Create initial list of letters
        for c in string.uppercase:
            self.let.append(c)
        
        ###Create list of initial letters indexes
        for c in self.let:
            self.letindex.append(self.let.index(c))
        
        ###Encode initial letter indexes    
        for c in self.letindex:
            try:
                self.chgindex.append(self.letindex.index(c) - self.scale.get())
        
            except ValueError:
                self.chgindex.append(self.letindex[0])
        
        ###Create list of encoded letters
        for c in self.chgindex:
            try:
                self.chglet.append(self.let[c])
            
            except IndexError:
                self.chglet.append(self.let[c-26])
        
        ###Update caesar shift encoded label        
        self.newletters.config(text='')
        self.newletters.config(text=''.join(self.chglet))
        
        ###Replace text according to upper/lower/alphanumeric
        caesar_text = ''
        for c in change_text:
        
            ###Replace uppercase with encoded uppercase                
            if str.isupper(str(c)):
                i = self.let.index(c)
                caesar_text = caesar_text + str(self.chglet[i])
        
            ###Replace lowercase with encoded lowercase                
            if str.islower(str(c)):
                i = self.let.index(string.upper(c))
                caesar_text = caesar_text + string.lower(self.chglet[i])
        
            ###Replace digits with self                            
            if str.isdigit(str(c)):
                caesar_text = caesar_text + c
        
            ###Replace any non-alphanumeric character with self                
            if not str.isalnum(str(c)):
                caesar_text = caesar_text + c
    
        ###Update text    
        change_text = caesar_text    
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        self.update_idletasks()
        
        collectstats()

    ###Create scaleforward event function
    def scaleforward(self, event):
        self.scale.set(self.scale.get() + 1)

    ###Create scaleback event function
    def scaleback(self, event):
        self.scale.set(self.scale.get() - 1)