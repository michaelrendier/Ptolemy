#!/usr/bin/python
##yyyyyyyyyyybcghlllmppprrrsssssttt
import itertools
import pprint

strin = "yyyyyyyyyyybcghlllmppprrrsssssttt"
strfil = open('puzzle2.txt', 'w')
strlst = list(map("".join, itertools.permutations(strin)))
strfil.write(str(strlst))
strfil.close()
