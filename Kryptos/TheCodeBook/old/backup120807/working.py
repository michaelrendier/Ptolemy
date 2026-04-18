#/usr/bin/python
from Tkinter import *
import os
import tkMessageBox
import re
import string
import tkFont
import Image, ImageTk

class Pycrypt():#Pycrypt general functions class
	
	def __init__(self):
		#Global Texts
		self.original_text = ''#Original text
		self.working_text = ''#Working Text
		self.change_text = ''#Change Text
		
		#Fonts
		self.mono_font = tkFont.Font(family='Ubuntu Mono')#Mono spacing font
		
		#Pycrypt variables
		self.words = ''#Word count
		self.lines = ''#Line count
		self.double_letter = []#List of double letters
		self.triple_letter = []#List of triple letters
		self.dic1 = {}#Frequecy analysis dictionary
		self.frequency_english = 'AAAAAAAABBCCCDDDDEEEEEEEEEEEEEFFGGHHHHHHIIIIIIIJKLLLLMMNNNNNNNOOOOOOOOPPQRRRRRRSSSSSSTTTTTTTTTUUUVWWXYYZ'#English Letter Frequency****SIMPLIFY TEXT****
		self.dic2 = {}#English frequency analysis dictionary
		self.epf = []#List of english percent letter frequency
		self.wtpf = []#List of working text percent letter frequency
		self.let = [] #list of alphabetical letters
		
		body = Frame(root)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)
		
	def body(self, master):
		
		#Create window frame
		window_frame = Frame(root)
		window_frame.pack(fill=BOTH)
		
		#Create text frame
		text_frame = Frame(window_frame, bd=2, relief=RIDGE)
		text_frame.grid(row=0, column=0)
		
		#Create working text box
		working_frame = LabelFrame(text_frame, text='Working Text', bd=2, relief=RIDGE)
		working_frame.grid(row=0, column=0)
		
		working_scroll = Scrollbar(working_frame)
		working_scroll.grid(row=0, column=1, sticky=N+S)
		
		self.working_text_box = Text(working_frame, yscrollcommand=working_scroll.set, height=17, width=80, insertbackground='white', fg='white', bg='black')
		self.working_text_box.grid(row=0, column=0)
		
		working_scroll.config(command=self.working_text_box.yview)
		
		##Create change text box
		change_frame = LabelFrame(text_frame, text='Change Text', bd=2, relief=RIDGE)
		change_frame.grid(row=1, column=0)
		
		change_scroll = Scrollbar(change_frame)
		change_scroll.grid(row=1, column=1, sticky=N+S)
		
		self.change_text_box = Text(change_frame, yscrollcommand=change_scroll.set, height=17, width=80, insertbackground='white', fg='green', bg='black')
		self.change_text_box.grid(row=1, column=0)
		
		change_scroll.config(command=self.change_text_box.yview)
		
		#Create stats text box
		stats_frame = LabelFrame(text_frame, text='Text Statistics', bd=2, relief=RIDGE)
		stats_frame.grid(row=0, column=1, rowspan=2)
		
		stats_scroll = Scrollbar(stats_frame)
		stats_scroll.grid(row=0, column=3, rowspan=2, sticky=N+S)
		
		self.stats_text_box = Text(stats_frame, yscrollcommand=stats_scroll.set, height=36, width=40, fg='white', bg='black')
		self.stats_text_box.grid(row=0, column=2, rowspan=2)
		
		stats_scroll.config(command=self.stats_text_box.yview)
		
		#Create Status Bar
		status = StatusBar(root)
		status.pack(side=BOTTOM, fill=X)
		
	def matrixindex(self, Term, Matrix):#Search Matrix for Term return index
		for i in range(len(Matrix)):
			try:
				return [i, Matrix[i].index(Term)]
		
			except ValueError:
				pass

	def collectstats(self):#Collectstats function
		
		Pycrypt.stats_text_box.delete(1.0, END)
	
		#Count Number of Characters
		if len(Pycrypt.working_text) != 0:
			Pycrypt.stats_text_box.insert(END, 'Number of Characters: ' + str(len(Pycrypt.working_text.replace(' ', ''))))
			Pycrypt.stats_text_box.insert(END, '\n' + '-'*80 + '\n')
		
		#Count Number of Words
		self.words = Pycrypt.working_text.split(' ')
	
		if len(self.words) != 0:
			Pycrypt.stats_text_box.insert(END, 'Number of Words: ' + str(len(self.words)))
			Pycrypt.stats_text_box.insert(END, '\n' + '-'*80 + '\n')
	
		#Count Number of Lines of 80 characters
		self.lines = (len(Pycrypt.working_text)/80) + Pycrypt.working_text.count('\n')
		Pycrypt.stats_text_box.insert(END, 'Number of Lines X 80: ' + str(self.lines))
		Pycrypt.stats_text_box.insert(END, '\n' + '-'*80 + '\n')
		
		#Count Number of Sentences
		if len(Pycrypt.working_text.split(None)) > 1:
			self.sentence = Pycrypt.working_text.count('.') + Pycrypt.working_text.count('!') + Pycrypt.working_text.count('?')
			Pycrypt.stats_text_box.insert(END, 'Number of Sentences: ' + str(self.sentence))
			Pycrypt.stats_text_box.insert(END, '\n' + '-'*80 + '\n')
	
		#Collect all Double and Triple Occurances
		self.double_letter = re.findall(r'(.)\1\S\w', Pycrypt.working_text)
		self.triple_letter = re.findall(r'(.)\1\1\S\w', Pycrypt.working_text)
	
		#Check and Print Double Letters
		if self.double_letter != []:
			Pycrypt.stats_text_box.insert(END, 'Double Letter Groups\nIn Order of Occurance\n\n')
	
			for x in re.finditer(r'(.)\1', Pycrypt.working_text):
				Pycrypt.stats_text_box.insert(END, '%02d-%02d: %s\n' % (x.start(), x.end()-1, x.group(0)))
				Pycrypt.working_text_box.tag_add('double', '1.' + str(x.start()), '1.' + str(x.end()))
				Pycrypt.working_text_box.tag_config('double', background='black', foreground='red')
		
			Pycrypt.stats_text_box.insert(END, '-'*80 + '\n')
		
		#Check and Print Triple Letters
		if self.triple_letter != []:
			Pycrypt.stats_text_box.insert(END, 'Triple Letter Groups\nIn Order of Occurance\n\n')
		
			for x in re.finditer(r'(.)\1\1', Pycrypt.working_text):
				Pycrypt.stats_text_box.insert(END, '%02d-%02d: %s\n' % (x.start(), x.end()-1, x.group(0)))
				Pycrypt.working_text_box.tag_add('triple', '1.' + str(x.start()), '1.' + str(x.end()))
				Pycrypt.working_text_box.tag_config('triple', background='black', foreground='blue')
			
			Pycrypt.stats_text_box.insert(END, '-'*80 + '\n')
		
		#Count Characters for Frequency Analysis using Dictionary
		
		#Create working text Character Dictionary
		self.dic1 = {}
	
		for c in Pycrypt.working_text:
			try:
				self.dic1[c.upper()] += 1
				
			except KeyError:
				self.dic1[c.upper()] = 1
	
		#Gather Character Frequency and display sorted alphabetically
		Pycrypt.stats_text_box.insert(END, 'Frequency Analysis\nSorted by Letter\n\n')
	
		for k in sorted(self.dic1):
			Pycrypt.stats_text_box.insert(END, '%s - %d' % (k, self.dic1[k]) + '\n')
		
		Pycrypt.stats_text_box.insert(END, '' + '-'*80 + '\n')
	
		#Gather Character Frequency and display sorted numerically from biggest to smallest
		Pycrypt.stats_text_box.insert(END, 'Frequency Analysis\nSorted by Number\n\n')
	
		for k in sorted(self.dic1.keys(), key=self.dic1.get, reverse=True):
			Pycrypt.stats_text_box.insert(END, '%s - %d' % (k, self.dic1[k]) + '\n')
		
		Pycrypt.stats_text_box.insert(END, '' + '-'*80 + '\n')
	
		#Gather Character Frequency in Percent and display/list sorted numerically from biggest to smallest
		Pycrypt.stats_text_box.insert(END, 'Frequency Sorted by Percent\n\n')
	
		self.wtpf = [] 
		
		for k in sorted(self.dic1.keys(), key=(self.dic1.get), reverse=True):
			self.prct = ((float(self.dic1[k]) / float(len(Pycrypt.working_text))) * 100)
			Pycrypt.stats_text_box.insert(END, '%s %s %d' % (k, '|' * (int(self.prct)), (self.prct)) + '\n')
			self.wtpf.append(str(k.upper()))
			
		Pycrypt.stats_text_box.insert(END, '\n' + '-'*80 + '\n')
	
		#Create English Frequency Character Dictionary
		
		self.dic2 = {}
	
		for c in self.frequency_english:
			try:
				self.dic2[c] += 1
			except KeyError:
				self.dic2[c] = 1
	
		#Gather English Character Frequency and display sorted alphabetically
		Pycrypt.stats_text_box.insert(END, 'English - Frequency Analysis\nIn Percent Rounded\n\n')
	
		for k in sorted(self.dic2):
			Pycrypt.stats_text_box.insert(END, '%s %s %d' % (k, '|'*(self.dic2[k]), self.dic2[k]) + '\n')
		
		Pycrypt.stats_text_box.insert(END, '' + '-'*80 + '\n')
	
		#Gather English Character Frequency and display sorted numerically from biggest to smallest	
		Pycrypt.stats_text_box.insert(END,  'English - Frequency Analysis\nSorted By Percent Rounded\n\n')
	
		self.epf = []
	
		for k in sorted(self.dic2.keys(), key=self.dic2.get, reverse=True):
			Pycrypt.stats_text_box.insert(END, '%s %s %d' % (k, '|'*(self.dic2[k]), self.dic2[k]) + '\n')
			self.epf.append(k.upper())
		
		Pycrypt.stats_text_box.insert(END, '' + '-'*80 + '\n')
	
	def randomdictionary(self):#Create dictionary check function####
		pass
		
	def uniqueletter(self):#Create unique letter pattern function###
		pass

	def createToolTip(self, widget, text):
		toolTip = ToolTip(widget)
		def enter(event):
			toolTip.showtip(text)
		def leave(event):
			toolTip.hidetip()
		widget.bind('<Enter>', enter)
		widget.bind('<Leave>', leave)
	
class ToolTip(object):

	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0

	def showtip(self, text):
		"Display text in tooltip window"
		self.text = text
		if self.tipwindow or not self.text:
			return
		x, y, cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx() + 27
		y = y + cy + self.widget.winfo_rooty() +27
		self.tipwindow = tw = Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		try:
			# For Mac OS
			tw.tk.call("::tk::unsupported::MacWindowStyle",
					"style", tw._w,
					"help", "noActivates")
		except TclError:
			pass
		label = Label(tw, text=self.text, justify=LEFT,
					background="#ffffe0", relief=SOLID, borderwidth=1,
					font=("tahoma", "8", "normal"))
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()



class Topmenu(Frame):#Menu Bar class
	
	def __init__(self, master):#Create the menu/filemenu

		menu = Menu(root)
		root.config(menu=menu)

		filemenu = Menu(menu)
		menu.add_cascade(label='File', menu=filemenu)
		filemenu.add_command(label='New', command=self.filemenunew)
		filemenu.add_command(label='Open', command=self.filemenuopen)
		filemenu.add_command(label='Save', command=self.filemenusave)
		filemenu.add_separator()
		filemenu.add_command(label='Exit', command=self.filemenuexit)

	def filemenunew(self):#Create file new function
		pass

	def filemenuopen(self):#Create file open function
		pass

	def filemenusave(self):#Create file save function
		pass

	def filemenuexit(self):#Create file exit function
		if tkMessageBox.askokcancel('Quit', 'Do you really wish to quit?'):
			root.destroy()

class Toolbar(Frame):#Toolbar class

	def __init__(self, master):#Create toolbar/buttons

		#Create toolbar frame
		self.frame = Frame(master, bd=2, relief=RIDGE)
		self.frame.pack(side=TOP, fill=X)

		#Create power button
		self.startpng = Image.open('images/start.png')
		self.startimg = ImageTk.PhotoImage(self.startpng)
		self.stoppng = Image.open('images/stop.png')
		self.stopimg = ImageTk.PhotoImage(self.stoppng)
		self.power = Button(self.frame, width=25, height=25, image=self.startimg, command=self.startwork)
		self.power.pack(side=LEFT, padx=2, pady=2)

		#Create tools frame
		self.tools = Frame(self.frame)
		self.tools.pack(side=LEFT, padx=2, pady=2, fill=X)

		#Create replace frame
		self.replace = Frame(self.tools, bd=2, relief=RIDGE)
		self.replace.pack(side=LEFT, padx=2, pady=2)

		#Create replace button
		self.replacepng = Image.open('images/replace.png')
		self.replaceimg = ImageTk.PhotoImage(self.replacepng)
		self.strip = Button(self.replace, state=DISABLED, image=self.replaceimg, width=25, height=25, command=self.raisereplace)
		self.strip.pack(side=LEFT)

		#Create self.transposition Frame
		self.trans = Frame(self.tools, bd=2, relief=RIDGE)
		self.trans.pack(side=LEFT, padx=2, pady=2)

		#Create railfence button
		self.railpng = Image.open('images/railfence.png')
		self.railimg = ImageTk.PhotoImage(self.railpng)
		self.railfence = Button(self.trans, state=DISABLED, image=self.railimg, width=25, height=25, command=self.raiserailfence)
		self.railfence.pack(side=LEFT)

		#Create scytale button
		self.scypng = Image.open('images/scytale.png')
		self.scyimg = ImageTk.PhotoImage(self.scypng)
		self.scytale = Button(self.trans, state=DISABLED, image=self.scyimg, width=25, height=25, command=self.raisescytale)
		self.scytale.pack(side=LEFT)

		#Create substitution frame
		self.substitute = Frame(self.tools, bd=2, relief=RIDGE)
		self.substitute.pack(side=LEFT, padx=2, pady=2)

		#Create caesar cipher button
		self.caesarpng = Image.open('images/caesar.png')
		self.caesarimg = ImageTk.PhotoImage(self.caesarpng)
		self.caesar = Button(self.substitute, state=DISABLED, image=self.caesarimg, width=25, height=25, command=self.raisecaesar)
		self.caesar.pack(side=LEFT)

		#Create pigpen (fonts) button
		self.pigpng = Image.open('images/pigpen.png')
		self.pigimg = ImageTk.PhotoImage(self.pigpng)
		self.pigpen = Button(self.substitute, state=DISABLED, image=self.pigimg, width=25, height=25, command=self.passnull)##
		self.pigpen.pack(side=LEFT)

		#Create Scrabble Button
		self.monopng = Image.open('images/monoalpha.png')
		self.monoimg = ImageTk.PhotoImage(self.monopng)
		self.scrabble = Button(self.substitute, state=DISABLED, image=self.monoimg, width=25, height=25, command=self.raisescrabble)
		self.scrabble.pack(side=LEFT)

		#Create self.advanced Ciphers Frame
		self.advanced = Frame(self.tools, bd=2, relief=RIDGE)
		self.advanced.pack(side=LEFT, padx=2, pady=2)

		#Create playfair button
		self.playpng = Image.open('images/playfair.png')
		self.playimg = ImageTk.PhotoImage(self.playpng)
		self.playfair = Button(self.advanced, state=DISABLED, image=self.playimg, width=25, height=25, command=self.raiseplayfair)
		self.playfair.pack(side=LEFT)

		#Create digraph button
		self.digraphpng = Image.open('images/digraph.png')
		self.digraphimg = ImageTk.PhotoImage(self.digraphpng)
		self.digraph = Button(self.advanced, state=DISABLED, image=self.digraphimg, width=25, height=25, command=self.passnull)##
		self.digraph.pack(side=LEFT)

		#Create homophonic button
		self.homopng = Image.open('images/homophonic.png')
		self.homoimg = ImageTk.PhotoImage(self.homopng)
		self.homophonic = Button(self.advanced, state=DISABLED, image=self.homoimg, width=25, height=25, command=self.passnull)##
		self.homophonic.pack(side=LEFT)

		#Create vigener button
		self.vigenerpng = Image.open('images/vigener.png')
		self.vigenerimg = ImageTk.PhotoImage(self.vigenerpng)
		self.vigener = Button(self.advanced, state=DISABLED, image=self.vigenerimg, width=25, height=25, command=self.passnull)##
		self.vigener.pack(side=LEFT)

		#Create enigma button
		self.enigmapng = Image.open('images/enigma.png')
		self.enigmaimg = ImageTk.PhotoImage(self.enigmapng)
		self.enigma = Button(self.advanced, state=DISABLED, image=self.enigmaimg, width=25, height=25, command=self.passnull)##
		self.enigma.pack(side=LEFT)

		#Create Statistical Analysis frame
		self.stats = Frame(self.tools, bd=2, relief=RIDGE)
		self.stats.pack(side=LEFT, padx=2, pady=2)

		#Create frequency analysis button
		self.freqletpng = Image.open('images/freqletters.png')
		self.freqletimg = ImageTk.PhotoImage(self.freqletpng)
		self.freqlet = Button(self.stats, state=DISABLED, image=self.freqletimg, width=25, height=25, command=self.passnull)##
		self.freqlet.pack(side=LEFT)

		#Create frequency double letters button
		self.freqdoupng = Image.open('images/freqdouble.png')
		self.freqdouimg = ImageTk.PhotoImage(self.freqdoupng)
		self.freqdouble = Button(self.stats, state=DISABLED, image=self.freqdouimg, width=25, height=25, command=self.passnull)##
		self.freqdouble.pack(side=LEFT)

		#Create vowel trowel button
		self.vowelpng = Image.open('images/voweltrowel.png')
		self.vowelimg = ImageTk.PhotoImage(self.vowelpng)
		self.voweltrowel = Button(self.stats, state=DISABLED, image=self.vowelimg, width=25, height=25, command=self.passnull)##
		self.voweltrowel.pack(side=LEFT)

	def startwork(self):#Power On function

		#Create Original, Working, Change Text
		Pycrypt.original_text = Pycrypt.working_text_box.get(1.0, END)
		Pycrypt.working_text = Pycrypt.working_text_box.get(1.0, END)
		Pycrypt.change_text = Pycrypt.working_text

		#Change Main Text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(END, Pycrypt.working_text)

		#Change change text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		#Change power button image
		self.power.config(image=self.stopimg)
		self.power.config(command=self.stopwork)

		#Enable tools
		self.drawer = []
		self.buttons =[]

		self.drawer = self.tools.winfo_children()

		for i in self.drawer:
			self.buttons.extend(i.winfo_children())

		for i in self.buttons:
			i.config(state=NORMAL)

		Pycrypt.collectstats()

	def stopwork(self):#Power Off function

		#Confirm losing changes
		if tkMessageBox.askokcancel('Revert To Original Text?', 'You will loose any changes...'):
			Pycrypt.change_text_box.delete(1.0, END)
			Pycrypt.working_text_box.delete(1.0, END)
			Pycrypt.working_text_box.insert(END, Pycrypt.original_text)

			#Change power button image
			self.power.config(image=self.startimg)
			self.power.config(command=self.startwork)

			#Disable tools
			self.drawer = []
			self.buttons =[]

			self.drawer = self.tools.winfo_children()

			for i in self.drawer:
				self.buttons.extend(i.winfo_children())

			for i in self.buttons:
				i.config(state=DISABLED)

	def updatetext(self):#Create update text function

		Pycrypt.working_text = Pycrypt.change_text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(1.0, Pycrypt.working_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(1.0, Pycrypt.working_text)
		Pycrypt.change_text = ''
		self.update.config(state=DISABLED)

		Pycrypt.collectstats()

	def passnull(self):#Create passnull function (for toolbar buttons)
		pass

	def raisereplace(self):#Create Replace Options Toplevel
		replacetop = Replace(root)
	
	def raiserailfence(self):
		railfencetop = Railfence(root)
	
	def raisescytale(self):#Create Scytale Toplevel
		scytaletop = Scytale(root)
		
	def raisecaesar(self):#Create Caesar Toplevel
		caesartop = Caesar(root)
		
	def raisescrabble(self):#Create Scrabble Toplevel
		scrabbletop = Scrabble(root)
	
	def raiseplayfair(self):#Create Playfair Toplevel
		playfairtop = Playfair(root)

class StatusBar(Frame):#StatusBar class

	def __init__(self, master):#Create frame/status label
		Frame.__init__(self, master)
		self.label = Label(self, bd=1, text='status bar', relief=RIDGE, anchor=W)
		self.label.pack(fill=X)

	def update(self, fmt, *args):#StatusBar Update
		self.label.config(text=fmt % args)
		self.label.update_idletasks()

	def clear(self):#StatusBar Clear
		self.label.config(text='')
		self.label.update_idletasks()

class Replace(Toplevel):#Replace Options class

	def __init__(self, parent):#Initialize Toplevel

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

	def body(self, master):#Create Replace Toplevel body

		#Create substitution replace options title
		self.frame = LabelFrame(master, text='Strip Which Characters?', width=20, relief=RIDGE)
		self.frame.pack()

		#Create remove self.spaces checkbox
		self.spaces = IntVar()
		self.space = Checkbutton(self.frame, text='Spaces', variable=self.spaces)
		self.space.bind('<Button-1>', self.replacespace) 
		self.space.grid(row=0, column=0, sticky=W)

		#Create remove End Of Line checkbox
		self.eol = IntVar()
		self.endofline = Checkbutton(self.frame, text='LF', variable=self.eol)
		self.endofline.bind('<Button-1>', self.replaceeol)
		self.endofline.grid(row=1, column=1, sticky=W)

		#Create remove punctuation checkbox
		self.punct = IntVar()
		self.punctuation = Checkbutton(self.frame, text='.?!$)', variable=self.punct)
		self.punctuation.bind('<Button-1>', self.replacepunct)
		self.punctuation.grid(row=0, column=1, sticky=W)

		#Create remove numbers checkbox
		self.num = IntVar()
		self.numbers = Checkbutton(self.frame, text='Numbers', variable=self.num)
		self.numbers.bind('<Button-1>', self.replacenum)
		self.numbers.grid(row=1, column=0, sticky=W)

		#Create remove tabs checkbox
		self.tab = IntVar()
		self.tabs = Checkbutton(self.frame, text='Tabs', variable=self.tab)
		self.tabs.bind('<Button-1>', self.replacetabs)
		self.tabs.grid(row=2, column=0, sticky=W)

		#Create remove cr checkbox
		self.cr = IntVar()
		self.carriage = Checkbutton(self.frame, text='CR', variable=self.cr)
		self.carriage.bind('<Button-1>', self.replacecr)
		self.carriage.grid(row=2, column=1, sticky=W)

	def buttonbox(self):#Create buttons

		box = Frame(self)

		#Create clear options button
		self.clear = Button(self.frame, text='Clear', width=17)
		self.clear.bind('<Button-1>', self.optionclear)
		self.clear.grid(row=5, column=0, columnspan=2)

		#Create done button
		self.done = Button(self.frame, text='Done', width=17, command=self.destroy)
		self.done.bind('<Button-1>', self.replacedone)
		self.done.grid(row=6, column=0, columnspan=2)

		box.pack()

	def cancel(self, event=None):#Replace Optios cancel button/window protocol

		Pycrypt.change_text = Pycrypt.working_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)

	def optionclear(self, event):#Clear Options button

		Pycrypt.change_text = Pycrypt.working_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)

		for i in self.frame.winfo_children():
			i.config(state=NORMAL)
			i.deselect()

		Pycrypt.collectstats()

	def replacedone(self, event):#Done button

		Pycrypt.working_text = Pycrypt.change_text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(END, Pycrypt.working_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)

		Pycrypt.collectstats()

	def replacespace(self, event):#Remove spaces

		Pycrypt.change_text = Pycrypt.change_text.replace(' ', '')
		event.widget.config(state=DISABLED)

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		Pycrypt.collectstats()

	def replaceeol(self, event):#Remove End Of Line Character	

		Pycrypt.change_text = Pycrypt.change_text.replace('\n', '')
		event.widget.config(state=DISABLED)

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		Pycrypt.collectstats()	

	def replacepunct(self, event):#Remove Punctuation

		for s in string.punctuation:
			Pycrypt.change_text = Pycrypt.change_text.replace(s, '')

		event.widget.config(state=DISABLED)

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		Pycrypt.collectstats()

	def replacenum(self, event):#Remove Numbers

		for d in string.digits:
			Pycrypt.change_text = Pycrypt.change_text.replace(d, '')

		event.widget.config(state=DISABLED)

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		Pycrypt.collectstats()	

	def replacetabs(self, event):#Remove Tabs

		Pycrypt.change_text = Pycrypt.change_text.replace('\t', '   ')
		event.widget.config(state=DISABLED)	

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		Pycrypt.collectstats()

	def replacecr(self, event):#Remove End Of Line Character

		Pycrypt.change_text = Pycrypt.change_text.replace('\r', '')
		event.widget.config(state=DISABLED)

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

		Pycrypt.collectstats()

class Railfence(Toplevel):#Railfence class#TODO#
	
	def __init__(self,parent):
		
		self.rf = IntVar()#Radio button variable
		self.rail_text = []#List of letters in change text
		self.matrix = [[],[]]#list of rails
		self.encode_text = ''#encoded text according to working text
		
		Toplevel.__init__(self, parent)
		self.transient(parent)
		
		self.title('Railfence')
		
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
		
		self.buttonframe = LabelFrame(master, text='Choose # of rails')
		self.buttonframe.pack(padx=5, pady=5)
		
		self.rail1 = Radiobutton(self.buttonframe, command=self.railfence, text='2', width=3, bd=2, variable=self.rf, value=0, indicatoron=0)
		self.rail1.grid(row=0, column=0, padx=2, pady=2)
		self.rail1.deselect()
		
		self.rail2 = Radiobutton(self.buttonframe, command=self.railfence, text='3', width=3, bd=2, variable=self.rf, value=1, indicatoron=0)
		self.rail2.grid(row=0, column=1, padx=2, pady=2)
		
		self.rail3 = Radiobutton(self.buttonframe, command=self.railfence, text='4', width=3, bd=2, variable=self.rf, value=2, indicatoron=0)
		self.rail3.grid(row=0, column=2, padx=2, pady=2)
		
		self.rail4 = Radiobutton(self.buttonframe, command=self.railfence, text='5', width=3, bd=2, variable=self.rf, value=3, indicatoron=0)
		self.rail4.grid(row=1, column=0, padx=2, pady=2)
		
		self.rail5 = Radiobutton(self.buttonframe, command=self.railfence, text='6', width=3, bd=2, variable=self.rf, value=4, indicatoron=0)
		self.rail5.grid(row=1, column=1, padx=2, pady=2)
		
		self.rail6 = Radiobutton(self.buttonframe, command=self.railfence, text='7', width=3, bd=2, variable=self.rf, value=5, indicatoron=0)
		self.rail6.grid(row=1, column=2, padx=2, pady=2)
		
		self.rail7 = Radiobutton(self.buttonframe, command=self.railfence, text='8', width=3, bd=2, variable=self.rf, value=6, indicatoron=0)
		self.rail7.grid(row=2, column=0, padx=2, pady=2)
		
		self.rail8 = Radiobutton(self.buttonframe, command=self.railfence, text='9', width=3, bd=2, variable=self.rf, value=7, indicatoron=0)
		self.rail8.grid(row=2, column=1, padx=2, pady=2)
		
		self.rail9 = Radiobutton(self.buttonframe, command=self.railfence, text='10', width=3, bd=2, variable=self.rf, value=8, indicatoron=0)
		self.rail9.grid(row=2, column=2, padx=2, pady=2)
		
	def buttonbox(self):
		
		box = Frame(self)

		w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=LEFT, padx=5, pady=5)

		self.bind("&lt;Return>", self.ok)
		self.bind("&lt;Escape>", self.cancel)

		box.pack()
		
	def ok(self, event=None):
		
		Pycrypt.working_text = Pycrypt.change_text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(END, Pycrypt.working_text)
		
		self.parent.focus_set()
		self.destroy()
	
	def cancel(self, event=None):
		
		Pycrypt.change_text = Pycrypt.working_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
		
		self.parent.focus_set()
		self.destroy()
	
	def railfence(self):
		
		Pycrypt.change_text = Pycrypt.working_text
		self.encode_text = ''
		self.rail_text = []
		self.matrix = [ [] for h in range(self.rf.get() + 2)]
		
		for i in Pycrypt.change_text:
			self.rail_text.append(str(i))
		
		if len(self.rail_text) % len(self.matrix) != 0:
			for i in range((len(self.matrix) - (len(self.rail_text) % len(self.matrix)))):
				self.rail_text.append('X')
		
		while self.rail_text != []:
			for i in range(self.rf.get() + 1, -1, -1):
				self.matrix[i].append(self.rail_text.pop(i))
		
		for i in range(len(self.matrix)):
			self.encode_text += ''.join(self.matrix[i])
		
		Pycrypt.change_text = self.encode_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
		
class Scytale(Toplevel):#Scytale Shift class

	def __init__(self, parent):#Initialize Scytale Toplevel
		
		self.pr = IntVar()#Radiobutton variable
		self.scytale = []#List of letters in change text
		self.matrix = [[],[]]#list of rails
		self.encode_text = ''#encoded text according to working text
		
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

	def body(self, master):#Create Scytale Toplevel body
		
		self.frame = LabelFrame(master, bd=2, text='# of letters/wrap', relief=RIDGE)
		self.frame.pack(side=LEFT, fill=Y)

		self.radio2 = Radiobutton(self.frame, text='2', variable=self.pr, width=3, value=0, indicatoron=0, command=self.scytaleshift)
		self.radio2.grid(row=3, column=0)
		self.radio2.deselect()
		
		self.radio3 = Radiobutton(self.frame, text='3', variable=self.pr, width=3, value=1, indicatoron=0, command=self.scytaleshift)
		self.radio3.grid(row=3, column=1)

		self.radio4 = Radiobutton(self.frame, text='4', variable=self.pr, width=3, value=2, indicatoron=0, command=self.scytaleshift)
		self.radio4.grid(row=3, column=2)

		self.radio5 = Radiobutton(self.frame, text='5', variable=self.pr, width=3, value=3, indicatoron=0, command=self.scytaleshift)
		self.radio5.grid(row=4, column=0)

		self.radio6 = Radiobutton(self.frame, text='6', variable=self.pr, width=3, value=4, indicatoron=0, command=self.scytaleshift)
		self.radio6.grid(row=4, column=1)

		self.radio7 = Radiobutton(self.frame, text='7', variable=self.pr, width=3, value=5, indicatoron=0, command=self.scytaleshift)
		self.radio7.grid(row=4, column=2)

		self.radio8 = Radiobutton(self.frame, text='8', variable=self.pr, width=3, value=6, indicatoron=0, command=self.scytaleshift)
		self.radio8.grid(row=5, column=0)

		self.radio9 = Radiobutton(self.frame, text='9', variable=self.pr, width=3, value=7, indicatoron=0, command=self.scytaleshift)
		self.radio9.grid(row=5, column=1)

		self.radio10 = Radiobutton(self.frame, text='10', variable=self.pr, width=3, value=8, indicatoron=0, command=self.scytaleshift)
		self.radio10.grid(row=5, column=2,)

	def buttonbox(self):#Create buttons
		
		box = Frame(self)

		w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def ok(self, event=None):#Scytale ok button
		
		Pycrypt.working_text = Pycrypt.change_text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(END, Pycrypt.working_text)
		
		self.parent.focus_set()
		self.destroy()
		
	def cancel(self, event=None):#Scytale cancel button/protocol handler
		
		Pycrypt.change_text = Pycrypt.working_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
		
		self.parent.focus_set()
		self.destroy()

	def scytaleshift(self):#Scytale Shift function
	
		Pycrypt.change_text = Pycrypt.working_text
		self.encode_text = ''
		self.scytale = []
		self.matrix = [ [] for h in range(self.pr.get() + 2)]
		
		for i in Pycrypt.change_text:
			self.scytale.append(str(i))
		
		if len(self.scytale) % len(self.matrix) != 0:
			for i in range((len(self.matrix) - (len(self.scytale) % len(self.matrix)))):
				self.scytale.append('X')
		
		while self.scytale != []:
			for i in range(self.pr.get() + 1, -1, -1):
				self.matrix[i].append(self.scytale.pop(i))
		
		for i in range(len(self.matrix)):
			self.encode_text += ''.join(self.matrix[i])
		
		Pycrypt.change_text = self.encode_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

class Caesar(Toplevel):#Caesar Shift class
	
	def __init__(self, parent):#Initialize Caesar Toplevel
		
		self.let = []#List of old letters
		self.letindex = []#List of old letter indecies
		self.chgindex = []#List of new letter indecies
		self.chglet = []#List of new letters
		self.caesar_text = ''#Caesar Text
		
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
		
	def body(self, master):#Create Caesar Shift Toplevel body
		
		#Create slider frame
		self.slider = Frame(master, width=300, bd=2, relief=RIDGE)
		self.slider.bind('<Button-4>', self.scaleforward)
		self.slider.bind('<Button-5>', self.scaleback)
		self.slider.pack(side=LEFT, fill=Y)
		
		#Create caesar shift title
		self.label = Label(self.slider, text='Caesar Shift', width=26, relief=RAISED)
		self.label.grid(row=0, column=0)
		
		#Create caesar spacer label
		self.spacer = Label(self.slider, text='Original = Red : Encoded = Blue ', width=26)
		self.spacer.grid(row=1, column=0)
		
		#Create ceaser scale
		self.scale = Scale(self.slider, from_=0, to=25, orient=HORIZONTAL, tickinterval=13, length=210, command=self.caesarshift)
		self.scale.bind('<Button-4>', self.scaleforward)
		self.scale.bind('<Button-5>', self.scaleback)
		self.scale.grid(row=2, column=0)
		
		#Create alphabetical 'original' letter label
		self.letters = Label(self.slider, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=Pycrypt.mono_font, fg='blue', width=26)
		self.letters.bind('<Button-4>', self.scaleforward)
		self.letters.bind('<Button-5>', self.scaleback)
		self.letters.grid(row=3, column=0)
		
		#Create caesar shifted 'encoded' letter label
		self.newletters = Label(self.slider, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=Pycrypt.mono_font, fg='red', width=26)
		self.newletters.bind('<Button-4>',self.scaleforward)
		self.newletters.bind('<Button-5>', self.scaleback)
		self.newletters.grid(row=4, column=0)
		
	def buttonbox(self):#Create buttons
		box = Frame(self)
		
		w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=LEFT, padx=5, pady=5)
		
		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)
		
		box.pack()
		
	def ok(self, event=None):#Caesar ok button
		
		Pycrypt.working_text = Pycrypt.change_text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(1.0, Pycrypt.working_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(1.0, Pycrypt.working_text)
		Pycrypt.change_text = ''
		
		Pycrypt.collectstats()
		self.parent.focus_set()
		self.destroy()
		
	def cancel(self, event=None):#Caesar cancel button
		
		Pycrypt.change_text = Pycrypt.working_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)
		
		Pycrypt.collectstats()
		
		self.parent.focus_set()
		self.destroy()
		
	def caesarshift(self, event):#Caesar Shift function
		
		Pycrypt.change_text = Pycrypt.working_text
		
		self.let = []
		self.letindex = []
		self.chgindex = []
		self.chglet = []
		
		#Create initial list of letters
		for c in string.uppercase:
			self.let.append(c)
		
		#Create list of initial letters indexes
		for c in self.let:
			self.letindex.append(self.let.index(c))
		
		#Encode initial letter indexes
		for c in self.letindex:
			try:
				self.chgindex.append(self.letindex.index(c) - self.scale.get())
				
			except ValueError:
				self.chgindex.append(self.letindex[0])
				
		#Create list of encoded letters
		for c in self.chgindex:
			try:
				self.chglet.append(self.let[c])
				
			except IndexError:
				self.chglet.append(self.let[c-26])
				
		#Update caesar shift encoded label
		self.newletters.config(text='')
		self.newletters.config(text=''.join(self.chglet))
		
		#Replace text according to upper/lower/alphanumeric
		for c in Pycrypt.change_text:
			
			#Replace uppercase with encoded uppercase
			if str.isupper(str(c)):
				i = self.let.index(c)
				self.caesar_text = self.caesar_text + str(self.chglet[i])
				
			#Replace lowercase with encoded lowercase
			if str.islower(str(c)):
				i = self.let.index(string.upper(c))
				self.caesar_text = self.caesar_text + string.lower(self.chglet[i])
					
			#Replace digits with self
			if str.isdigit(str(c)):
				self.caesar_text = self.caesar_text + c
				
			#Replace any non-alphanumeric character with self
			if not str.isalnum(str(c)):
				self.caesar_text = self.caesar_text + c
				
		#Update text
		Pycrypt.change_text = self.caesar_text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
		
		self.update_idletasks()
		
		Pycrypt.collectstats()
		
	def scaleforward(self, event):#Scaleforward event function
		self.scale.set(self.scale.get() + 1)
		
	def scaleback(self, event):#Scaleback event function
		self.scale.set(self.scale.get() - 1)

class Pigpen(Toplevel):#Pigpen class#TODO#
	pass

class Scrabble(Toplevel):#Scrabble Cipher class
	
	def __init__(self, parent):#Initialize Scrabble Toplevel

		self.ct = IntVar()#Change this int var
		self.tt = IntVar()#To this int var
		self.ln1 = []#List of change this tile names
		self.ln2 = []#List of to this tile names
		self.ctlist = []#List of change this picks
		self.ttlist = []#List of to this picks
		self.matrix = [[],[]]#Matrix of change this and to this
		self.text = []#Scrabble '...' text
		self.label = []#Scrabble label text
		self.clrct = self.change_this.winfo_children()#List of change this widgets
		self.clrtt = self.to_this.winfo_children()#List of to this widgets
		
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
		
	def body(self, master):#Create Scrabble Toplevel body

		#Create scrabble letters frame
		self.letters_frame = LabelFrame(master, text='Scrabble Tiles', bd=2, relief=RIDGE)
		self.letters_frame.pack()

		#Create old scrabble tiles w/itterated radiobuttons
		self.change_this = LabelFrame(self.letters_frame, text='Change this:',  bd=2, relief=RIDGE)
		self.change_this.pack(fill=Y)
		
		self.ln1 = []
		
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
				
		#Create new scrabble tiles w/itterated radiobuttons
		self.to_this = LabelFrame(self.letters_frame, text='To this:', bd=2, relief=RIDGE)
		self.to_this.pack()
				
		self.ln2 = []
			
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
			
		#Create old scrabble list
		self.old = Label(self.letters_frame, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=Pycrypt.mono_font, fg='blue', width=26)
		self.old.pack()
	
		#Create new scrabble list
		self.new = Label(self.letters_frame, text='', font=Pycrypt.mono_font, fg='red', width=26)
		self.new.pack()
		
		#Create old scrabble tool frame
		self.analysis = LabelFrame(master, text='English Frequency Analysis', width=240, bd=2, relief=RIDGE)
		self.analysis.pack()
	
		#Create scrabble english freq analysis Title
		self.freq = Label(self.analysis, text='Click letters to use:', relief=RAISED, width=26)
		self.freq.pack()
	
		#Create scrabble working text frequency list
		self.freq_old = Label(self.analysis, text='', font=Pycrypt.mono_font, fg='blue')
		self.freq_old.bind('<Button-1>', self.scrabblefreq)
		self.freq_old.pack()
	
		if len(Pycrypt.wtpf) < 26 or len(Pycrypt.wtpf) > 26:
			self.freq_old.config(text='< 26 Char')
		
		if len(Pycrypt.wtpf) > 26:
			self.freq_old.config(text='> 26 Char')
	
		if len(Pycrypt.wtpf) == 26:
			self.freq_old.config(text=''.join(Pycrypt.wtpf).upper())
	
		#Create scrabble change text frequency list
		self.freq_new = Label(self.analysis, text=''.join(Pycrypt.epf), font=Pycrypt.mono_font, fg='red')
		self.freq_new.bind('<Button-1>', self.scrabblefreq)
		self.freq_new.pack()
		
	def buttonbox(self):#Create Buttons###STOP BUTTON AND FUNCTION
		box = Frame(self)

		#Create scrabble start button
		self.start = Button(box, text='Click to Start', width=23, command=self.startscrabble)
		self.start.pack()
		
		#Create scrabble stop button
	
		#Create scrabble clear changes button
		self.clear = Button(box, text='Clear Changes', state=DISABLED, width=23, command=self.scrabbleclear)
		self.clear.pack()
	
		#Create scrabble commit changes button
		self.done = Button(box, text='Commit Changes', width=23, command=self.destroy)
		self.done.bind('<Button-1>', self.scrabbledone)
		self.done.pack()

		box.pack()
		
	def cancel(self):#Scrabble window close

		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)
		
		Pycrypt.collectstats()
		
		self.parent.focus_set()
		self.destroy()
		
	def scrabblefreq(self, event):#Scrabble Letter Frequency Order event
		
		Pycrypt.change_text = ''
		
		#Replace text according to upper/lower/alphanumeric
		for c in Pycrypt.working_text:
		
			#Replace uppercase with encoded uppercase
			if str.isupper(str(c)):
				i = Pycrypt.wtpf.index(c)
				Pycrypt.change_text = Pycrypt.change_text + str(Pycrypt.epf[i])
			
			#Replace lowercase with encoded lowercase
			if str.islower(str(c)):
				i = Pycrypt.wtpf.index(string.upper(c))
				try:
					Pycrypt.change_text = Pycrypt.change_text + string.lower(Pycrypt.epf[i])
				except IndexError:
					pass
			
			#Replace digits with self
			if str.isdigit(str(c)):
				Pycrypt.change_text = Pycrypt.change_text + c
			
			#Replace any non-alphanumeric character with self
			if not str.isalnum(str(c)):
				Pycrypt.change_text = Pycrypt.change_text + c
		
		#Update text
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
		
		Pycrypt.collectstats()
		
	def startscrabble(self):#Start button
		
		for i in self.change_this.winfo_children():
			i.config(state=NORMAL)
			i.deselect()
			
		self.matrix = [[],[]]
		self.ctlist = []
		self.ttlist = []
		self.text = []
		self.label = []
		
		for i in Pycrypt.change_text:
			self.text.append('.')
			
		for i in string.uppercase:
			self.ctlist.append(i)
			self.ttlist.append(i)		
		
		self.new.config(text='.' * 26)
		for i in string.uppercase:
			self.label.append('.')
		
		self.start.config(state=DISABLED)
		self.clear.config(state=NORMAL)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, ''.join(self.text))
		
	def scrabbleclear(self):#clear changes button event
		
		for i in self.clrct:
			if self.clrct.index(i) <= 12:
				i.grid(row=0, column=self.clrct.index(i))
				i.deselect()
				
			if self.clrct.index(i) >= 13:
				i.grid(row=1, column=self.clrct.index(i) - 13)
				i.deselect()
		
		for i in self.clrtt:
			if self.clrtt.index(i) <= 12:
				i.grid(row=0, column=self.clrtt.index(i))
				i.deselect()
				
			if self.clrtt.index(i) >= 13:
				i.grid(row=1, column=self.clrtt.index(i) - 13)
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
		
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)
		
		Pycrypt.collectstats()
		
	def scrabbledone(self, event):#Commit changes button event
		
		Pycrypt.change_text = ''.join(self.text)
		Pycrypt.working_text = Pycrypt.change_text_box.get(1.0, END)
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(END, Pycrypt.working_text)
	
		Pycrypt.collectstats()
		
		self.parent.focus_set()
		self.destroy()
		
	def ctevent(self):#'Change this' tiles
		
		try:
			self.ctlist.remove(string.uppercase[self.ct.get()])
			self.matrix[0].extend([string.uppercase[self.ct.get()]])
			
			for i in self.change_this.winfo_children():
				i.config(state=DISABLED)
				i.deselect()
				
			for i in self.to_this.winfo_children():
				i.config(state=NORMAL)
				i.deselect()
				
		except ValueError:
			if tkMessageBox.showinfo('Used Letter', 'Letter Already Used'):
				pass
		
	def ttevent(self):#'To this' tiles
		
		try:
			self.ttlist.remove(string.uppercase[self.tt.get()])
			self.matrix[1].extend([string.uppercase[self.tt.get()]])
			
			for i in self.change_this.winfo_children():
				i.config(state=NORMAL)
				i.deselect()
				
			for i in self.to_this.winfo_children():
				i.config(state=DISABLED)
				i.deselect()
			
			#Change scrabble_new label
			self.label[string.uppercase.index(self.matrix[0][-1])] = self.matrix[1][-1]
			self.new.config(text=''.join(self.label))
				
			#update change text
			for c in range(0, len(Pycrypt.change_text)):
				
				if str.isupper(str(Pycrypt.change_text[c])):
					
					if Pycrypt.change_text[c] == self.matrix[0][-1]:
						self.text[c] = self.matrix[1][-1]
				
				if str.islower(str(Pycrypt.change_text[c])):
					
					if str.upper(str(Pycrypt.change_text[c])) == self.matrix[0][-1]:
						self.text[c] = str.lower(self.matrix[1][-1])
			
			Pycrypt.change_text_box.delete(1.0, END)
			Pycrypt.change_text_box.insert(END, ''.join(self.text))
			
		except ValueError:
			if tkMessageBox.showinfo('Used Letter', 'Letter Already Used'):
				pass

class Playfair(Toplevel):#Playfair Cipher class
	
	def __init__(self, parent):#Playfair Toplevel initialize
		
		self.key = StringVar()#Key entry string var
		self.dic = []#list of unique letters
		self.square = []#List of unique letters + alphabet
		self.copy = []#Copy of self.square for popping
		self.matrix = []#Playfair square with key matrix
		self.digraph_text = []#List of change text split in pairs
		
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
		
	def body(self, master):#Playfair body 
		
		self.keyframe = LabelFrame(master, text='Enter Key Here:', bd=2, relief=RIDGE)
		self.keyframe.pack()
		
		self.entry = Entry(self.keyframe, textvariable=self.key, width=26)
		self.entry.bind('<KeyRelease>', self.validate)
		self.entry.bind('<BackSpace>', self.entryclear)
		self.entry.bind('<Return>', self.usekey)
		self.entry.pack()
		
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
	
	def buttonbox(self):#Playfair buttonbox
		
		box = Frame(self)

		w = Button(box, text='Encode', command=self.encode)
		w.grid(row=0, column=0, padx=5, pady=5)
		w = Button(box, text='Decode', command=self.decode)
		w.grid(row=0, column=1, padx=5, pady=5)
		w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
		w.grid(row=1, column=0, padx=5, pady=5)
		w = Button(box, text="Cancel", width=10, command=self.cancel)
		w.grid(row=1, column=1, padx=5, pady=5)
		
		self.bind("<Escape>", self.cancel)
		
		box.pack()

	def entryclear(self, event):#Playfair clear entry box
		self.key.set('')
	
	def validate(self, event):#Playfair text only entry validation
		if event.char == '\r':
			pass
		
		elif event.char.upper() not in string.uppercase:
			self.key.set(self.key.get()[0:-1])
		
		elif event.char.upper() == 'J':
			self.key.set(self.key.get()[0:-1] + 'I')

	def encode(self):#Playfair encode text
		
		self.encode_text = []
		
		for i in self.digraph_text:
			self.first = i[0]
			self.second = i[1]
			
			if self.first == 'J':
				self.first = 'I'
				
			if self.second == 'J':
				self.second = 'I'
				
			x1, y1 = Pycrypt.matrixindex(self.first, self.matrix)
			x2, y2 = Pycrypt.matrixindex(self.second, self.matrix)
			
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
		Pycrypt.change_text = ' '.join(self.encode_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
	
	def decode(self):#Playfair decode text
		
		self.decode_text = []
		
		for i in self.digraph_text:
			self.first = i[0]
			self.second = i[1]
			
			if self.first == 'J':
				self.first = 'I'
				
			if self.second == 'J':
				self.second = 'I'
				
			x1, y1 = Pycrypt.matrixindex(self.first, self.matrix)
			x2, y2 = Pycrypt.matrixindex(self.second, self.matrix)
										
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
		Pycrypt.change_text = ' '.join(self.decode_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
	
	def ok(self, event=None):#Playfair ok button/event
		
		Pycrypt.change_text = ''.join(self.digraph_text)
		Pycrypt.working_text = Pycrypt.change_text
		Pycrypt.working_text_box.delete(1.0, END)
		Pycrypt.working_text_box.insert(END, Pycrypt.working_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)
	
		self.parent.focus_set()
		self.destroy()
		
		Pycrypt.collectstats()
		
	def cancel(self, event=None):#Playfair cancel button/event/protocol
		
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.working_text)
				
		self.parent.focus_set()
		self.destroy()
		
		Pycrypt.collectstats()
		
	def usekey(self, event):#Playfair unique letters from key into square and fill
		
		self.dic = []
		self.square = []
		self.copy = []
		
		for i in string.uppercase:
			
			if i == 'J':
				pass
			
			else:
				self.square.append(i)
				self.copy.append(i)
				
		for i in string.upper(self.key.get()):
			if i in self.dic:
				pass
				
			else:
				self.dic.append(i)
				
		for i in self.dic:
			try:
				self.square.remove(i)
				self.square.insert(self.dic.index(i), i)
				self.copy.remove(i)
				self.copy.insert(self.dic.index(i), i)
				
			except ValueError:
				pass
				
		for i in self.squareframe.winfo_children():
			i.config(text=self.copy.pop(0))
				
		self.matrix = [ self.square[i * 5: (i+1) * 5] for i in range(5) ]
		
		self.digraph_text = [Pycrypt.change_text[i:i+2] for i in range(0, len(Pycrypt.change_text), 2)]
		self.digraph_text = [i.upper() for i in self.digraph_text]
		
		if len(self.digraph_text[-1]) == 1:
			self.digraph_text[-1] += 'X'
		
		Pycrypt.change_text = ' '.join(self.digraph_text)
		Pycrypt.change_text_box.delete(1.0, END)
		Pycrypt.change_text_box.insert(END, Pycrypt.change_text)

class Digraph(Toplevel):#Create digraph#TODO#
	pass

class Homophonic(Toplevel):#Create homophonic#TODO#
	pass

class Vigener(Toplevel):#Create vigener#TODO#
	pass

class Enigma(Toplevel):#Create enigma#TODO#
	pass

#Instantiate root, Pycrypt, Topmenu and Toolbar
root = Tk()
root.title('The Code Program')
#root.geometry('900x600')
#root.protocol('WM_DELETE_WINDOW', filemenuexit)#intercept window close button

Pycrypt = Pycrypt()
menu = Topmenu(root)
tools = Toolbar(root)

root.mainloop()