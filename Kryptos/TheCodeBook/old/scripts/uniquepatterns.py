#/usr/bin/python
import string

###Open Input File
inputfile = 'double_letter_word_list.txt' #Change This
old_text = open(inputfile, 'r').read()
encoding = open(inputfile).encoding

###Uncomment if text has punctuation
#for x in string.punctuation: 
#	old_text = old_text.replace(x, '')
	
###Uncomment if text has numbers
#for x in string.digits:
#	old_text = old_text.replace(x, '')
	
###Uncomment if text isn't UTF-8
#old_text = (unicode(old_text, encoding).encode('utf-8'))

###Open output file
outputfile = 'INSERT NEW TEXT FILE NAME HERE' #Change This
new_text =  open(outputfile, 'w')

###Create some dictionaries and lists
new_dict = {}
new_word_list = []
old_text = old_text.upper()
word_list = old_text.split(None)

###Check for Unique Letters in each word
for word in word_list:
	###Create start definitions and a counter to use for each word
	counter = 0
	newword = ''
	let_count = {}
	let = []
	
	###Create list of letters
	for c in string.uppercase:
		let.append(c)	
	
	###Process Unique Characters into Words
	for l in word:
		
		###Count Unique Letters
		try:
			counter += 1
			let_count[(let.pop(let.index(l)))] = counter
			newword = newword + str(let_count[l])
		
		###Except for Used Letter	
		except ValueError:
			newword = newword + str(let_count[l])
			counter = counter - 1		
	
	###Add new dictionary entry {'word': 'uniquepattern'}		
	new_dict[word] = newword
	
	###Create new list of unique patterns
	new_word_list.append(newword)

###Combine word and unique pattern lists
for e in sorted(new_dict):
	new_text.write(e + ' ' + new_dict[e] + '\n')
	print e, new_dict[e]
