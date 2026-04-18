
#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

from PyQt5.QtWidgets import QSystemTrayIcon, QAction, qApp, QMenu
from PyQt5.QtGui import QIcon



class SystemTrayIcon(QSystemTrayIcon):

	def __init__(self, icon, parent=None):
		super(SystemTrayIcon, self).__init__(parent)

		self.Ptolemy = parent
		print("SYSTEM TRAY ICON PARENT: ", self.Ptolemy)

		self.exitAction = QAction(QIcon('/home/rendier/Ptolemy/images/Phaleron/power.svg'), 'Exit', self)
		self.exitAction.setToolTip('Exit Ptolemy')
		self.exitAction.triggered.connect(qApp.quit)
		self.hideAction = QAction(QIcon('/home/rendier/Ptolemy/images/Phaleron/none.png'), "Hide", self)
		self.hideAction.setToolTip('Hide Application')
		self.hideAction.triggered.connect(self.Ptolemy.hideShow)
		self.showAction = QAction(QIcon('/home/rendier/Ptolemy/images/Phaleron/none.png'), "Show", self)
		self.showAction.setToolTip('Show Application')
		self.showAction.triggered.connect(self.Ptolemy.hideShow)
		self.menu = QMenu(parent)
		self.menu.addAction(self.exitAction)
		self.menu.addSeparator()
		self.menu.addSeparator()
		self.menu.addAction(self.hideAction)
		self.setContextMenu(self.menu)