#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKit import *
from PyQt5.QtMultimedia import *



import sys, os



class Earth(QGraphicsItem):
	
	def __init__(self, parent=None):
		super(Earth, self).__init__(parent)
		QGraphicsItem.__init__(self)
		
		self.Ptolemy = parent
		print("EARTH PARENT: ", self.Ptolemy)
		
		
		
	def __del__(self):
		
		pass
	
	def initUi(self):
		
		pass
	
	def paint(self, painter)