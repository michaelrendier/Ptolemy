#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

# print(dir(Pharos))

from Callimachus.Database import Database
from Pharos.Dialogs import Dialogs
from Pharos.SystemTrayIcon import SystemTrayIcon
from Pharos.Philadelphos.CommandInput import Command
from Pharos.Interface import User
from Pharos.UtilityFunctions import cmdline
from Pharos.Menu import Menu
from Phaleron.APISniff.CodeBrowser import CodeBrowser



from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *

from subprocess import Popen, PIPE, call
from urllib.request import build_opener
from formlayout import fedit
from PIL import Image, ImageQt

import sys, os, time, inspect

# current = dir()

class Ui_MainWindow(object):

	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.setWindowTitle(
			QApplication.translate("MainWindow", "Πτολεμαῖος Φιλάδελφος", None))
		brush = QBrush(QColor('black'))
		brush.setStyle(Qt.SolidPattern)
		screen = QDesktopWidget().screenGeometry()
		self.Form = QWidget(MainWindow)
		self.Form.setObjectName("Main Window")
		self.Form.setContentsMargins(0, 0, 0, 0)
		self.view = QGraphicsView(self.Form)
		self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setContentsMargins(0, 0, 0, 0)
		self.view.setMouseTracking = True
		self.view.setInteractive(True)

		self.view._zoom = 0
		self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
		self.view.setFrameShape(QFrame.NoFrame)
		self.view.setBackgroundBrush(brush)
		self.view.setObjectName("The Show")

		MainWindow.setGeometry(screen)
		self.Form.setGeometry(screen)
		self.view.setGeometry(screen)

		MainWindow.setCentralWidget(self.Form)
		self.retranslateUi(MainWindow)
		QMetaObject.connectSlotsByName(MainWindow)

		self.layout = QGridLayout(self.Form)
		# self.layout.addItem(self, 0, 0, 1, 1)
		# self.layout.setMargin(0)
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)

	def retranslateUi(self, MainWindow):

		pass

	def wheelEvent(self, event):
		pass

class Ptolemy(QMainWindow):

	def __init__(self, current, parent=None):
		super(Ptolemy, self).__init__(parent)
		QMainWindow.__init__(self)

		# This is always the same
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		# Flags
		# self.CONTEXT_MENU = False


		# Ptolemy Variables
		self.homeDir = "/home/rendier/Ptolemy/"
		self.mediaDir = self.homeDir + 'media/'
		self.imgDir = self.homeDir + 'images/'
		self.pharosImg = self.imgDir + 'Pharos/'
		self.screen = QDesktopWidget().screenGeometry()

		# self.currentDir = currentDir
		# print("DIR : " + str(currentDir))

		# Scene
		self.scene = QGraphicsScene(0, 0, self.screen.width(), self.screen.height())
		self.ui.view.setScene(self.scene)


		# Modules
		self.db = Database(parent=self)
		self.dialogs = Dialogs(parent=self)
		# print(self.dialogs)
		self.opener = build_opener()
		self.opener.addheaders = [("User-agent", "Mozilla/5.0 (X11; Linux x86_64)"), ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"), ("Accept_encoding", "gzip, deflate, br"), ("Accept_language", "en-US,en;q=0.9"), ("Upgrade_insecure_requests", "1")]
		self.sysTrayIcon = SystemTrayIcon(QIcon(self.imgDir + 'Pharos/indicator-ball.gif'), parent=self)
		self.sysTrayIcon.show()
		
		# Identity
		self.name = "Πτολεμαῖος Φιλάδελφος"
		self.user = Popen('whoami', stdout=PIPE, shell=True).communicate()[0][0:-1]
		self.platform = Popen('uname -o', stdout=PIPE, shell=True).communicate()[0][0:-1]
		self.nodename = Popen('uname -n', stdout=PIPE, shell=True).communicate()[0][0:-1]

		self.stylesheet = "QMainWindow { border: 1px solid white; background-color: black; color: white } " \
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

		# # Window Vars
		# self.windowlist = []
		# self.windowcounter = 0
		#
		# # Taskbar Vars
		# self.tasklist = []
		# self.taskwin = {}
		#
		# Command History
		self.cmdhistory = []

		# ~ self.ui.view.setViewport(QtOpenGL.QGLWidget())###Could Not Create Shader TODO

		self.GLFonts = [
			'GLUT_BITMAP_8_BY_13',
			'GLUT_BITMAP_9_BY_15',
			'GLUT_BITMAP_TIMES_ROMAN_10',
			'GLUT_BITMAP_HELVETICA_10',
			'GLUT_BITMAP_HELVETICA_12'
		]
		self.colors = [(r, g, b) for r in (0, 1) for g in (0, 1) for b in (0, 1)]

		self.initUI()

	def __del__(self):

		# self.Search.deleteLater()

		# Restore sys.stdout
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__
		pass

	def closeEvent(self, a0: QCloseEvent):

		exit()
		pass


	def initUI(self):

		w = self.screen.width()
		h = self.screen.height()

		# Create Groups
		# self.taskbarg = self.scene.createItemGroup([])
		# self.taskbarg.setAcceptHoverEvents(True)


		# Build GUI
		
		
		self.Philadelphos = Command(self)
		self.scene.addWidget(self.Philadelphos)


		
		# self.Philadelphos_thread = WorkThread(self, 1, None)
		# self.Philadelphos_thread.workFinished.connect(self.dialogs.infoBox)
		# self.Philadelphos_thread.start()

		self.Menu = Menu(parent=self)
		self.scene.addWidget(self.Menu)

		self.Interface = User(self)
		self.scene.addWidget(self.Interface)
	
		# self.Keyboard = VirtualKeys(parent=self)
		# self.scene.addWidget(self.Keyboard)
	
		# self.lookatme = CodeBrowser(dir(self))#current) # Fix using browser todo
		
		# QSound.play('/home/rendier/Ptolemy/Pharos/audio/demo3.wav')

		

		# self.Search = Phaleron.TreasureHunt.Main(self)
		# self.Search.show()



		# self.WindowManager = WindowManager(parent=self)

		# System Tray Icon

        # self.attempt1 = self.scene.addEllipse(self.Interface.UserDisplay.boundingRect(), QPen(Qt.red), QBrush(Qt.green))
        # self.Interface.
		# rect, text, call, tooltip, parent
		# test = PButton((self.screen.width() / 2, self.screen.height() / 2, 150, 25), 'testthis', self.scrollMenu,
		#                'test button', self)
		# self.scene.addItem(test)

		# self.desktop = self.scene.addRect(254, 0, w - 189, h - 50, self.pen('white', 1),
		#                                   self.brush('black'))  # set 254 to 127 TODO

		# self.taskbar = self.scene.addRect(w - 62, 0, 62, h - 50, self.pen('white', 1), self.brush('black'))

	# GLTry = GLWindow()

	# Base level functions
	def openSearch(self, event):
		cmdline('cd /home/rendier/Ptolemy/Phaleron/TreasureHunt && python3 TreasureHunt.py')
		
	
		# from Phaleron.TreasureHunt.TreasureHunt import TreasureHunt
		# self.Search = TreasureHunt(self)
		# self.Search.show()

	def openNavigation(self, event):
		from Anaximander.Navigation import Navigation
		self.Navigation = Navigation(self)
		self.Navigation.show()

	def openCore(self, event):
		from Mouseion.GLViewer import Viewer
		from Alexandria.Core import Core
		self.Core = Viewer(Core, self)
		# self.Core.show()

	def openEarth(self, event):
		from Mouseion.GLViewer import Viewer
		from Alexandria.Earth import Earth
		self.Earth = Viewer(Earth, rotate=True, parent=self)
		# self.Earth.show()

	def openGraphPlot(self, event):
		from Archimedes.Maths.GraphPlot import GraphPlot
		dataList = [('Equation', '')]
		title = 'GraphPlot Hungry'
		comment = 'Please enter equation'
		results = fedit(dataList, title, comment)
		print("RESULTS: ", results[0].split(", "))
		equation = results[0].split(", ")

		self.GraphPlot = GraphPlot(equation)

	def openStanDev(self, event):
		pass

	def openDbCPanel(self, event):
		from Callimachus.DBControlPanel import DBControlPanel
		self.dbCPanel = DBControlPanel(self)
		self.dbCPanel.show()
	
	def openNotepad(self):
		from Phaleron.Notepad import Notepad
		self.notepad = Notepad(self)
		self.notepad.show()
	
	def openWikiGroup(self, event):
		from Mouseion.WikiGroup import WikiGroup
		self.wikiGroup = WikiGroup(self)
		self.wikiGroup.show()

	def openLibrary(self, event):
		from Mouseion.Library import Library
		self.library = Library(self)
		self.library.show()
	
	def testing(self):
		
		self.Philadelphos.setOutput('inside the test subject')
		
		if self.CommandGroup.handlesChildEvents == False:
			self.CommandGroup.setHandlesChildEvents(True)
		
		else:
			self.CommandGroup.setHandlesChildEvents(False)
	
	def volume(self, event):

		if event.delta() > 0 and event.pos() in self.soundrect:
			self.output("volume up", 'red')
			call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
			pass

		elif event.delta() < 0 and event.pos() in self.soundrect:
			self.output('volume down', 'red')
			call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
			pass

		pass

	def pen(self, color, width=1):

		pen = QPen(QColor(color))
		pen.setWidth(width)
		pen.setCapStyle(Qt.FlatCap)
		return pen

	def brush(self, color):

		return QBrush(QColor(color))

	def color(self, color):

		return QColor(color)

	def font(self, size=10):

		return QFont('Ubuntu Mono', size)

	def cwd(self):

		return os.getcwd()

	def sysDate(self):

		return "{0}.{1}.{2}".format(
			"%02d" % time.localtime()[2],
			"%02d" % time.localtime()[1],
			str(time.localtime()[0])[2:]
		)

	def sysTime(self):

		return "{0}:{1}:{2}".format(
			"%02d" % time.localtime()[3],
			"%02d" % time.localtime()[4],
			"%02d" % time.localtime()[5]
		)

	def sysYear(self):

		return "{0}.{1}.{2}".format(
			time.localtime()[6],
			time.localtime()[7],
			time.localtime()[8]
		)

	def timeStamp(self):

		return [self.sysDate(), self.sysTime(), self.sysYear()]

	def hideShow(self):

		if self.isVisible():
			self.hide()
			self.Search.hide()
			self.sysTrayIcon.menu.removeAction(self.sysTrayIcon.hideAction)
			self.sysTrayIcon.menu.addAction(self.sysTrayIcon.showAction)
		else:
			self.show()
			self.Search.show()

		pass

	def cronJob(self, interval, job):

		self.cron = QTimer(self)
		self.cron.setInterval(interval)
		try:
			self.cron.timeout.connect(job)

		except TypeError:
			pass
		self.cron.start()

	def timedJob(self, timer, job):

		self.timer = QTimer(self)
		self.timer.timeout.connect(job)
		self.timer.start(timer)

		pass

	def codeReload(self, module, option):

		# fix for reload all code or just single module
		# make text editor that live reloads any code worked on with syntax hilighter
		pass

	def pixmap(self, imgpath, size=None):  # TODO

		# img = Image.open(imgpath)
		# enhancer = ImageEnhance.Brightness(img)
		#
		# # self.scene.clear()
		# w, h = img.size
		# imgQ = ImageQt.ImageQt(img)  # we need to hold reference to imgQ, or it will crash
		pixMap = QPixmap(imgpath).scaled(size[0], size[1])  # .fromImage(imgQ)
		# if size:
		# 	pixMap
		# self.scene.addPixmap(pixMap)

		return pixMap

	def image(self, imgpath):

		img = Image.open(imgpath)
		imgQ = ImageQt.ImageQt(img)
		imgout = QImage(imgQ)
		return imgout

	def icon(self, imgpath):

		icon = QIcon(imgpath)
		return icon

	def svg(self, painter, imgpath, QRectF):

		QSvgRenderer(imgpath).render(painter, QRectF)

	# def arc(self, painter, rect, radius, start_angle, sweep_angle):
	# 	dbprint('Main.arc', self)
	#
	# 	self.rect = rect
	# 	self.radius = radius
	# 	self.arcRect = QRectF(
	# 		self.rect.x() + 75 - radius,
	# 		self.rect.y() + 75 - radius,
	# 		2 * radius,
	# 		2 * radius
	# 	)
	#
	# 	start_angle *= 16
	# 	sweep_angle *= 16
	#
	# 	painter.drawArc(self.arcRect, start_angle, sweep_angle)

	# Event Handlers *MAKE EVENT HANDLER CLASS* TODO
	def keyPressEvent(self, event):

		if event.key() == Qt.Key_Escape:
			pass

		pass

	def mousePressEvent(self, event):

		outputObject = str(str(self.ui.view.itemAt(event.x(), event.y()))[1:-1].split(" ")[:-2])
		outputObject = str(self.ui.view.itemAt(event.x(), event.y()))
		try:
			outputParent = str(str(self.ui.view.itemAt(event.x(), event.y()).parent)[1:-1].split(" ")[:-2])
			objectName = str(str(self.ui.view.itemAt(event.x(), event.y()).__name__))
			self.Philadelphos.setOutput(outputObject + outputParent + " Name is: " + objectName, speak=True)

		except AttributeError:
			self.Philadelphos.setOutput(outputObject + " : No Parent", speak=True)
		# print("DIR OF CLICKED OBJECT : " + str(dir(self.ui.view.itemAt(event.x(), event.y()))))

		self.aniclick(event)


		# Left Click
		if event.button() == Qt.LeftButton:

			pass

		# Right click
		elif event.button() == Qt.RightButton:

			pass

		# Middle Click
		elif event.button() == Qt.MiddleButton:  #####

			pass

		# QGraphicsScene.mousePressEvent(self, event)

	def mouseMoveEvent(self, event):  #

		# self.time
		# if self.Win.restrict.contains(event.scenePos()):#event.x(), event.y()):
		# 	QtGui.QGraphicsItem.mouseMoveEvent(self, event)
		# #Left Button Drag
		# if event.button() == QtCore.Qt.LeftButton:
		# 	self.setOutput(str(self.scene.itemAt(event.x(), event.y()).__name__))

		QMainWindow.mouseMoveEvent(self, event)
		pass

	def wheelEvent(self, event):

		# scale = pow(2, -(event.delta() / 240))
		# # scale = 2 ** -event.delta() / 240.0
		# self.scaleView(scale)

		# if event.delta() > 0:
		# 	factor = 2
		# 	self.ui.view._zoom += 1
		# 	self.ui.view.scale(factor, factor)
		#
		# elif event.delta() < 0:
		# 	factor = 1/2
		# 	self.ui.view._zoom -= 1
		# 	self.ui.view.scale(factor, factor)

		# self.ui.view.wheelEvent(event)
		pass

	def resizeEvent(self, event):

		pass

	def scaleView(self, scalefactor):

		# factor = numpy.matrix().scale(scalefactor, scalefactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
		# if factor < 0.07 or factor >100:
		#
		# 	return

		self.ui.view.scale(scalefactor, scalefactor)
		pass

	# Functions
	def inputBox(self, x, y, ltext, textc, penc, brushc):

		if self.inboxnum == []:
			self.inboxnum.append('1')
		else:
			self.inboxnum.append(1 + len(self.inboxnum))

		box = QGraphicsRectItem(x, y, 150, 25)
		box.setPen(self.pen(penc, 1))

		inlbl = QLabel(self)
		inlbl.setText(str(self.inboxnum[-1]) + ') ' + ltext)
		inlbl.setStyleSheet(self.stylesheet)
		inlbl.resize(75, 25)
		inlbl.move(x + 5, y)

		inedit = QLineEdit(self)
		inedit.setStyleSheet(self.stylesheet)
		inedit.resize(50, 23)
		inedit.move(x + 75, y + 1)

		okbtn = QPushButton('OK', self)
		okbtn.setStyleSheet(self.stylesheet)
		okbtn.resize(23, 23)
		okbtn.move(x + 127, y + 2)

	def scrollMenu(self):

		pass

	def aniclick(self, event):  #

		brush = QBrush()
		brush.setColor(QColor('black'))
		pen = QPen()
		pen.setColor(QColor('white'))
		pen.setWidth(2)
		# print('animated click')
		c1 = self.scene.addEllipse(event.x() - 10, event.y() - 10, 20, 20, pen, brush)
		# time.sleep(0.5)
		c2 = self.scene.addEllipse(event.x() - 15, event.y() - 15, 30, 30, pen, brush)
		# self.scene.removeItem(c1)
		# time.sleep(0.5)
		c3 = self.scene.addEllipse(event.x() - 20, event.y() - 20, 40, 40, pen, brush)
		self.scene.removeItem(c2)
		# time.sleep(0.5)
		c4 = self.scene.addEllipse(event.x() - 25, event.y() - 25, 50, 50, pen, brush)
		# self.scene.removeItem(c3)
		# time.sleep(0.5)
		c5 = self.scene.addEllipse(event.x() - 30, event.y() - 30, 60, 60, pen, brush)
		self.scene.removeItem(c4)
		# time.sleep(0.5)
		# self.scene.removeItem(c5)
		# print('done')

	# ADD PARENT TO THIS FUNCTION IN MATH2 TODO
	def countvar(self, parent=None):

		vc = 0
		iv = 0
		blist = []

		# ~ print alist
		# ~ for i in alist:
		# ~ print i
		# ~ if type(i) == str:
		# ~ vc += 1
		# ~ print vc

		# blist = locals().values()
		# print blist
		alist = inspect.getfullargspec(parent)
		print(alist.args)
		# ~ for i in range(len(alist.args)):
		# ~ print 'i =', i
		# ~ item = 'iv = '+ str(method.__module__) + '.' + str(method.__name__) + '.' + alist.args[i]
		# ~ print item
		# ~ exec item
		# ~ blist.append(iv)
		# ~ if type(iv) is str:
		# ~ vc += 1
		print(vc, blist)
		return vc

def main():

	app = QApplication(sys.argv)
	app.setApplicationName('Ptolemy II')
	# sys.setrecursionlimit(10000)
	Ptol = Ptolemy(current)

	Ptol.setWindowIcon(QIcon('/home/rendier/Ptolemy/images/ptol.svg'))
	# Ptolemy.setWindowFlags(Ptolemy.windowFlags() | Qt.FramelessWindowHint)
	# Ptolemy.setWindowState(Qt.WindowMaximized)
	# Ptolemy.setWindowState(QtCore.Qt.WindowFullScreen)
	Ptol.show()
	# sys.stdout = OutLog(Ptolemy.Philadelphos.PtolOut, color='white')
	# sys.stderr = OutLog(Ptolemy.Philadelphos.PtolOut, color='red')

	# It's exec_ because exec is a reserved word in Python
	sys.exit(app.exec_())

current=dir()

if __name__ == "__main__":
	main()