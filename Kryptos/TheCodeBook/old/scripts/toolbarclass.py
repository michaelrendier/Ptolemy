#/usr/bin/python

class Toolbar(Frame):
    
    def __init__(self, master):
    
        ###Create self.frame frame
        self.frame = Frame(master, bd=2, relief=RIDGE)
        self.frame.pack(side=TOP, fill=X)

        ###Create start button
        self.start = Button(self.frame, text='Start', width=5, command=self.startwork)
        self.start.pack(side=LEFT, padx=2, pady=2)

        ###Create stop button
        self.stop = Button(self.frame, text='Stop', width=5, state=DISABLED, command=self.stopwork)
        self.stop.pack(side=LEFT, padx=2, pady=2)

        ###Create update text button
        self.update = Button(self.frame, text='Update', width=5, state=DISABLED, command=self.updatetext)
        self.update.pack(side=LEFT, padx=2, pady=2)

        ###Create replace frame
        self.replace = Frame(self.frame, bd=2, relief=RIDGE)
        self.replace.pack(side=LEFT, padx=2, pady=2)

        ###Create replace button
        self.replacepng = Image.open('images/replace.png')
        self.replaceimg = ImageTk.PhotoImage(self.replacepng)

        self.strip = Button(self.replace, image=self.replaceimg, width=25, height=25, command=self.raisereplace)
        self.strip.pack(side=LEFT)
        
        ###Create self.transposition Frame
        self.trans = Frame(self.frame, bd=2, relief=RIDGE)
        self.trans.pack(side=LEFT, padx=2, pady=2)

        ###Create railfence button
        self.railpng = Image.open('images/railfence.png')
        self.railimg = ImageTk.PhotoImage(self.railpng)

        self.railfence = Button(self.trans, image=self.railimg, width=25, height=25, command=self.passnull)####
        self.railfence.pack(side=LEFT)
        
        ###Creat   e scytale button
        self.scypng = Image.open('images/scytale.png')
        self.scyimg = ImageTk.PhotoImage(self.scypng)

        self.scytale = Button(self.trans, image=self.scyimg, width=25, height=25, command=self.passnull)####
        self.scytale.pack(side=LEFT)

        ###Create substitution frame
        self.substitute = Frame(self.frame, bd=2, relief=RIDGE)
        self.substitute.pack(side=LEFT, padx=2, pady=2)

        ###Create caesar cipher button
        self.caesarpng = Image.open('images/caesar.png')
        self.caesarimg = ImageTk.PhotoImage(self.caesarpng)

        self.caesar = Button(self.substitute, image=self.caesarimg, width=25, height=25, command=self.raisecaesar)
        self.caesar.pack(side=LEFT)

        ###Create pigpen (fonts) button
        self.pigpng = Image.open('images/pigpen.png')
        self.pigimg = ImageTk.PhotoImage(self.pigpng)

        self.pigpen = Button(self.substitute, image=self.pigimg, width=25, height=25, command=self.passnull)####
        self.pigpen.pack(side=LEFT)

        ###Create Scrabble Button
        self.monopng = Image.open('images/monoalpha.png')
        self.monoimg = ImageTk.PhotoImage(self.monopng)

        self.scrabble = Button(self.substitute, image=self.monoimg, width=25, height=25, command=self.raisescrabble)
        self.scrabble.pack(side=LEFT)

        ###Create self.advanced Ciphers Frame
        self.advanced = Frame(self.frame, bd=2, relief=RIDGE)
        self.advanced.pack(side=LEFT, padx=2, pady=2)

        ###Create playfair button
        self.playpng = Image.open('images/playfair.png')
        self.playimg = ImageTk.PhotoImage(self.playpng)

        self.playfair = Button(self.advanced, image=self.playimg, width=25, height=25, command=self.passnull)####
        self.playfair.pack(side=LEFT)
        
        ###Create digraph button
        self.digraphpng = Image.open('images/digraph.png')
        self.digraphimg = ImageTk.PhotoImage(self.digraphpng)
        
        self.digraph = Button(self.advanced, image=self.digraphimg, width=25, height=25, command=self.passnull)####
        self.digraph.pack(side=LEFT)
        
        ###Create homophonic button
        self.homopng = Image.open('images/homophonic.png')
        self.homoimg = ImageTk.PhotoImage(self.homopng)
        
        self.homophonic = Button(self.advanced, image=self.homoimg, width=25, height=25, command=self.passnull)####
        self.homophonic.pack(side=LEFT)
        
        ###Create vigener button
        self.vigenerpng = Image.open('images/vigener.png')
        self.vigenerimg = ImageTk.PhotoImage(self.vigenerpng)
        
        self.vigener = Button(self.advanced, image=self.vigenerimg, width=25, height=25, command=self.passnull)####
        self.vigener.pack(side=LEFT)
        
        ###Create enigma button
        self.enigmapng = Image.open('images/enigma.png')
        self.enigmaimg = ImageTk.PhotoImage(self.enigmapng)
        
        self.enigma = Button(self.advanced, image=self.enigmaimg, width=25, height=25, command=self.passnull)####
        self.enigma.pack(side=LEFT)
        
        ###Create Statistical Analysis frame
        self.stats = Frame(self.frame, bd=2, relief=RIDGE)
        self.stats.pack(side=LEFT, padx=2, pady=2)
        
        ###Create frequency analysis button
        self.freqletpng = Image.open('images/freqletters.png')
        self.freqletimg = ImageTk.PhotoImage(self.freqletpng)
        
        self.freqlet = Button(self.stats, image=self.freqletimg, width=25, height=25, command=self.passnull)####
        self.freqlet.pack(side=LEFT)
        
        ###Create frequency double letters button
        self.freqdoupng = Image.open('images/freqdouble.png')
        self.freqdouimg = ImageTk.PhotoImage(self.freqdoupng)
        
        self.freqdouble = Button(self.stats, image=self.freqdouimg, width=25, height=25, command=self.passnull)####
        self.freqdouble.pack(side=LEFT)
        
        ###Create vowel trowel button
        self.vowelpng = Image.open('images/voweltrowel.png')
        self.vowelimg = ImageTk.PhotoImage(self.vowelpng)
        
        self.voweltrowel = Button(self.stats, image=self.vowelimg, width=25, height=25, command=self.passnull)####
        self.voweltrowel.pack(side=LEFT)
        
    #Create startwork function
    def startwork(self):
        global original_text
        global working_text
        global change_text
    
        ###Create Original, Working, Change Text
        original_text = working_text_box.get(1.0, END)
        working_text = working_text_box.get(1.0, END)
        change_text = working_text
    
        ###Change Main Text
        working_text_box.delete(1.0, END)
        working_text_box.insert(END, working_text)
    
        ###Change change text
        change_text_box.delete(1.0, END)
        change_text_box.insert(END, change_text)
    
        self.start.config(state=DISABLED)
        self.stop.config(state=NORMAL)
    
    #Create stopwork function
    def stopwork(self):
        global original_text
    
        if tkMessageBox.askokcancel('Revert To Original Text?', 'You will loose any changes...'):
            change_text_box.delete(1.0, END)
            working_text_box.delete(1.0, END)
            working_text_box.insert(END, original_text)
            self.start.config(state=NORMAL)
            self.stop.config(state=DISABLED)    

    #Create update text function
    def updatetext(self):
        global workign_text
        global change_text
    
        working_text = change_text
        working_text_box.delete(1.0, END)
        working_text_box.insert(1.0, working_text)
        change_text_box.delete(1.0, END)
        change_text_box.insert(1.0, working_text)
        change_text = ''
        self.update.config(state=DISABLED)
    
        collectstats()

    #Create passnull function (for toolbar buttons)
    def passnull(self):
        pass
    
    def raisescrabble(self):
        scrabbletop = Scrabble(root)
    
    def raisecaesar(self):
        caesartop = Caesar(root)
    
    def raisereplace(self):
        replacetop = Replace(root)