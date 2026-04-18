#/usr/bin/python

#Playfair Matrix
[
['A', 'B', 'C', 'D', 'E'], 
['F', 'G', 'H', 'I', 'K'], 
['L', 'M', 'N', 'O', 'P'], 
['Q', 'R', 'S', 'T', 'U'], 
['V', 'W', 'X', 'Y', 'Z']
]

#split _list_ into _matrix_ with row length _l_
_matrix_ = [ _list_[i*_l_: (i+1)*_l_] for i in range(_l_) ]

#split _string_ into _list_ grouped into _l_ letters		
_list_ = [_string_[i:i+_l_] for i in range(0, len(_string_), _l_)]

#convert _list_ to upper/lower case _LIST_
_LIST_ = [i.upper() for i in _list_]

#create _matrix_ with height _h_ and width _w_
_matrix_ = [ [ [] for h in range(_h_)] for w in range(_w_) ]

#display function code ONLY IF FROM FILE
import inspect
for i in (inspect.getsourcelines(inspect.getsourcelines))[0]: print i

#instantiate classes
def __init__(self):
	
	con = math2.con()
	misc = math2.misc()
	circles = math2.circles()
	fractions = math2.fractions()
	polynom = math2.polynom()
	stats = math2.stats()
	area = math2.area()
	volume = math2.volume()
	surfacearea = math2.surfacearea()
	perimeter = math2.perimeter()
	generators = math2.generators()
	fractals = math2.fractals()


graphicsView.mapToScene( graphicsView.viewport()->rect().center() )
