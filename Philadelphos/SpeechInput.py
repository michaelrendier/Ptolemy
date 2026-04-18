#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'rendier'

"""
https://realpython.com/python-speech-recognition/
http://jrmeyer.github.io/asr/2016/01/09/Installing-CMU-Sphinx-on-Ubuntu.html
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKit import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import speech_recognition as sr


sr.__version__
r = sr.Recognizer()
dataclip = sr.AudioFile('demo3.wav')
with dataclip as source:
	audio = r.record(source)
	
r.recognize_sphinx(audio)
mic = sr.Microphone()

class SpeechInput(QAudioRecorder):
	
	def __init__(self, parent=None):
		super(SpeechInput, self).__init__(parent)
		QAudioRecorder.__init__(self)
		
		pass
	
	def intervalLCD(self):
		"""
		Start the interval timer
		"""
		QSound.play("ding.mp3")
		# QSound("ding.mp3").play()
		# QSound.play("./audio/ding.mp3")
		# QSound.play("a.mp3")
		# QSound.play("./a.mp3")
		self.minutes = 4
		self.timer.singleShot(1000, self.updateLCD)


