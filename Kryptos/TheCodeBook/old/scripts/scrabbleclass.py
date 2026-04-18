#/usr/bin/python

class Scrabble(Toplevel):	
	
	def __init__(self, parent):
		
		self.ctlist = []
		self.ttlist = []
		self.matrix = [[],[]]
		self.text = []
		self.label = []
		
		Toplevel.__init__(self, parent)
		self.transient(parent)
		
		self.title('Scrabble')
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
			
		###Create scrabble letters frame
		self.letters_frame = LabelFrame(master, text='Scrabble Tiles', bd=2, relief=RIDGE)
		self.letters_frame.pack()
		
		###Create old scrabble tiles w/itterated radiobuttons
		self.change_this = LabelFrame(self.letters_frame, text='Change this:',  bd=2, relief=RIDGE)
		self.change_this.pack(fill=Y)
		
		self.ln1 = []
		self.ct = IntVar()
		
		for l in range(0, 26):
			self.ln1.append('radioct' + str(l))
			
		for i in range(0, 26):	
				
			self.ln1[i] = Radiobutton(self.change_this, state=DISABLED, command=self.ctevent, text=string.uppercase[i], width=1, bd=2, fg='blue', variable=self.ct, value=i, indicatoron=0)
			
			if i <= 12:
				self.ln1[i].grid(row=0, column=i)
				self.ln1[i].deselect()
					
			if i >= 13:
				self.ln1[i].grid(row=1, column=i - 13)
				self.ln1[i].deselect()
				
		###Create new scrabble tiles w/itterated radiobuttons
		self.to_this = LabelFrame(self.letters_frame, text='To this:', bd=2, relief=RIDGE)
		self.to_this.pack()
				
		self.ln2 = []
		self.tt = IntVar()
			
		for l in range(0, 26):
			self.ln2.append('radiott' + str(l))
					
		for i in range(0, 26):	
			self.ln2[i] = Radiobutton(self.to_this, state=DISABLED, command=self.ttevent, text=string.uppercase[i], width=1, bd=2, fg='red', variable=self.tt, value=i, indicatoron=0)
			
			if i <= 12:
				self.ln2[i].grid(row=0, column=i)
				self.ln2[i].deselect()
			
			if i >= 13:
				self.ln2[i].grid(row=1, column=i - 13)
				self.ln2[i].deselect()
			
		###Create old scrabble list
		self.old = Label(self.letters_frame, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=mono_font, fg='blue', width=26)
		self.old.pack()
	
		###Create new scrabble list
		self.new = Label(self.letters_frame, text='', font=mono_font, fg='red', width=26)
		self.new.pack()
		
		###Create old scrabble tool frame
		self.analysis = LabelFrame(master, text='English Frequency Analysis', width=240, bd=2, relief=RIDGE)
		self.analysis.pack()
	
		###Create scrabble english freq analysis Title
		self.freq = Label(self.analysis, text='Click letters to use:', relief=RAISED, width=26)
		self.freq.pack()
	
		###Create scrabble working text frequency list	
		self.freq_old = Label(self.analysis, text='', font=mono_font, fg='blue')
		self.freq_old.bind('<Button-1>', self.scrabblefreq)
		self.freq_old.pack()
	
		if len(wtpf) < 26 or len(wtpf) > 26:
			self.freq_old.config(text='< 26 Characters')
		
		if len(wtpf) > 26:
			self.freq_old.config(text='> 26 Characters')
	
		if len(wtpf) == 26:
			self.freq_old.config(text=''.join(wtpf).upper())
	
		###Create scrabble change text frequency list
		self.freq_new = Label(self.analysis, text=''.join(epf), font=mono_font, fg='red')
		self.freq_new.bind('<Button-1>', self.scrabblefreq)
		self.freq_new.pack()
	
	# add standard button box. override if you don't want the
	def buttonbox(self):
		box = Frame(self)

		###Create scrabble start button
		self.start = Button(box, text='Click to Start', width=23, command=self.startscrabble)
		self.start.pack()
		
		###Create scrabble stop button
	
		###Create scrabble clear changes button
		self.clear = Button(box, text='Clear Changes', state=DISABLED, width=23, command=self.scrabbleclear)
		self.clear.pack()
	
		###Create scrabble commit changes button
		self.done = Button(box, text='Commit Changes', width=23, command=self.destroy)
		self.done.bind('<Button-1>', self.scrabbledone)
		self.done.pack()

		box.pack()
		
		collectstats()
	
	def cancel(self):
		global working_text
		
		change_text_box.delete(1.0, END)
		change_text_box.insert(END, working_text)
		
		collectstats()
		
		self.parent.focus_set()
		self.destroy()
		
	###Create commit changes button event
	def scrabbledone(self, event):
		global working_text
		global change_text
				
		change_text = ''.join(self.text)
		working_text = change_text
		working_text_box.delete(1.0, END)
		working_text_box.insert(END, working_text)
	
		collectstats()
		
		self.parent.focus_set()
		self.destroy()
		
	###Create scrabble Letter Frequency Order <Button-1> event	
	def scrabblefreq(self, event):
		global epf
		global wtpf
		global working_text
		global change_text
		
		change_text = ''
		
		###Replace text according to upper/lower/alphanumeric
		for c in working_text:
		
			###Replace uppercase with encoded uppercase				
			if str.isupper(str(c)):
				i = wtpf.index(c)
				change_text = change_text + str(epf[i])
			
			###Replace lowercase with encoded lowercase				
			if str.islower(str(c)):
				i = wtpf.index(string.upper(c))
				try:				
					change_text = change_text + string.lower(epf[i])
				except IndexError:
					pass
									
			###Replace digits with self							
			if str.isdigit(str(c)):
				change_text = change_text + c
			
			###Replace any non-alphanumeric character with self				
			if not str.isalnum(str(c)):
				change_text = change_text + c
		
		###Update text
		change_text_box.delete(1.0, END)
		change_text_box.insert(END, change_text)
		update_text.config(state=NORMAL)
		
		collectstats()

	###clicking on start button
	def startscrabble(self):
		
		global working_text
		global change_text
				
		for i in self.change_this.winfo_children():
			i.config(state=NORMAL)
			i.deselect()
			
		self.matrix = [[],[]]
		self.ctlist = []
		self.ttlist = []
		self.text = []
		self.label = []
		
		for i in change_text:
			self.text.append('.')
			
		for i in string.uppercase:
			self.ctlist.append(i)
			self.ttlist.append(i)		
		
		self.new.config(text='.' * 26)
		for i in string.uppercase:
			self.label.append('.')
		
		self.start.config(state=DISABLED)
		self.clear.config(state=NORMAL)
		change_text_box.delete(1.0, END)
		change_text_box.insert(END, ''.join(self.text))
		
	###clicking on 'change this' tiles
	def ctevent(self):
		
		try:
			l = string.uppercase[self.ct.get()]
			self.ctlist.remove(l)
			self.matrix[0].extend([l])					
							
			for i in self.change_this.winfo_children():
				i.config(state=DISABLED)
				i.deselect()
				
			for i in self.to_this.winfo_children():
				i.config(state=NORMAL)
				i.deselect()
				
		except ValueError:
			if tkMessageBox.showinfo('Used Letter', 'Letter Already Used'):
				pass
	
	###clicking on 'to this' tiles	
	def ttevent(self):
		global working_text
		global change_text
				
		try:
			###create 
			l = string.uppercase[self.tt.get()]
			self.ttlist.remove(l)
			self.matrix[1].extend([l])
							
			for i in self.change_this.winfo_children():
				i.config(state=NORMAL)					
				i.deselect()
				
			for i in self.to_this.winfo_children():
				i.config(state=DISABLED)
				i.deselect()	
			
			###Change scrabble_new label
			ol = string.uppercase.index(self.matrix[0][-1])
			self.label[ol] = self.matrix[1][-1]
			self.new.config(text=''.join(self.label))
				
			###updatr change text
			for c in range(0, len(change_text)):
				
				if str.isupper(str(change_text[c])):
					
					if change_text[c] == self.matrix[0][-1]:
						self.text[c] = self.matrix[1][-1]
						
				if str.islower(str(change_text[c])):
					
					if str.upper(str(change_text[c])) == self.matrix[0][-1]:
						self.text[c] = str.lower(self.matrix[1][-1])
				
			change_text_box.delete(1.0, END)
			change_text_box.insert(END, ''.join(self.text))
			
		except ValueError:
			if tkMessageBox.showinfo('Used Letter', 'Letter Already Used'):
				pass		
			
	###clear changes button event
	def scrabbleclear(self):
		global working_text
		
		clrct = self.change_this.winfo_children()
		for i in clrct:
			if clrct.index(i) <= 12:
				i.grid(row=0, column=clrct.index(i))
				i.deselect()
			if clrct.index(i) >= 13:
				i.grid(row=1, column=clrct.index(i) - 13)
				i.deselect()
		
		clrtt = self.to_this.winfo_children()
		for i in clrtt:
			if clrtt.index(i) <= 12:
				i.grid(row=0, column=clrtt.index(i))
				i.deselect()
			if clrtt.index(i) >= 13:
				i.grid(row=1, column=clrtt.index(i) - 13)
				i.deselect()
				
		for i in self.change_this.winfo_children():
			i.config(state=DISABLED)					
			i.deselect()
				
		for i in self.to_this.winfo_children():
			i.config(state=DISABLED)
			i.deselect()
		
		self.start.config(state=NORMAL)
		
		self.clear.config(state=DISABLED)
		
		self.new.config(text='.' * 26)
		
		change_text_box.delete(1.0, END)
		change_text_box.insert(END, working_text)
		
		collectstats()