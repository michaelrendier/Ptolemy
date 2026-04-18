#/usr/bin/python
from Tkinter import *
#from mx.TextTools import *
import tkMessageBox
import re
import string
import collections
import tkFont
import Image, ImageTk


#Global Variables
#####

original_text = ''
working_text = ''
change_text = ''
current_toolbox = 'transposition'
epf = [] #english language character percent frequency
wtpf = [] #working text percent frequency
let = [] #list of alphabetical letters
selet = [] #list of letters for popping
for c in string.uppercase:
	selet.append(c)


#Create file menu functions
#####


###Create file new function
#####
def filemenunew():
	pass


###Create file open function
#####
def filemenuopen():
	pass


###Create file save function
#####
def filemenusave():
	pass
	
###Create file exit function
def filemenuexit():
    if tkMessageBox.askokcancel('Quit', 'Do you really wish to quit?'):
        root.destroy()


#Create toolbox menu functions
#####

###Create transposition toolbox visibility function
#####
def transposition():
	global current_toolbox
	
	sub_toolbox.grid_forget()
	stats_toolbox.grid_forget()
	#acipher_toolbox.grid_forget()
	
	trans_toolbox.grid(row=1, columnspan=2, sticky=NW)
	current_toolbox = 'trans'

###Create substitution toolbox visibility function
#####
def substitution():
	global current_toolbox
	
	trans_toolbox.grid_forget()
	stats_toolbox.grid_forget()
	#acipher_toolbox.grid_forget()
	
	sub_toolbox.grid(row=1, columnspan=2, sticky=NW)
	current_toolbox = 'sub'	

###Create statistical analysis toolbox visibility function
#####
def statsanalysis():	
	global current_toolbox
	
	trans_toolbox.grid_forget()
	sub_toolbox.grid_forget()
	#acipher_toolbox.grid_forget()
	
	stats_toolbox.grid(row=1, columnspan=2, sticky=NW)
	current_toolbox = 'stats'
	
###Create Advanced Ciphers toolbox visibility function
#####
def advancedcipher():
	global current_toolbox
	
	#sub_toolbox.grid_forget()
	#trans_toolbox.grid_forget()
	#stats_toolbox.grid_forget()
	
	#acipher_toolbox.grid(row=1, columnspan=2, sticky=NW)
	#current_toolbox = 'acipher'
	pass
	
#Create startwork function
#####
def startwork():
	global original_text
	global working_text
	global change_text
	
	###Create Original, Working, Change Text
	original_text = working_text_box.get(1.0, END)
	working_text = working_text_box.get(1.0, END)
	change_text = working_text
	
	###Create replace options start work toplevel
	replace_top = Toplevel()
	replace_top.title('Replace Characters')
	
	###Create substitution replace options title
	opt_spacer = Label(replace_top, text='Strip Characters', width=20, relief=RAISED)
	opt_spacer.grid(row=0, columnspan=2)
	
	###Create replace options label
	opt_label = Label(replace_top, text='Check to Remove')
	opt_label.grid(row=1, column=0, columnspan=2)
	
	###Create remove spaces checkbox
	spaces = IntVar()
	spaces_chk = Checkbutton(replace_top, text='Spaces', variable=spaces)
	spaces_chk.bind('<Button-1>', replacespace) 
	spaces_chk.grid(row=2, column=0, sticky=W)
		
	###Create remove End Of Line checkbox
	eol = IntVar()
	eol_chk = Checkbutton(replace_top, text='LF', variable=eol)
	eol_chk.bind('<Button-1>', replaceeol)
	eol_chk.grid(row=3, column=1, sticky=W)
		
	###Create remove punctuation checkbox
	punct = IntVar()
	punct_chk = Checkbutton(replace_top, text='.?!$)', variable=punct)
	punct_chk.bind('<Button-1>', replacepunct)
	punct_chk.grid(row=2, column=1, sticky=W)
	
	###Create remove numbers checkbox
	num = IntVar()
	num_chk = Checkbutton(replace_top, text='Numbers', variable=num)
	num_chk.bind('<Button-1>', replacenum)
	num_chk.grid(row=3, column=0, sticky=W)
	
	###Create remove tabs checkbox
	tabs = IntVar()
	tabs_chk = Checkbutton(replace_top, text='Tabs', variable=tabs)
	tabs_chk.bind('<Button-1>', replacetabs)
	tabs_chk.grid(row=4, column=0, sticky=W)
	
	###Create remove cr checkbox
	cr = IntVar()
	cr_chk = Checkbutton(replace_top, text='CR', variable=cr)
	cr_chk.bind('<Button-1>', replacecr)
	cr_chk.grid(row=4, column=1, sticky=W)
	
	###Change Main Text
	working_text_box.delete(1.0, END)
	working_text_box.insert(END, working_text)
	
	###Change change text
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, working_text)
	
	###Collect Stats
	collectstats()
	spaces_chk.config(state=NORMAL)
	eol_chk.config(state=NORMAL)
	punct_chk.config(state=NORMAL)
	num_chk.config(state=NORMAL)
	tabs_chk.config(state=NORMAL)
	se.set('')
	start_btn.config(state=DISABLED)
	stop_btn.config(state=NORMAL)
	
	###Create clear options button
	opt_clear = Button(replace_top, text='Clear Options', width=17, command=replace_top.destroy)
	opt_clear.bind('<Button-1>', optionclear)
	opt_clear.grid(row=5, column=0, columnspan=2)
	
	###Create done button
	opt_done = Button(replace_top, text='Done', width=17, command=replace_top.destroy)
	opt_done.bind('<Button-1>', replacedone)
	opt_done.grid(row=6, column=0, columnspan=2)
	
#Create stopwork function
#####
def stopwork():
	global original_text
	
	if tkMessageBox.askok('Revert To Original Text?', 'You will loose any changes...'):
		change_text_box.delete(1.0, END)
		working_text_box.delete(1.0, END)
		working_text_box.insert(END, original_text)
		start_btn.config(state=NORMAL)
		stop_btn.config(state=DISABLED)	
		
		se.set('')
		
#Create update text function
#####
def updatetext():
	global workign_text
	global change_text
	
	working_text = change_text
	working_text_box.delete(1.0, END)
	working_text_box.insert(1.0, working_text)
	change_text_box.delete(1.0, END)
	change_text_box.insert(1.0, working_text)
	change_text = ''
	update_text.config(state=DISABLED)
	
	collectstats()
	
#Create scrabble toplevel function
def scrabbletop():
	global working_text
	global change_text
	
	scrabble_text = ''
	for i in change_text:
		scrabble_text += '*'
		
		
	
	scrabble_top = Toplevel()
	scrabble_top.title('Scrabble-Monoalphabetic')
	
	scrabble_top_frame = Frame(scrabble_top, width=240, height=240)
	scrabble_top_frame.pack()
	
	def scrabblechange():
		pass####
		
	def scrabblelabels(event):
		pass####
		#disablestate
				
	def disablestate():
		if event.widget.cget('state') == 'NORMAL':
			event.widget.config(state=DISABLED)
				
		if event.widget.cget('state') == 'DISABLED':
			if tkMessageBox.showerror('Character Already Defined', 'Clear Changes first...'):
				pass
				
	def enablestates():
		for i in range(0, 26):
			ln1[i].config(state=NORMAL)
			ln2[i].config(state=NORMAL)
			
	def scrabbledone(event):
		global working_text
	
		working_text = change_text
		working_text_box.delete(1.0, END)
		working_text_box.insert(END, working_text)
	
		collectstats()

	###
	scrabble_change_this = Frame(scrabble_top_frame, width=240, height=120)
	scrabble_change_this.pack()
	
	ln1 = []
	ct = IntVar()
	for l in range(1, 27):
		ln1.append('label_name1' + str(l))

	for i in range(0, 26):	
		ln1[i] = Radiobutton(scrabble_change_this, text=string.uppercase[i], width=1, bd=2, fg='blue', command=scrabblelabels, variable=ct, value=i, indicatoron=0)
		
		if i <= 12:
			ln1[i].grid(row=0, column=i)
					
		if i >= 13:
			ln1[i].grid(row=1, column=i - 13)
	
	###	
	scrabble_to_this = Frame(scrabble_top_frame, width=240, height=120)
	scrabble_to_this.pack()
	
	ln2 = []
	tt = IntVar()	
	for l in range(1, 27):
		ln2.append('label_name2' + str(l))

	for i in range(0, 26):	
		ln2[i] = Radiobutton(scrabble_to_this, text=string.uppercase[i], width=1, bd=2, fg='red', relief=RIDGE, command=scrabblelabels, variable=tt, value=i, indicatoron=0)
		
		if i <= 12:
			ln2[i].grid(row=2, column=i)
					
		if i >= 13:
			ln2[i].grid(row=3, column=i - 13)
		
	clear_scrabble = Button(scrabble_top, text='Clear Changes', width=23, command=enablestates)
	clear_scrabble.pack()
	
	done_scrabble = Button(scrabble_top, text='Commit Changes', width=23, command=scrabble_top.destroy)
	done_scrabble.bind('<Button-1>', scrabbledone)
	done_scrabble.pack()
	
	collectstats()
	
#Create replace options event functions	
#####

###Remove Spaces
#####
def replacespace(event):
	global working_text
	global change_text
	
	change_text = change_text.replace(' ', '')
	event.widget.config(state=DISABLED)
			
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, change_text)
	
	collectstats()

###Remove End Of Line Character	
#####
def replaceeol(event):
	global working_text
	global change_text

	change_text = change_text.replace('\n', '')
	event.widget.config(state=DISABLED)
	
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, change_text)
	
	collectstats()	
		
###Remove Punctuation
#####
def replacepunct(event):
	global working_text
	global change_text
	
	for s in string.punctuation:
		change_text = change_text.replace(s, '')
		
	event.widget.config(state=DISABLED)
	
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, change_text)
	
	collectstats()

###Remove Numbers
#####
def replacenum(event):
	global working_text
	global change_text
	
	for d in string.digits:
		change_text = change_text.replace(d, '')
		
	event.widget.config(state=DISABLED)
		
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, change_text)
	
	collectstats()	
		
###Remove Tabs
#####
def replacetabs(event):
	global working_text
	global change_text
	
	change_text = change_text.replace('\t', '   ')
	event.widget.config(state=DISABLED)	
		
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, change_text)
	
	collectstats()

###Remove End Of Line Character	
#####
def replacecr(event):
	global working_text
	global change_text
	
	change_text = change_text.replace('\r', '')
	event.widget.config(state=DISABLED)
		
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, change_text)
	
	collectstats()	

###Create clear options function
#####
def optionclear(event):
	global working_text
	global original_text
	
	change_text_box.delete(1.0, END)
	change_text_box.insert(END, working_text)
	change_text = working_text
	
	collectstats()
	startwork()

###Create replace options done function
#####
def replacedone(event):
	global working_text
	
	working_text = change_text
	working_text_box.delete(1.0, END)
	working_text_box.insert(END, working_text)
	
	collectstats()
	
#Create collectstats function
#####
def collectstats():
	global working_text
	global spaces
	global eol
	global punct
	global num
	global epf
	global wtpf
		
	stats_text_box.delete(1.0, END)
	
	###Count Number of Characters
	if len(working_text) != 0:
		stats_text_box.insert(END, 'Number of Characters: ' + str(len(working_text.replace(' ', ''))))
		stats_text_box.insert(END, '\n' + '-'*40 + '\n')
		
	###Count Number of Words
	words = working_text.split(' ')
	
	if len(words) != 0:
		stats_text_box.insert(END, 'Number of Words: ' + str(len(words)))
		stats_text_box.insert(END, '\n' + '-'*40 + '\n')
	
	###Count Number of Lines of 80 characters
	lines = (len(working_text)/80) + working_text.count('\n')	
	stats_text_box.insert(END, 'Number of Lines X 80: ' + str(lines))
	stats_text_box.insert(END, '\n' + '-'*40 + '\n')
		
	###Count Number of Sentences
	if len(working_text.split(None)) > 1:
		sentence = working_text.count('.') + working_text.count('!') + working_text.count('?')
		stats_text_box.insert(END, 'Number of Sentences: ' + str(sentence))
		stats_text_box.insert(END, '\n' + '-'*40 + '\n')
	
	###Collect all Double and Triple Occurances
	double_letter = re.findall(r'(.)\1\S\w', working_text)
	triple_letter = re.findall(r'(.)\1\1\S\w', working_text)
	
	###Check and Print Double Letters
	if double_letter != []:
		stats_text_box.insert(END, 'Double Letter Groups\nIn Order of Occurance\n\n')
	
		for x in re.finditer(r'(.)\1', working_text):
			stats_text_box.insert(END, '%02d-%02d: %s\n' % (x.start(), x.end()-1, x.group(0)))
			working_text_box.tag_add('double', '1.' + str(x.start()), '1.' + str(x.end()))
			working_text_box.tag_config('double', background='black', foreground='red')
		
		stats_text_box.insert(END, '-'*40 + '\n')
		
	###Check and Print Triple Letters
	if triple_letter != []:
		stats_text_box.insert(END, 'Triple Letter Groups\nIn Order of Occurance\n\n')
		
		for x in re.finditer(r'(.)\1\1', working_text):
			stats_text_box.insert(END, '%02d-%02d: %s\n' % (x.start(), x.end()-1, x.group(0)))
			working_text_box.tag_add('triple', '1.' + str(x.start()), '1.' + str(x.end()))
			working_text_box.tag_config('triple', background='black', foreground='blue')
			
		stats_text_box.insert(END, '-'*40 + '\n')
		
	###Count Characters for Frequency Analysis using Dictionary
		
	###Create working_text Character Dictionary
	d = {}
	
	for c in working_text:
		try:
			d[c.upper()] += 1
		except:
			d[c.upper()] = 1
	
	###Gather Character Frequency and display sorted alphabetically
	stats_text_box.insert(END, 'Frequency Analysis\nSorted by Letter\n\n')		
	
	for k in sorted(d):
		stats_text_box.insert(END, '%s %s %d' % (k, '|'*(d[k]), d[k]) + '\n')
		
	stats_text_box.insert(END, '' + '-'*40 + '\n')
	
	###Gather Character Frequency and display sorted numerically from biggest to smallest
	stats_text_box.insert(END, 'Frequency Analysis\nSorted by Number\n\n')	
	
	for k in sorted(d.keys(), key=d.get, reverse=True):
		stats_text_box.insert(END, '%s %s %d' % (k, '|'*(d[k]), d[k]) + '\n')
		
	stats_text_box.insert(END, '' + '-'*40 + '\n')
	
	###Gather Character Frequency in Percent and display/list sorted numerically from biggest to smallest
	stats_text_box.insert(END, 'Frequency Sorted by Percent\n\n')
	
	wtpf = [] 
		
	for k in sorted(d.keys(), key=(d.get), reverse=True):
		prct = float(d[k]) / float(len(working_text))
		stats_text_box.insert(END, '%s %s %d' % (k, '|' * (int(prct * 100)), (prct * 100)) + '\n')
		
		wtpf.append(str(k.upper()))
		if len(wtpf) < 26 or len(wtpf) > 26:
			monoalpha_freq_old.config(text='Less than 26 Characters')
			
		if len(wtpf) > 26:
			monoalpha_freq_old.config(text='More than 26 Characters')
		
		if len(wtpf) == 26:
			monoalpha_freq_old.config(text=''.join(wtpf).upper())
		
	stats_text_box.insert(END, '\n' + '-'*40 + '\n')
	
	###Create English Frequency Character Dictionary ****SIMPLIFY TEXT****	
	frequency_english = 'AAAAAAAABBCCCDDDDEEEEEEEEEEEEEFFGGHHHHHHIIIIIIIJKLLLLMMNNNNNNNOOOOOOOOPPQRRRRRRSSSSSSTTTTTTTTTUUUVWWXYYZ'
	d2 = {}
	
	for c in frequency_english:
		try:
			d2[c] += 1
		except:
			d2[c] = 1
	
	###Gather English Character Frequency and display sorted alphabetically		
	stats_text_box.insert(END, 'English - Frequency Analysis\nIn Percent Rounded\n\n')		
	
	for k in sorted(d2):
		stats_text_box.insert(END, '%s %s %d' % (k, '|'*(d2[k]), d2[k]) + '\n')
		
	stats_text_box.insert(END, '' + '-'*40 + '\n')
	
	###Gather English Character Frequency and display sorted numerically from biggest to smallest	
	stats_text_box.insert(END,  'English - Frequency Analysis\nSorted By Percent Rounded\n\n')
	
	epf = []
	
	for k in sorted(d2.keys(), key=d2.get, reverse=True):
		stats_text_box.insert(END, '%s %s %d' % (k, '|'*(d2[k]), d2[k]) + '\n')
		epf.append(k.upper())
		
	monoalpha_freq_new.config(text=''.join(epf))
	stats_text_box.insert(END, '' + '-'*40 + '\n')
	
###Create dictionary check function##########
#####			
#def randomdictionary():

#Create caesarshift event function		
#####
def caesarshift(event):
	global working_text
	global change_text
	global let

	let = []
	let_index = []
	chg_index = []
	chg_let = []
	
	change_text = working_text
	###Create initial list of letters
	for c in string.uppercase:
		let.append(c)
		
	###Create list of initial letters indexes
	for c in let:
		let_index.append(let.index(c))
	
	###Encode initial letter indexes	
	for c in let_index:
		try:
			chg_index.append(let_index.index(c) - caesar_sub.get())
		
		except ValueError:
			chg_index.append(let_index[0])
	
	###Create list of encoded letters
	for c in chg_index:
		try:
			chg_let.append(let[c])
			
		except IndexError:
			chg_let.append(let[c-26])
	
	###Update caesar shift encoded label		
	change_scale.config(text=''.join(chg_let))
		
	###Replace text according to upper/lower/alphanumeric
	caesar_text = ''
	for c in change_text:
		
		###Replace uppercase with encoded uppercase				
		if str.isupper(str(c)):
			i = let.index(c)
			caesar_text = caesar_text + str(chg_let[i])
		
		###Replace lowercase with encoded lowercase				
		if str.islower(str(c)):
			i = let.index(string.upper(c))
			caesar_text = caesar_text + string.lower(chg_let[i])
		
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
	update_text.config(state=NORMAL)
	collectstats()

###Create scaleforward event function
#####
def scaleforward(event):
	caesar_sub.set(caesar_sub.get() + 1)

###Create scaleback event function
#####
def scaleback(event):
	caesar_sub.set(caesar_sub.get() - 1)

#Create monoalphabetic shift functions
#####

###Create monoalpha <KeyPress> event
#####
def monoalphacaps(event):
	global selet	
	
	###Make list to check if character has been used
	if se.get() == '':
		selet = []
		for c in string.uppercase:
			selet.append(c)
	
	###Check if character typed has been used already
	try:
		selet.pop(selet.index(se.get()[-1:].upper()))
		se.set(se.get().upper())

	except ValueError:
		se.set(se.get()[:-1].upper())

###Create monoalpha <BackSpace> event
#####
def monoalphaclear(event):
	global selet
	
	se.set('')

###Create monoalpha <Return> event
#####
def monoalphatext(event):
	global working_text
	
	sel = str(se.get())
	change_text = ''
	
	###Check number of letters input = 26
	if len(sel) < 26 or len(sel) >26:
		if tkMessageBox.askokcancel('OK', '26 Letters Required, No Spaces'):
			pass
	if len(sel) == 26:
		monoalpha_text = []
		change_text = ''
		for t in se.get():
			monoalpha_text.append(t)
		
		monoalpha_new.config(text=se.get())
		
		###Replace text according to upper/lower/alphanumeric
		for c in working_text:
		
			###Replace uppercase with encoded uppercase				
			if str.isupper(str(c)):
				i = let.index(c)
				change_text = change_text + str(monoalpha_text[i])
		
			###Replace lowercase with encoded lowercase				
			if str.islower(str(c)):
				i = let.index(string.upper(c))
				change_text = change_text + string.lower(monoalpha_text[i])
		
			###Replace digits with self							
			if str.isdigit(str(c)):
				change_text = change_text + c
		
			###Replace any non-alphanumeric character with self				
			if not str.isalnum(str(c)):
				change_text = change_text + c
	
	###Update text
	working_text = change_text		
	working_text_box.delete(1.0, END)
	working_text_box.insert(END, working_text)
	collectstats()

###Create monoalpha Letter Frequency Order <Button-1> event	
#####
def monoalphafreq(event):
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
				
#Create scytale function##########
#####
def scytaleshift():
	global working_text
	global change_text
	global pr
	
	scytale = []
	change_text = working_text
	
	#Pre-allocate a 2D matrix of empty lists.
	def newmatrix(W, H):
		return [ [ [] for i in range(W) ] for j in range(H) ]
	
	matrix = newmatrix(15, 1)	
	print 'matrix =\n', matrix
	
	for c in change_text:
		scytale.append(c)
	print 'pr.get() =', pr.get()
	print 'scytale =\n', scytale
	for c in scytale:
		print 'c =', c
		for s in range(pr.get() + 1, -1, -1):
			try:
				matrix[0][s].extend([str(scytale.pop(s))])
				#print 'scytale =\n', scytale
				print 'matrix line=\n', matrix[0][s]
			except IndexError:
				matrix[0][s].extend([str(scytale.pop())])
				#print 'scytale =\n', scytale
				print 'matrix line=\n', matrix[0][s]
				
	print 'matrix =\n', matrix
			
	change_text_box.delete(1.0, END)
		
	for s in range(0, 15):
		change_text_box.insert(END, ''.join(matrix[0][s]))
		
	change_text = change_text_box.get(1.0, END)		
	update_text.config(state=NORMAL)	
	
def debugprint(event):
	print event.x / 7, event.y / 14
	

#Create Status Bar Class        
#####
class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, text='status bar', relief=RIDGE, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text='')
        self.label.update_idletasks()

###Create window	
root = Tk()
root.wm_title('The Code Program')
#root.geometry('900x600')
#root.protocol('WM_DELETE_WINDOW', filemenuexit)#intercept window close button

#####
###Create the menu
#####
menu = Menu(root)
root.config(menu=menu)

###Create file menu
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New', command=filemenunew)
filemenu.add_command(label='Open', command=filemenuopen)
filemenu.add_command(label='Save', command=filemenusave)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=filemenuexit)

###Create Toolbox menu
toolboxmenu = Menu(menu)
menu.add_cascade(label='Cipher Class', menu=toolboxmenu)
toolboxmenu.add_command(label='Transposition', command=transposition)
toolboxmenu.add_command(label='Substitution', command=substitution)
toolboxmenu.add_command(label='Advanced', command=advancedcipher)


#####
###Create toolbar
#####

###Create toolbar frame
toolbar = Frame(root, bd=2, relief=RIDGE)

###Create start button
start_btn = Button(toolbar, text='Start', width=5, command=startwork)
start_btn.pack(side=LEFT, padx=2, pady=2)

###Create stop button
stop_btn = Button(toolbar, text='Stop', width=5, state=DISABLED, command=stopwork)
stop_btn.pack(side=LEFT, padx=2, pady=2)

###Create update text button
update_text = Button(toolbar, text='Update', width=5, state=DISABLED, command=updatetext)
update_text.pack(side=LEFT, padx=2, pady=2)

###Create Scrabble Button
#####
monopng = Image.open('images/monoalpha.png')
monoimg = ImageTk.PhotoImage(monopng)

scrabble_btn = Button(toolbar, image=monoimg, width=25, height=25, command=scrabbletop)
scrabble_btn.pack(side=LEFT, padx=2, pady=2)

toolbar.pack(side=TOP, fill=X)

#####
###Create window frame
#####
window_frame = Frame(root, bd=2, relief=RIDGE)
window_frame.pack(fill=BOTH)

###Create text frame
text_frame = Frame(window_frame, bd=2, relief=RIDGE)
text_frame.grid(row=0, column=0)

###Create working text box
working_scroll = Scrollbar(text_frame)
working_scroll.grid(row=0, column=1, sticky=N+S)

working_text_box = Text(text_frame, yscrollcommand=working_scroll.set, height=12, width=80, insertbackground='white', fg='white', bg='black')
working_text_box.grid(row=0, column=0)

working_scroll.config(command=working_text_box.yview)

##Create change text box
change_scroll = Scrollbar(text_frame)
change_scroll.grid(row=1, column=1, sticky=N+S)

change_text_box = Text(text_frame, yscrollcommand=change_scroll.set, height=12, width=80, insertbackground='white', fg='green', bg='black')
change_text_box.grid(row=1, column=0)

change_scroll.config(command=change_text_box.yview)

###Create stats text box
stats_scroll = Scrollbar(text_frame)
stats_scroll.grid(row=0, column=3, rowspan=2, sticky=N+S)

stats_text_box = Text(text_frame, yscrollcommand=stats_scroll.set, height=24, width=40, fg='white', bg='black')
stats_text_box.grid(row=0, column=2, rowspan=2)

stats_scroll.config(command=stats_text_box.yview)

#####
###Create transposition toolbox
#####
trans_toolbox = Frame(window_frame, height=200, width=892, bd=2, relief=RIDGE)
trans_toolbox.grid(row=1, columnspan=2, sticky=NW)

#####
###Create Rail Fence
#####

#####
###Create Latin Square & Key
#####

#####
###Create scytale tool
#####
scytale_frame = Frame(trans_toolbox, bd=2, relief=RIDGE)
scytale_frame.pack(side=LEFT, fill=Y)

scytale_title = Label(scytale_frame, text='Scytale Transposition', width=21, relief=RAISED)
scytale_title.grid(row=0, column=0, columnspan=3)

scytale_label = Label(scytale_frame, text='Letters per wrap', width=21)
scytale_label.grid(row=1, column=0, columnspan=3)

pr = IntVar()

scytale_radio2 = Radiobutton(scytale_frame, text='2', variable=pr, value=0, command=scytaleshift)
scytale_radio2.grid(row=3, column=0, sticky=W)

scytale_radio3 = Radiobutton(scytale_frame, text='3', variable=pr, value=1, command=scytaleshift)
scytale_radio3.grid(row=3, column=1, sticky=W)

scytale_radio4 = Radiobutton(scytale_frame, text='4', variable=pr, value=2, command=scytaleshift)
scytale_radio4.grid(row=3, column=2, sticky=W)

scytale_radio5 = Radiobutton(scytale_frame, text='5', variable=pr, value=3, command=scytaleshift)
scytale_radio5.grid(row=4, column=0, sticky=W)

scytale_radio6 = Radiobutton(scytale_frame, text='6', variable=pr, value=4, command=scytaleshift)
scytale_radio6.grid(row=4, column=1, sticky=W)

scytale_radio7 = Radiobutton(scytale_frame, text='7', variable=pr, value=5, command=scytaleshift)
scytale_radio7.grid(row=4, column=2, sticky=W)

scytale_radio8 = Radiobutton(scytale_frame, text='8', variable=pr, value=6, command=scytaleshift)
scytale_radio8.grid(row=5, column=0, sticky=W)

scytale_radio9 = Radiobutton(scytale_frame, text='9', variable=pr, value=7, command=scytaleshift)
scytale_radio9.grid(row=5, column=1, sticky=W)

scytale_radio10 = Radiobutton(scytale_frame, text='10', variable=pr, value=8, command=scytaleshift)
scytale_radio10.grid(row=5, column=2, sticky=W)

#for i in range(0, 15):
#	scytale_radio = 'scytail_radio' + str(i + 2)
#	if i + 2 == 2 or i + 2 == 3 or i + 2 == 4:
#		scytale_radio = Radiobutton(scytale_frame, text=i + 2, variable=pr, value=i)
#		scytale_radio.bind('<Button-1>', scytaleshift)
#	for c in range(0, 3):
#		scytale_radio.grid(row=3, column=c, sticky=W)
#		
#	if i + 2 == 5 or i + 2 == 6 or i + 2 == 7:
#		scytale_radio = Radiobutton(scytale_frame, text=i + 2, variable=pr, value=i)
#		scytale_radio.bind('<Button-1>', scytaleshift)
#		for c in range(0, 3):
#			scytale_radio.grid(row=4, column=c, sticky=W)
#		
#	if i + 2 == 8 or i + 2 == 9 or i + 2 == 10:
#		scytale_radio = Radiobutton(scytale_frame, text=i + 2, variable=pr, value=i)
#		scytale_radio.bind('<Button-1>', scytaleshift)
#		for c in range(0, 3):
#			scytale_radio.grid(row=5, column=c, sticky=W)
#	
#	if i + 2 == 11 or i + 2 == 12 or i + 2 == 13:
#		scytale_radio = Radiobutton(scytale_frame, text=i + 2, variable=pr, value=i)
#		scytale_radio.bind('<Button-1>', scytaleshift)
#		for c in range(0, 3):
#			scytale_radio.grid(row=6, column=c, sticky=W)
#		
#	if i + 2 == 14 or i + 2 == 15 or i + 2 == 16:
#		scytale_radio = Radiobutton(scytale_frame, text=i + 2, variable=pr, value=i)
#		scytale_radio.bind('<Button-1>', scytaleshift)
#		for c in range(0, 3):
#			scytale_radio.grid(row=6, column=c, sticky=W)

###Create square shift and Key tool

#####
###Create substitution toolbox
#####
sub_toolbox = Frame(window_frame, height=200, width=892, bd=2, relief=RIDGE)
#sub_toolbox.grid(row=1, columnspan=2, sticky=NW)




#####
###Create Caesar Shift Tool
#####
mono_font = tkFont.Font(family='Ubuntu Mono')

###Create slider frame
caesar_frame = Frame(sub_toolbox, width=300, bd=2, relief=RIDGE)
caesar_frame.bind('<Button-4>', scaleforward)
caesar_frame.bind('<Button-5>', scaleback)
caesar_frame.pack(side=LEFT, fill=Y)

###Create caesar shift title
caesar_label = Label(caesar_frame, text='Caesar Shift', width=26, relief=RAISED)
caesar_label.grid(row=0, column=0)

###Create caesar spacer label
caesar_spacer = Label(caesar_frame, text='Original = Red : Encoded = Blue ', width=26)
caesar_spacer.grid(row=1, column=0)

###Create ceaser scale
caesar_sub = Scale(caesar_frame, from_=0, to=25, orient=HORIZONTAL, tickinterval=13, length=210, command=caesarshift)
caesar_sub.bind('<Button-4>', scaleforward)
caesar_sub.bind('<Button-5>', scaleback)
caesar_sub.grid(row=2, column=0)

###Create alphabetical 'original' letter label
letters_scale = Label(caesar_frame, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=mono_font, fg='blue', width=26)
letters_scale.bind('<Button-4>', scaleforward)
letters_scale.bind('<Button-5>', scaleback)
letters_scale.grid(row=3, column=0)

###Create caesar shifted 'encoded' letter label
change_scale = Label(caesar_frame, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=mono_font, fg='red', width=26)
change_scale.bind('<Button-4>', scaleforward)
change_scale.bind('<Button-5>', scaleback)
change_scale.grid(row=4, column=0)

#####
#Create monoalpha substitution tool
#####

###Create monoalpha substitution frame
monoalpha_frame = Frame(sub_toolbox, bd=2, relief=RIDGE)
monoalpha_frame.pack(side=LEFT, fill=Y)

###Create monoalpha substitution title
monoalpha_frame_label = Label(monoalpha_frame, text='Monoalphabetic Cipher', width=26, relief=RAISED)
monoalpha_frame_label.grid(row=0, column=0)

se = StringVar()
monoalpha_entry = Entry(monoalpha_frame, width=26, font=mono_font, textvariable=se)
monoalpha_entry.bind('<Return>', monoalphatext)
monoalpha_entry.bind('<KeyRelease>', monoalphacaps)
monoalpha_entry.bind('<BackSpace>', monoalphaclear)
monoalpha_entry.grid(row=2, column=0)

monoalpha_old = Label(monoalpha_frame, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=mono_font, fg='red', width=26)
monoalpha_old.grid(row=3, column=0)

monoalpha_new = Label(monoalpha_frame, text='', font=mono_font, fg='blue', width=26)
monoalpha_new.grid(row=4, column=0)

monoalpha_freq = Label(monoalpha_frame, text='English Frequency Analysis Shift', relief=RAISED, width=26)
monoalpha_freq.grid(row=5, column=0)

monoalpha_freq_old = Label(monoalpha_frame, text='', font=mono_font, fg='blue')
monoalpha_freq_old.bind('<Button-1>', monoalphafreq)
monoalpha_freq_old.grid(row=6, column=0)

monoalpha_freq_new = Label(monoalpha_frame, text='', font=mono_font, fg='red')
monoalpha_freq_new.bind('<Button-1>', monoalphafreq)
monoalpha_freq_new.grid(row=7, column=0)

#####
###Create statistical analysis toolbox
#####
stats_toolbox = Frame(window_frame, height=200, width=892, bd=2, relief=RIDGE)
#stats_toolbox.grid(row=1, columnspan=2, sticky=NW)

###Create Status Bar
status = StatusBar(root)
status.pack(side=BOTTOM, fill=X)

#####
###Create top level windows here
#####



root.mainloop()
