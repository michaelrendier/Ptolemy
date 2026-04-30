#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *

from subprocess import Popen, PIPE, call

from Pharos.Dialogs import Dialogs
from Callimachus.Database import Database

import sys
from matplotlib import pyplot as ptl
from Pharos.PtolFace import PtolFace


class DBControlPanel(QMainWindow, PtolFace):
	
	def __init__(self, parent=None):
		super(DBControlPanel, self).__init__(parent)
		QMainWindow.__init__(self)
		
		self.setWindowTitle('Callimachus DB CPanel - Ptolemy')
		
		if parent:
			self.Ptolemy = parent
			print("DBCONTROLPANEL PARENT: ", self.Ptolemy)
			self.imageDir = self.Ptolemy.imgDir + 'Callimachus/'
			self.styles = self.Ptolemy.stylesheet
			self.dialogs = self.Ptolemy.dialogs
			self.database = self.Ptolemy.db
			
		else:
   # TODO:SETTINGS — hardcoded path, use PTOL_ROOT
			self.imageDir = PTOL_ROOT + '/images/Callimachus/'
			self.styles = "QMainWindow { border: 1px solid white; background-color: black; color: white } " \
						  "QWidget { background-color: black; color: white } " \
						  "QMenuBar { border: 1px solid white; background-color: black; color: white } " \
						  "QMenuBar::item { background-color: black; color: white } " \
						  "QToolBar { border: 1px solid white; background-color: black; color: white } " \
						  "QToolButton { background-color: black; color: white } " \
						  "QToolButton::hover { background-color: blue; color: white } " \
						  "QStatusBar { border: 1px solid white; background-color: black; color: white } " \
						  "QTabWidget { border: 1px solid white; background-color: black; color: white } " \
						  "QTabBar::tab { border: 1px solid white; background-color: black; color: white } " \
						  "QWebView { border: 1px solid white; background-color: white; color: black } " \
						  "QComboBox { border: 1px solid white; background-color: grey; color: black } " \
						  "QComboBox::item { background-color: grey; color: black } " \
						  "QPushButton { border: 1px solid white; background-color: black; color: white } " \
						  "QPushButton::hover {border: 1px solid blue } " \
						  "QLineEdit { border: 1px solid white; background-color: grey; color: black } " \
						  "QDockWidget { border: 1px solid white; background-color: black; color: white } " \
						  "QTableWidget { background-color: white; color: black } " \
						  "QTextBrowser { border: 1px solid black; background-color: white; color: black } " \
						  "QLabel {border: 0px } " \
						  "QListWidget { background-color: grey; color: black } " \
						  "QListWidgetItem { border: 1px solid black } " \
						  "QTableWidget { background-color: black; color: white } " \
						  "QTableWidget::item:focus { border: 1px solid white; background-color: blue; color: white } " \
						  "QHeaderView::section { background-color: darkblue; color: white }"
			self.dialogs = Dialogs(self)
			self.database = Database(self)
			
		self.setStyleSheet(self.styles)
		self.btnSize = 32
		
		
		
		
		self.initUi()
		
	def __del__(self):
		
		pass
	
	def initUi(self):
		
		self.widget = QWidget(self)
		self.setCentralWidget(self.widget)
		self.layout = QGridLayout(self)
		
		self.sectionBtn = QSvgWidget(self.imageDir + 'section.svg')
		self.sectionBtn.setFixedSize(self.btnSize, self.btnSize)
		self.sectionBtn.setToolTip('Add Section')
		self.sectionBtn.mousePressEvent = self.dialogs.addSectionBox
		
		self.noteBtn = QSvgWidget(self.imageDir + 'notepad.svg')
		self.noteBtn.setFixedSize(self.btnSize, self.btnSize)
		self.noteBtn.setToolTip('Add Note')
		self.noteBtn.mousePressEvent = self.dialogs.addNoteBox
		
		self.categoryBtn = QSvgWidget(self.imageDir + 'category.svg')
		self.categoryBtn.setFixedSize(self.btnSize, self.btnSize)
		self.categoryBtn.setToolTip('Add Category')
		self.categoryBtn.mousePressEvent = self.dialogs.addCategoryBox
		
		self.dependencyPtolBtn = QSvgWidget(self.imageDir + 'ptolemydependency.svg')
		self.dependencyPtolBtn.setFixedSize(self.btnSize, self.btnSize)
		self.dependencyPtolBtn.setToolTip('Add Ptolemy Dependency')
		self.dependencyPtolBtn.mousePressEvent = self.dialogs.addPtolDependencyBox
		
		self.dependencyServerBtn = QSvgWidget(self.imageDir + 'serverdependency.svg')
		self.dependencyServerBtn.setFixedSize(self.btnSize, self.btnSize)
		self.dependencyServerBtn.setToolTip('Add Server Dependency')
		self.dependencyServerBtn.mousePressEvent = self.dialogs.addServerDependencyBox
		
		self.recipeBtn = QSvgWidget(self.imageDir + 'recipe.svg')
		self.recipeBtn.setFixedSize(self.btnSize, self.btnSize)
		self.recipeBtn.setToolTip('Add New Recipe')
		self.recipeBtn.mousePressEvent = self.dialogs.addRecipe
		
		self.archiveBtn = QSvgWidget(self.imageDir + 'archive.svg')
		self.archiveBtn.setFixedSize(self.btnSize, self.btnSize)
		self.archiveBtn.setToolTip('Archive a URL')
		self.archiveBtn.mousePressEvent = self.dialogs.archiveArticle
		
		self.codeBtn = QSvgWidget(self.imageDir + 'codeblock.svg')
		self.codeBtn.setFixedSize(self.btnSize, self.btnSize)
		self.codeBtn.setToolTip('Add New Script')
		self.codeBtn.mousePressEvent = self.dialogs.addCode
		
		blankList = []
		for i in range(17):
			code = 'self.blankBtn{0} = QSvgWidget(self.imageDir + "blank.svg")'.format(str(i))
			exec(code)
			code = 'self.blankBtn{0}.setFixedSize(self.btnSize, self.btnSize)'.format(str(i))
			exec(code)
			code = 'blankList.append(self.blankBtn{0}'.format(str(i))
			
		
		# print("DIR: ", dir(self))
		
		
		# self.blankBtn = QSvgWidget(self.imageDir + 'blank.svg')
		# self.blankBtn.setFixedSize(self.btnSize, self.btnSize)
		
		
		self.layout.addWidget(self.noteBtn, 0, 0, 1, 1)
		self.layout.addWidget(self.dependencyPtolBtn, 0, 1, 1, 1)
		self.layout.addWidget(self.dependencyServerBtn, 0, 2, 1, 1)
		self.layout.addWidget(self.sectionBtn, 0, 3, 1, 1)
		self.layout.addWidget(self.categoryBtn, 0, 4, 1, 1)
		self.layout.addWidget(self.recipeBtn, 1, 0, 1, 1)
		self.layout.addWidget(self.archiveBtn, 1, 1, 1, 1)
		self.layout.addWidget(self.codeBtn, 1, 2, 1, 1)
		self.layout.addWidget(self.blankBtn16, 1, 3, 1, 1)
		self.layout.addWidget(self.blankBtn15, 1, 4, 1, 1)
		self.layout.addWidget(self.blankBtn14, 2, 0, 1, 1)
		self.layout.addWidget(self.blankBtn13, 2, 1, 1, 1)
		self.layout.addWidget(self.blankBtn12, 2, 2, 1, 1)
		self.layout.addWidget(self.blankBtn11, 2, 3, 1, 1)
		self.layout.addWidget(self.blankBtn10, 2, 4, 1, 1)
		self.layout.addWidget(self.blankBtn9, 3, 0, 1, 1)
		self.layout.addWidget(self.blankBtn8, 3, 1, 1, 1)
		self.layout.addWidget(self.blankBtn7, 3, 2, 1, 1)
		self.layout.addWidget(self.blankBtn6, 3, 3, 1, 1)
		self.layout.addWidget(self.blankBtn5, 3, 4, 1, 1)
		self.layout.addWidget(self.blankBtn4, 4, 0, 1, 1)
		self.layout.addWidget(self.blankBtn3, 4, 1, 1, 1)
		self.layout.addWidget(self.blankBtn2, 4, 2, 1, 1)
		self.layout.addWidget(self.blankBtn1, 4, 3, 1, 1)
		self.layout.addWidget(self.blankBtn0, 4, 4, 1, 1)
		
		
		self.widget.setLayout(self.layout)
		
		


def main():
	
	app = QApplication(sys.argv)
	app.setApplicationName('Callimachus DB CPanel - Ptolemy')
	# sys.setrecursionlimit(10000)
	CPanel = DBControlPanel()
	
 # TODO:SETTINGS — hardcoded path, use PTOL_ROOT
	CPanel.setWindowIcon(QIcon(PTOL_ROOT + '/images/ptol.svg'))
	CPanel.setWindowTitle('Callimachus DB CPanel - Ptolemy')
	CPanel.show()

	
	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()