#/usr/bin/python

class Replace(Toplevel):
    
    def __init__(self, parent):
        
        Toplevel.__init__(self, parent)
        
        self.transient(parent)
        
        self.title('Replace')
        
        self.parent = parent
        
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        
        self.buttonbox()
        
        self.grab_set()
        
        if not self.initial_focus:
            self.initial_focus = self
            
        self.protocol('WM_WINDOW_DELETE', self.cancel)
        
        self.geometry('+%d+%d' % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.initial_focus.focus_set()
        
        self.wait_window(self)
        
    def body(self, master):
        
        ###Create substitution replace options title
        self.frame = LabelFrame(master, text='Strip Which Characters?', width=20, relief=RIDGE)
        self.frame.pack()
    
        ###Create remove self.spaces checkbox
        self.spaces = IntVar()
        self.space = Checkbutton(self.frame, text='Spaces', variable=self.spaces)
        self.space.bind('<Button-1>', self.replacespace) 
        self.space.grid(row=0, column=0, sticky=W)
        
        ###Create remove End Of Line checkbox
        self.eol = IntVar()
        self.endofline = Checkbutton(self.frame, text='LF', variable=self.eol)
        self.endofline.bind('<Button-1>', self.replaceeol)
        self.endofline.grid(row=1, column=1, sticky=W)
        
        ###Create remove punctuation checkbox
        self.punct = IntVar()
        self.punctuation = Checkbutton(self.frame, text='.?!$)', variable=self.punct)
        self.punctuation.bind('<Button-1>', self.replacepunct)
        self.punctuation.grid(row=0, column=1, sticky=W)
    
        ###Create remove numbers checkbox
        self.num = IntVar()
        self.numbers = Checkbutton(self.frame, text='Numbers', variable=self.num)
        self.numbers.bind('<Button-1>', self.replacenum)
        self.numbers.grid(row=1, column=0, sticky=W)
    
        ###Create remove tabs checkbox
        self.tab = IntVar()
        self.tabs = Checkbutton(self.frame, text='Tabs', variable=self.tab)
        self.tabs.bind('<Button-1>', self.replacetabs)
        self.tabs.grid(row=2, column=0, sticky=W)
    
        ###Create remove cr checkbox
        self.cr = IntVar()
        self.carriage = Checkbutton(self.frame, text='CR', variable=self.cr)
        self.carriage.bind('<Button-1>', self.replacecr)
        self.carriage.grid(row=2, column=1, sticky=W)
        
    def buttonbox(self):
        
        box = Frame(self)
        
        ###Create clear options button
        self.clear = Button(self.frame, text='Clear', width=17)
        self.clear.bind('<Button-1>', self.optionclear)
        self.clear.grid(row=5, column=0, columnspan=2)
    
        ###Create done button
        self.done = Button(self.frame, text='Done', width=17, command=self.destroy)
        self.done.bind('<Button-1>', self.replacedone)
        self.done.grid(row=6, column=0, columnspan=2)
        
        box.pack()
        
    def cancel(self, event=None):
        global working_text
        global change_text
        
        change_text = working_text
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, working_text)
    
    ###Create clear options function
    def optionclear(self, event):
        global working_text
        global change_text
        
        change_text = working_text
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, working_text)
                
        for i in self.frame.winfo_children():
            i.config(state=NORMAL)
            i.deselect()
            
        collectstats()
        
    ###Create replace options done function
    def replacedone(self, event):
        global working_text
        
        working_text = change_text
        working_text_box.delete(1.0, END)
        working_text_box.insert(END, working_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, working_text)
        
        collectstats()
        
    ###Remove spaces
    def replacespace(self, event):
        global working_text
        global change_text
        
        change_text = change_text.replace(' ', '')
        event.widget.config(state=DISABLED)
                
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        collectstats()
    
    ###Remove End Of Line Character    
    def replaceeol(self, event):
        global working_text
        global change_text
    
        change_text = change_text.replace('\n', '')
        event.widget.config(state=DISABLED)
        
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        collectstats()    
            
    ###Remove Punctuation
    def replacepunct(self, event):
        global working_text
        global change_text
        
        for s in string.punctuation:
            change_text = change_text.replace(s, '')
            
        event.widget.config(state=DISABLED)
        
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        collectstats()
    
    ###Remove Numbers
    def replacenum(self, event):
        global working_text
        global change_text
        
        for d in string.digits:
            change_text = change_text.replace(d, '')
            
        event.widget.config(state=DISABLED)
            
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        collectstats()    
            
    ###Remove Tabs
    def replacetabs(self, event):
        global working_text
        global change_text
        
        change_text = change_text.replace('\t', '   ')
        event.widget.config(state=DISABLED)    
            
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        collectstats()
    
    ###Remove End Of Line Character    
    def replacecr(self, event):
        global working_text
        global change_text
        
        change_text = change_text.replace('\r', '')
        event.widget.config(state=DISABLED)
            
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        
        collectstats()