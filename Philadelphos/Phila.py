#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

from chatterbot import ChatBot
from chatterbot.trainers import UbuntuCorpusTrainer, ChatterBotCorpusTrainer


Ptol = ChatBot(
	name='Ptolemy',
	storage_adapter='chatterbot.storage.SQLStorageAdapter',
	preprocessors=[
		'chatterbot.preprocessors.clean_whitespace',
		'chatterbot.preprocessors.unescape_html',
		'chatterbot.preprocessors.convert_to_ascii'
	],
	logic_adapters=[
		'chatterbot.logic.MathematicalEvaluation',
		'chatterbot.logic.TimeLogicAdapter',
		'chatterbot.logic.BestMatch'
	],
	# database_uri='mysql://phpmyadmin:SriLanka65@localhost/Philadelphos'
	database_uri='sqlite:///Ptol.db'
)

# Utrainer = UbuntuCorpusTrainer(Ptol)
# Utrainer.train()
#
# Ctrainer = ChatterBotCorpusTrainer(Ptol)
# Ctrainer.train('chatterbot.corpus.english')



RUN_FLAG = True

while RUN_FLAG:
	try:
		the_input = input("   User:> ")
		if the_input.lower() == 'quit':
			print("Quitting Chat Session")
			RUN_FLAG = False
			
		else:
			bot_input = Ptol.get_response(the_input)
			print("Ptolemy:>", bot_input)
		
		
	except(KeyboardInterrupt, EOFError, SystemExit):
		break

