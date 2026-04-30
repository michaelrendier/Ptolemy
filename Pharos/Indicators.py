#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *

class ThreadIndicator(QGraphicsItem):
	"""Thread Indicator
	geometry: [x, y, width, height]
	"""
	
	def __init__(self, geometry, parent=None):
		super(ThreadIndicator, self).__init__(parent)
		
		self.parent = parent
		print("INDICATOR PARENT:", self.parent)
		
		self.geometry = geometry
		
	
	def paint(self, painter, option, widget):
		
  # TODO:SETTINGS — hardcoded path, use PTOL_ROOT
		self.indicator = QIcon(PTOL_ROOT + "/images/Pharos/indicator-ball.png", parent=self)
		
	