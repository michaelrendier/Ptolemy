class Playfair(Toplevel):
    
    def __init__(self, parent):
        
        Toplevel.__init__(self, parent)
        
        self.transient(parent)
        
        self.title('Playfair Cipher')
        
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
        
        self.entry.focus_set()
        
        self.wait_window(self)
        
    def body(self, master):
        
        self.keyframe = LabelFrame(master, text='Enter Key Here:', bd=2, relief=RIDGE)
        self.keyframe.pack()
        
        self.key = StringVar()
        self.entry = Entry(self.keyframe, textvariable=self.key, width=26)
        self.entry.bind('<KeyRelease>', self.validate)
        self.entry.bind('<BackSpace>', self.entryclear)
        self.entry.pack()
        
        self.keybutton = Button(self.keyframe, text='Use Key', command=self.usekey)
        self.keybutton.pack()
        
        self.squareframe = LabelFrame(master, text='Playfair Square', bd=2, relief=RIDGE)
        self.squareframe.pack()
        
        for i in range(25):
            self.i = Label(self.squareframe, width=2, justify=CENTER, text=i, relief=RAISED)
            
            if i <= 4:
                self.i.grid(row=0, column=i)
            
            if i >= 5 and i <= 9:
                self.i.grid(row=1, column=i - 5)
                
            if i >= 10 and i <= 14:
                self.i.grid(row=2, column=i - 10)
                
            if i >= 15 and i <= 19:
                self.i.grid(row=3, column=i - 15)
            
            if i >= 20 and i <= 24:
                self.i.grid(row=4, column=i - 20)
    
    def buttonbox(self):
        
        box = Frame(self)

        w = Button(box, text='Encode', command=self.encode)
        w.grid(row=0, column=0, padx=5, pady=5)
        w = Button(box, text='Decode', command=self.decode)
        w.grid(row=0, column=1, padx=5, pady=5)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.grid(row=1, column=0, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.grid(row=1, column=1, padx=5, pady=5)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        
        box.pack()

    def entryclear(self, event):
        self.key.set('')
    
    def validate(self, event):
        if event.char.upper() not in string.uppercase:
            self.key.set(self.key.get()[0:-1])
        
    def encode(self):
        global change_text
        
        self.encode_text = []
        
        for i in self.digraph_text:
            self.first = i[0]
            self.second = i[1]
            
            if self.first == 'J':
                self.first = 'I'
                
            if self.second == 'J':
                self.second = 'I'
                
            x1, y1 = matrixindex(self.first, self.matrix)
            x2, y2 = matrixindex(self.second, self.matrix)
            
            #same row increase y
            if x1 == x2 and y1 != y2:
                x3 = x1
                y3 = y1 + 1
                x4 = x2
                y4 = y2 + 1
                
                if y3 > 4:
                    y3 = 0
                if y4 > 4:
                    y4 = 0
            
            #same column increase x
            elif x1 != x2 and y1 == y2:
                x3 = x1 + 1
                y3 = y1
                x4 = x2 + 1
                y4 = y2
                
                if x3 > 4:
                    x3 = 0
                if x4 > 4:
                    x4 = 0
                
            #double letters increase y
            elif x1 == x2 and y1 == y2:
                x3 = x1
                y3 = y1 + 1
                x4 = x2
                y4 = y2 + 1
                
                if y3 > 4:
                    y3 = 0
                if y4 > 4:
                    y4 = 0
                
            #corners switch y
            elif x1 != x2 and y1 != y2:
                x3 = x1
                y3 = y2
                x4 = x2
                y4 = y1
                                
            self.encode_text.append(self.matrix[x3][y3] + self.matrix[x4][y4])
        
        self.digraph_text = self.encode_text
        change_text = ' '.join(self.encode_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
    
    def decode(self):
        global change_text
        
        self.decode_text = []
        
        for i in self.digraph_text:
            self.first = i[0]
            self.second = i[1]
            
            if self.first == 'J':
                self.first = 'I'
                
            if self.second == 'J':
                self.second = 'I'
                
            x1, y1 = matrixindex(self.first, self.matrix)
            x2, y2 = matrixindex(self.second, self.matrix)
                                        
            #same row decrease y
            if x1 == x2 and y1 != y2:
                x3 = x1
                y3 = y1 - 1
                x4 = x2
                y4 = y2 - 1
                
                if y3 < 0:
                    y3 = 4
                if y4 < 0:
                    y4 = 4
            
            #same column decrease x
            elif x1 != x2 and y1 == y2:
                x3 = x1 - 1
                y3 = y1
                x4 = x2 - 1
                y4 = y2
                
                if x3 < 0:
                    x3 = 4
                if x4 < 0:
                    x4 = 4
                
            #double letters decrease y
            elif x1 == x2 and y1 == y2:
                x3 = x1
                y3 = y1 - 1
                x4 = x2
                y4 = y2 - 1
                
                if y3 < 0:
                    y3 = 4
                if y4 < 0:
                    y4 = 4
                
            #corners switch y
            elif x1 != x2 and y1 != y2:
                x3 = x1
                y3 = y2
                x4 = x2
                y4 = y1
                                
            self.decode_text.append(self.matrix[x3][y3] + self.matrix[x4][y4])
        
        self.digraph_text = self.decode_text
        change_text = ' '.join(self.decode_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
    
    def ok(self, event=None):
        global working_text
        global change_text
        
        change_text = ''.join(self.digraph_text)
        working_text = change_text
        working_text_box.delete(1.0, END)
        working_text_box.insert(END, working_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
    
        self.parent.focus_set()
        self.destroy()
        
        collectstats()
        
    def cancel(self, event=None):
        global working_text
        global change_text
        
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, working_text)
                
        self.parent.focus_set()
        self.destroy()
        
        collectstats()
        
    def usekey(self):
        global working_text
        global change_text
        
        self.dic = {}
        self.square = []
        self.copy = []
        
        for i in string.uppercase:
            
            if i == 'J':
                pass
            
            else:
                self.square.append(i)
                self.copy.append(i)
                
        for i in string.upper(self.key.get()):
            try:
                self.dic[i] += 1
                
            except KeyError:
                self.dic[i] = 1
                
        for i in sorted(self.dic):
            try:
                self.square.remove(i)
                self.square.insert(sorted(self.dic).index(i), i)
                self.copy.remove(i)
                self.copy.insert(sorted(self.dic).index(i), i)
                
            except ValueError:
                pass
                
        for i in self.squareframe.winfo_children():
            i.config(text=self.copy.pop(0))
                
        self.matrix = [ self.square[i*5: (i+1)*5] for i in range(5) ]
        
        self.digraph_text = [change_text[i:i+2] for i in range(0, len(change_text), 2)]
        self.digraph_text = [i.upper() for i in self.digraph_text]
        
        if len(self.digraph_text[-1]) == 1:
            self.digraph_text[-1] += 'X'
        
        change_text = ' '.join(self.digraph_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
        