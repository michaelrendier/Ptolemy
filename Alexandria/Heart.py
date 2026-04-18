#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'rendier'
#Builtins
from math import *
import time
import random
import os
import sys
from threading import *
from subprocess import PIPE, Popen
import hashlib
import ctypes

#OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLE import *
# import OpenGL_accelerate as glAcc
# import OpenGLContext

#Installed
import psutil
import ast
import numpy
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageTransform

# import pyopencl
# import pygame
# from pygame.locals import *

# import Earth
# from kivy.uix.slider import Slider


try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO
# -----------
# VARIABLES
# -----------
global Show

g_fViewDistance = 9.
g_Width = 600
g_Height = 600

g_nearPlane = 0.1
g_farPlane = 100.

action = ""
xStart = yStart = 0.
zoom = 20.

xRotate = 0.
yRotate = 0.
zRotate = 0.

xTrans = 0.
yTrans = 0.

colorsAll = [(r, g, b) for r in range(0, 254) for g in range(0, 254) for b in range(0, 254)]
colors = [(r, g, b) for r in (0, 1) for g in (0, 1) for b in (0, 1)]

red = (255,0,0)
darkRed = (128, 0, 0)
green = (0,255,0)
darkGreen = (0, 128, 0)
blue = (0,0,255)
cyan = (0, 255, 255)
magenta = (255, 0, 255)
yellow = (255, 255, 0)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)
grey = (79, 79, 79)

cube_nodes = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
cube_edges = ([(n, n + 4) for n in range(0, 4)] + [(n, n + 1) for n in range(0, 8, 2)] + [(n, n + 2) for n in (0, 1, 4, 5)])
cube_surfaces = []  # TODO

fonts = [GLUT_BITMAP_8_BY_13, GLUT_BITMAP_9_BY_15, GLUT_BITMAP_TIMES_ROMAN_10, GLUT_BITMAP_HELVETICA_10, GLUT_BITMAP_HELVETICA_12
]


# -------------------
# SCENE CONSTRUCTOR
# -------------------

def scenemodel():
	glRotate(90, 0., 0., 1.)
	glutSolidTeapot(1.)

def Cube(nodes, edges):
	
	surfaces = (
		(0, 1, 2, 3),
		(4, 5, 6, 7),
		(0, 1, 4, 5),
		(2, 3, 6, 7),
		(0, 2, 4, 6),
		(1, 3, 5, 7)
	)
	
	for i in cube_nodes:
		Label3d(i[0], i[1], i[2], GLUT_BITMAP_9_BY_15, "(" + str(i[0]) + "," + str(i[1]) + "," + str(i[2]) + ")", 1,
				   1, 0, 0)
	
	# glBegin(GL_QUADS)
	# for surface in surfaces:
	# 	x = 0
	# 	for vertex in surface:
	# 		x += 1
	# 		glColor3fv(colors[x], 0)
	# 		glVertex3fv(nodes[vertex])
	# glEnd()
	
	glBegin(GL_LINES)
	for edge in edges:
		for vertex in edge:
			# glColor3fv(colors[6])
			glVertex3fv(nodes[vertex])
	glEnd()

def Window():
	windowVerts = (
		(0.2, 0.2, 0),
		(0.8, 0.2, 0),
		(0.8, 0.8, 0),
		(0.2, 0.8, 0),
		(0.2, 0.5, 0),
		(0.5, 0.2, 0),
		(0.5, 0.8, 0),
		(0.8, 0.5, 0)
	)
	
	windowLines = (
		(0, 1),
		(1, 2),
		(2, 3),
		(3, 0),
		(4, 7),
		(5, 6)
	)
	# for i in windowVerts:
	# 	Label3d(i[0], i[1], i[2], GLUT_BITMAP_9_BY_15, "(" + str(i[0]) + "," + str(i[1]) + "," + str(i[2]) + ")", 1,
	# 	           1, 0, 0)
	glBegin(GL_LINES)
	for edge in windowLines:
		for vertex in edge:
			glColor3fv(colors[6])
			glVertex3fv(windowVerts[vertex])
	glEnd()

def cityGrid(xmin, xmax, dx, ymin, ymax, dy):
	for x in range(xmin, xmax +1, dx):
		for y in range(ymin, ymax + 1, dy):
			glBegin(GL_LINES)
			glVertex3f(x, ymin, 0)
			glVertex3f(x, ymax, 0)
			glVertex3f(xmin, y, 0)
			glVertex3f(xmax, y, 0)
			glEnd()
			# Label3d(0, 0, 0, GLUT_BITMAP_9_BY_15, "(0, 0, 0)")
			# Label3d(1, 1, 0, GLUT_BITMAP_9_BY_15, "(1, 1, 0)")
			
def Cylinder(x, y, z, base, top, height, slices, stacks, method=GL_FILL):
	quadratic = gluNewQuadric()
	glTranslate(x, y, z)
	gluQuadricNormals(quadratic, GLU_SMOOTH)  # Create Smooth Normals (NEW)
	gluQuadricTexture(quadratic, GL_TRUE)
	gluQuadricDrawStyle(quadratic, method)
	glColor3f(1, 0, 0)
	gluCylinder(quadratic, base, top, height, slices, stacks)
	glTranslate(-x, -y, -z)

def partialCylinder(cx, cy, cz, radius, height, start_angle, sweep_angle, sides, method=GL_TRIANGLE_STRIP):
	try:
		theta = -2.0 / (360.0 / sweep_angle) * pi / (sides)
	except ZeroDivisionError:
		theta = pi / 180
	c = cos(theta)
	s = sin(theta)
	
	x = radius * cos(start_angle * pi / 180.)
	y = radius * sin(start_angle * pi / 180.)
	
	glBegin(method)
	for i in range(sides + 1):
		glVertex3f(x + cx, y + cy, cz)
		glVertex3f(x + cx, y + cy, cz + height)
		
		t = x
		x = c * x - s * y
		y = s * t + c * y
	glEnd()
	
def partialDisk(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle, method=GL_FILL):
	quadratic = gluNewQuadric()
	glTranslate(x, y, z)
	gluQuadricNormals(quadratic, GLU_SMOOTH)  # Create Smooth Normals (NEW)
	gluQuadricTexture(quadratic, GL_TRUE)
	gluQuadricDrawStyle(quadratic, method)
	gluPartialDisk(quadratic, inner, outer, slices, loops, start_angle, sweep_angle)
	glTranslate(-x, -y, -z)

def partialCircle(cx, cy, cz, radius, start_angle, sweep_angle, sides, method=GL_LINE_STRIP):
	try:
		theta = -2.0 / (360.0 / sweep_angle) * pi / (sides)
	except ZeroDivisionError:
		theta = pi / 180
	c = cos(theta)
	s = sin(theta)

	x = radius * cos(start_angle * (pi / 180.))
	y = radius * sin(start_angle * (pi / 180.))
	
	glBegin(method)
	for i in range(sides + 1):
		glVertex3f(x + cx, y + cy, cz)
		
		t = x
		x = c * x - s * y
		y = s * t + c * y
	glEnd()

def arcCylinder(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle, height, method=GL_FILL):#ADD SIDES IN QUADS TODO
	c1 = cos((-start_angle + 90) * pi / 180)
	s1 = sin((-start_angle + 90) * pi / 180)
	c2 = cos(((-start_angle + 90) - sweep_angle) * pi / 180)
	s2 = sin(((-start_angle + 90) - sweep_angle) * pi / 180)
	quad1 = [(inner * c1, inner * s1, z),
			 (outer * c1, outer * s1, z),
			 (inner * c1, inner * s1, z + height),
			 (outer * c1, outer * s1, z + height)]
	
	quad2 = [(inner * c2, inner * s2, z),
			 (outer * c2, outer * s2, z),
			 (inner * c2, inner * s2, z + height),
			 (outer * c2, outer * s2, z + height)]
	
	glBegin(GL_TRIANGLE_STRIP)
	for i in quad1:
		glVertex3fv(i)
	glEnd()
	
	glBegin(GL_TRIANGLE_STRIP)
	for i in quad2:
		glVertex3fv(i)
	glEnd()
	
	# GLU_FILL , GLU_LINE , GLU_SILHOUETTE , and GLU_POINT
	quad = gluNewQuadric()
	glTranslatef(x, y, z)
	gluQuadricNormals(quad, GLU_SMOOTH)
	gluQuadricTexture(quad, GL_TRUE)
	gluQuadricDrawStyle(quad, method)
	gluPartialDisk(quad, inner, outer, slices, loops, start_angle, sweep_angle)
	partialCylinder(x, y, z, inner, height, -start_angle + 90, sweep_angle, slices, GL_TRIANGLE_STRIP)
	partialCylinder(x, y, z, outer, height, -start_angle + 90, sweep_angle, slices, GL_TRIANGLE_STRIP)
	glTranslatef(x, y, z + height)
	gluPartialDisk(quad, inner, outer, slices, loops, start_angle, sweep_angle)
	glTranslatef(-x, -y, -(z + height))

def Star(cx, y, cz, radius, start_angle, arc_angle, sides, method=GL_LINE_STRIP):
	theta = float(arc_angle / (sides - 1))
	tangent_factor = tan(theta)
	radial_factor = cos(theta)
	
	x = radius * cos(start_angle)
	z = radius * sin(start_angle)
	
	glBegin(method)
	for i in range(0, sides + 1):
		
		glVertex3f(x + cx, y, z + cz)
		tx = -z
		tz = x
		
		x += tx * tangent_factor
		z += tz * tangent_factor
		
		x *= radial_factor
		z *= radial_factor
		
	glEnd()
	
def Circle(cx, cy, z, radius, sides, method=GL_LINE_LOOP):
	
	theta = 2.0 * pi / sides
	c = cos(theta)
	s = sin(theta)
	
	x = radius
	y = 0
	
	glBegin(method)
	for i in range(0, sides + 1):
		glVertex3f(x + cx, y + cy, z)
		
		t = x
		x = c * x - s * y
		y = s * t + c * y
		
	
	glEnd()

def Label3d(x, y, z, text, font=GLUT_BITMAP_8_BY_13):
	blending = False
	if glIsEnabled(GL_BLEND):
		blending = True
	
	glEnable(GL_BLEND)
	glRasterPos3f(x, y, z)
	for ch in text:
		glutBitmapCharacter(font, ctypes.c_int(ord(ch)))
	
	if not blending:
		glDisable(GL_BLEND)

def cmdline(command):
	process = Popen(
		args=command,
		stdout=PIPE,
		stderr=PIPE,
		shell=True
	)
	return process.communicate()[0]

def percentarc3d(x, y, z, inner, outer, start_angle, sweep_angle, height, type, percent, method=GL_FILL, slices=36,
				 loops=36):
	"""
	type 0 = Angle
	type 1 = Height
	type 2 = Both
	:param x:
	:param y:
	:param z:
	:param inner:
	:param outer:
	:param start_angle:
	:param sweep_angle:
	:param height:
	:param type:
	:param method:
	:param slices:
	:param loops:
	:return:
	"""
	percent = int(percent) / 100.0
	
	if percent != 0:
		
		if type == 0:
			arcCylinder(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle * percent, height,
						method)
		
		elif type == 1:
			arcCylinder(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle, height * percent,
						method)
			glColor3f(1, 1, 1)
			partialDisk(x, y, z + height, inner, outer, slices, loops, start_angle, sweep_angle, GLU_SILHOUETTE)
		
		elif type == 2:
			
			arcCylinder(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle * percent, height * percent,
						method)
			glColor3f(1, 1, 1)
			partialDisk(x, y, z + height, inner, outer, slices, loops, start_angle, sweep_angle * percent,
						GLU_SILHOUETTE)
	
	glutPostRedisplay()

def ioarc3d(x, y, z, inner, outer, start_angle, sweep_angle, height, type, input1, input2, range, method=GL_FILL,
			slices=36, loops=36):  # TODO
	"""
	Type 0 = Indicator
	Type 1 = Percent Opposite directions
	Type 2 = Height
	Type 3 = Both
	:param x:
	:param y:
	:param z:
	:param inner:
	:param outer:
	:param start_angle:
	:param sweep_angle:
	:param height:
	:param type:
	:param input1:
	:param input2:
	:param range:
	:param method:
	:param slices:
	:param loops:
	:return:
	"""
	
	# if type == 0:
	#
	# elif type == 1:
	#
	# elif type == 2:
	#
	# elif type == 3:
	
	pass

def indicatorarc3d(x, y, z, inner, outer, start_angle, sweep_angle, height, input1, method=GL_FILL, slices=36, loops=36):
	
	partialDisk(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle, GLU_SILHOUETTE)
	
	if input1 > 0:
		arcCylinder(x, y, z, inner, outer, slices, loops, start_angle, sweep_angle, height, method)
	
	glutPostRedisplay()



#ADD
class Earth(object):  # FIX ROTATING THING AGAIN

	def __init__(self, center=(0, 0, 0), size=1, parent=None):
		super(Earth, self).__init__()
		object.__init__(self)
		global xRotate
		self.citylist = []
		self.cx = center[0]
		self.cy = center[1]
		self.cz = center[2]
		self.size = size
		self.id = id(self)
		self.live = ["Eureka"]
		self.livedin = ["Bishop", "Eureka", "Brea", "Los Angeles", "Seattle", "Murfreesboro", "New Orleans",
		                "Pensacola", "Atlanta", "Orlando", "Redding", "Gardnerville", "Carson City", "Lawton",
		                "Colorado Springs", "El Paso"]
		
		os.system("python /home/rendier/JARVIS/scripts/Alexandria/GoogleEarth.py")
		print 'Places Updated'
		
		with open('citylist.txt', 'r') as f:
			self.citylist = ast.literal_eval(f.read())
		
		with open('locations.txt', 'r') as nf:
			self.locations = ast.literal_eval(nf.read())

		# self.show(self, self.id)
		self.build()
		
	def build(self):

		glRotate(-90, 1, 0, 0)
		glRotate(-90, 0, 1, 0)
		glScale(self.size, self.size, self.size)
		
		for i in self.citylist:

			glColor3f(0.7, 0.7, 0.7)
			# if i[0] in self.livedin:
			# 	glPointSize(2)
			# 	glColor(1, 0, 0)

			try:
				point = self.convert(float(i[2]) * pi / 180, float(i[3]) * pi / 180)

			except ValueError:
				pass

			else:
				glBegin(GL_POINTS)
				glVertex3f(point[0] + self.cx, point[1] + self.cy, point[2] + self.cz)
				glEnd()
				
				if i[0] in self.livedin and i[7] == 'USA':
					point2 = self.convert(float(i[2]) * pi / 180, float(i[3]) * pi / 180, 0.2)
					glColor3f(1, 0, 0)
					glLineWidth(2)
					glBegin(GL_LINES)
					glVertex3f(point[0] + self.cx, point[1] + self.cy, point[2] + self.cz)
					glVertex3f(point2[0] + self.cx, point2[1] + self.cy, point2[2] + self.cz)
					glEnd()
					if i[0] in self.live:
						glColor(0, 1, 1)
						glPointSize(3)
						glBegin(GL_POINTS)
						glVertex3f(point2[0], point2[1], point2[2])
						glEnd()
						glColor(1, 1, 0)
						Circle(point2[0], point2[1], point2[2], 0.04, 36)

				glPointSize(1)
		
		for i in self.locations:
			
			glColor3f(1, 1, 0)
			
			try:
				point = self.convert(float(i[2]) * pi / 180, float(i[1]) * pi / 180)
			
			except ValueError:
				pass
			
			else:
				glPointSize(2)
				glBegin(GL_POINTS)
				glVertex3f(point[0] + self.cx, point[1] + self.cy, point[2] + self.cz)
				glEnd()
				
				glPointSize(1)
		self.surface(1.99)

		glScale(1 / self.size, 1 / self.size, 1 / self.size)
		glRotate(90, 0, 1, 0)
		glRotate(90, 1, 0, 0)

	def convert(self, lat, lon, alt=0):
		# see http://www.mathworks.de/help/toolbox/aeroblks/llatoecefposition.html
		rad = numpy.float64(2 * self.size)  # Radius of the Earth (in meters)
		f = numpy.float64(1.0 / 298.257223563)  # Flattening factor WGS84 Model
		cosLat = numpy.cos(lat)
		sinLat = numpy.sin(lat)
		FF = (1.0 - f) ** 2
		C = 1 / numpy.sqrt(cosLat ** 2 + FF * sinLat ** 2)
		S = C * FF

		x = (rad * C + alt) * cosLat * numpy.cos(lon)
		y = (rad * C + alt) * cosLat * numpy.sin(lon)
		z = (rad * S + alt) * sinLat

		return (x, y, z)
	
	def surface(self, radius, slices=36, stacks=36):

		glColor3f(1, 1, 1)
		glBegin(GL_LINES)
		glVertex3f(self.cx, self.cy, (-radius - 1 + self.cz))
		glVertex3f(self.cx, self.cy, (radius + 1 + self.cz))
		glEnd()

		glTranslate(self.cx, self.cy, self.cz)
		glColor(0, 0, 0)
		glutSolidSphere(radius, slices, stacks)

		glColor(0, 0, 0.2)
		glutWireSphere(radius, slices, stacks)
		glTranslate(-self.cx, -self.cy, -self.cz)

	def show(self, object, objid):
		Show.add(object, objid)

	def hide(self, object):
		Show.remove(object)
		
class GraphPlot(object):#ADD GLSCALE TO THIS TODO
	
	def __init__(self, equation=None, center=(0, 0, 0), grid_range=100, step=10, color=(1, 1, 1), size=1, resolution=2, parent=None):
		super(GraphPlot, self).__init__()
		object.__init__(self)
		self.cx = center[0]
		self.cy = center[1]
		
		try:
			self.cz = center[2]
		except IndexError:
			pass
		
		self.center = center
		self.range = grid_range
		self.step = step
		if equation:
			self.equation = equation
		self.color = color
		self.size = size
		self.resolution = resolution
		
		self.build()
		# self.show(self, id(self))
		
	def build(self):
		if len(self.center) == 2:
			for i in range(len(self.equation)):
				self.graph2d(self.equation[i], colors[i + 1])
			self.grid2d(self.range, self.step)
			
		if len(self.center) == 3:
			self.image = Image.open("./images/trans-grad.png")  # MCP_3D_Graphic.jpg")#kerneltex.jpg")
			self.ix = self.image.size[0]
			self.iy = self.image.size[1]
			self.image = self.image.convert("RGBA").tobytes("raw", "RGBA")
			
			self.LoadTextures(self.image)
			
			if type(self.equation) == str:
				self.graph3d(self.equation, self.color)
			elif type(self.equation) == list:
				for i in range(len(self.equation)):
					self.graph3d(self.equation[i], colors[i + 1])
			self.grid3d(self.range, self.step)
			self.halo3d(self.range)
	
	def LoadTextures(self, image):
		
		# Create Texture
		textures = glGenTextures(3)
		glBindTexture(GL_TEXTURE_2D, int(textures[1]))  # 2d texture (x and y size)
		
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, self.ix, self.iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
		#
		# Create Linear Filtered Texture
		glBindTexture(GL_TEXTURE_2D, int(textures[1]))
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, self.ix, self.iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
		
		# Create MipMapped Texture
		glBindTexture(GL_TEXTURE_2D, int(textures[2]))
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
		gluBuild2DMipmaps(GL_TEXTURE_2D, 3, self.ix, self.iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
	
	def halo3d(self, grid_range):#FIX GRADIENT TRANSPARANCY TRY TRANSPARENT TEXTURE TODO
		
		
		# glEnable(GL_TEXTURE_2D)
		# glEnable(GL_TEXTURE_GEN_S)
		# glEnable(GL_TEXTURE_GEN_T)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glColor4f(1, 1, 1, 0.4)
		
		glPushMatrix()
		glBegin(GL_QUADS)
		glVertex3f((grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glVertex3f((grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glEnd()
		
		glBegin(GL_QUADS)
		glVertex3f((grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glVertex3f((grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glEnd()
		
		glBegin(GL_QUADS)
		glVertex3f((grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glVertex3f((grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glEnd()
		
		glBegin(GL_QUADS)
		glVertex3f((-grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (0 + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (-grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glVertex3f((-grid_range + self.cx) * self.size, (grid_range + self.cy) * self.size, (grid_range + self.cz) * self.size)
		glEnd()
		
		glPopMatrix()
		# glDisable(GL_TEXTURE_GEN_S)
		# glDisable(GL_TEXTURE_GEN_T)
		# glDisable(GL_TEXTURE_2D)
		
		glDisable(GL_BLEND)
	
	def grid3d(self, grid_range, step):

		glColor3f(0.2, 0.2, 0.2)
		
		for x in range(-grid_range, grid_range + 1, step):
			Label3d((x + self.cx) * self.size, (self.cy + grid_range) * self.size, (self.cz - grid_range) * self.size, str(x))
			for y in range(-grid_range, grid_range + 1, step):
				Label3d((grid_range + self.cx) * self.size, (self.cy + y) * self.size, (self.cz - grid_range) * self.size, str(y))
				glBegin(GL_LINES)
				glVertex3f((x + self.cx) * self.size, (self.cy - grid_range) * self.size, (self.cz - grid_range) * self.size)
				glVertex3f((x + self.cx) * self.size, (self.cy + grid_range) * self.size, (self.cz - grid_range) * self.size)
				glVertex3f((self.cx - grid_range) * self.size, (self.cy + y) * self.size, (self.cz - grid_range) * self.size)
				glVertex3f((self.cx + grid_range) * self.size, (self.cy + y) * self.size, (self.cz - grid_range) * self.size)
				glEnd()
		
		# glColor3f(0, 0, 0.5)
		for x in range(-grid_range, grid_range + 1, step):
			Label3d((self.cx + x) * self.size, (self.cy - grid_range) * self.size, (self.cz + grid_range) * self.size, str(x))
			for z in range(-grid_range, grid_range + 1, step):
				Label3d((self.cx + grid_range) * self.size, (self.cy - grid_range) * self.size, (self.cz + z) * self.size, str(z))
				glBegin(GL_LINES)
				glVertex3f((self.cx + x) * self.size, (self.cy - grid_range) * self.size, (self.cz - grid_range) * self.size)
				glVertex3f((self.cx + x) * self.size, (self.cy - grid_range) * self.size, (self.cz + grid_range) * self.size)
				glVertex3f((self.cx - grid_range) * self.size, (self.cy - grid_range) * self.size, (self.cz + z) * self.size)
				glVertex3f((self.cx + grid_range) * self.size, (self.cy - grid_range) * self.size, (self.cz + z) * self.size)
				glEnd()
		
		# glColor3f(0, 0.5, 0)
		for y in range(-grid_range, grid_range + 1, step):
			Label3d((self.cx - grid_range) * self.size, (self.cy + y) * self.size, (self.cz + grid_range) * self.size, str(y))
			for z in range(-grid_range, grid_range + 1, step):
				Label3d((self.cx - grid_range) * self.size, (self.cy + grid_range) * self.size, (self.cz + z) * self.size, str(z))
				glBegin(GL_LINES)
				glVertex3f((self.cx - grid_range) * self.size, (self.cy - grid_range) * self.size, (self.cz + z) * self.size)
				glVertex3f((self.cx - grid_range) * self.size, (self.cy + grid_range) * self.size, (self.cz + z) * self.size)
				glVertex3f((self.cx - grid_range) * self.size, (self.cy + y) * self.size, (self.cz - grid_range) * self.size)
				glVertex3f((self.cx - grid_range) * self.size, (self.cy + y) * self.size, (self.cz + grid_range) * self.size)
				glEnd()
		
		axes = [
			[[(-grid_range + self.cx) * self.size, 0, 0], [(grid_range + self.cx) * self.size, 0, 0]],
			[[0, (-grid_range + self.cy) * self.size, 0], [0, (grid_range + self.cy) * self.size, 0]],
			[[0, 0, (-grid_range + self.cz) * self.size], [0, 0, (grid_range + self.cz) * self.size]]
		]
		
		glColor3f(1, 1, 1)
		glBegin(GL_LINES)
		for axis in axes:
			glVertex3f(axis[0][0], axis[0][1], axis[0][2])
			glVertex3f(axis[1][0], axis[1][1], axis[1][2])
		glEnd()
			
	def graph3d(self, equation, color=(1, 1, 1), method=GL_QUADS):#DO SPHERE AND INVERSE TODO
		array = []
		grid_steps = self.range * 2 * self.resolution
				
		for x in numpy.linspace(-self.range, self.range, grid_steps + 1):
			line = []
			for y in numpy.linspace(-self.range, self.range, grid_steps + 1):
				# exec "z = {}".format(equation)
				try:
					exec "z = {}".format(equation)
				except ValueError:
					pass
				except ZeroDivisionError:
					pass
				else:
					line.append(((x + self.cx) * self.size, (y + self.cy) * self.size, (z + self.cz) * self.size))
			array.append(line)

		array = sorted(array)
		
		for i in range(len(array) - 1):
			for j in range(grid_steps):
				glColor3f(color[0], color[1], color[2])
				glBegin(GL_LINE_LOOP)
				glVertex3f(array[i][j][0], array[i][j][1], array[i][j][2])#
				glVertex3f(array[i][j + 1][0], array[i][j + 1][1], array[i][j + 1][2])
				glVertex3f(array[i + 1][j + 1][0], array[i + 1][j + 1][1], array[i + 1][j + 1][2])
				glVertex3f(array[i + 1][j][0], array[i + 1][j][1], array[i + 1][j][2])
				glEnd()
							
		if method == GL_QUADS:
			glColor3f(color[0] * 0.1, color[1] * 0.1, color[2] * 0.1)
			for i in range(len(array) - 1):
				for j in range(grid_steps):
					glBegin(GL_QUADS)
					glVertex3f(array[i][j][0], array[i][j][1], array[i][j][2])
					glVertex3f(array[i][j + 1][0], array[i][j + 1][1], array[i][j + 1][2])
					glVertex3f(array[i + 1][j + 1][0], array[i + 1][j + 1][1], array[i + 1][j + 1][2])
					glVertex3f(array[i + 1][j][0], array[i + 1][j][1], array[i + 1][j][2])
					glEnd()
		
		self.grid3d(self.range, self.step)
	
	def grid2d(self, grid_range, step):
		
		axes = [
			[[(-grid_range * self.size) + self.cx, self.cy], [(grid_range * self.size) + self.cx, self.cy]],
			[[self.cx, (-grid_range * self.size) + self.cy], [self.cx, (grid_range * self.size) + self.cy]]
		]
		gui.refresh2d()
		
		glColor3f(0.4, 0.4, 0.4)
		# glScale(self.size, self.size, self.size)
		glBegin(GL_LINES)
		for axis in axes:
			glVertex2f(axis[0][0], axis[0][1])
			glVertex2f(axis[1][0], axis[1][1])
		glEnd()
		
		glColor3f(0.2, 0.2, 0.2)

		for x in range(-grid_range, grid_range + 1, step):
			gui.label((x * self.size + self.cx ), (self.cy + grid_range * self.size), str(x))
			for y in range(-grid_range, grid_range + 1, step):
				gui.label((self.cx + grid_range * self.size) , (y * self.size + self.cy), str(y))
				glBegin(GL_LINES)
				glVertex2f((x * self.size + self.cx), (self.cy - grid_range * self.size))
				glVertex2f((x * self.size + self.cx), (self.cy + grid_range * self.size))
				glVertex2f((self.cx - grid_range * self.size), (self.cy + y * self.size))
				glVertex2f((self.cx + grid_range * self.size), (self.cy + y * self.size))
				glEnd()
		
		gui.refresh3d()
		
	def graph2d(self, equation, color=(1, 1, 1), method=GL_LINES):#fix for +/- root etc TODO
		array = []
		grid_steps = (self.range * 2) + 1
		
		for x in numpy.linspace(-self.range, self.range, grid_steps):
			try:
				exec "y = {}".format(equation)
			except ValueError:
				pass
			except ZeroDivisionError:
				pass
			else:
				array.append(((x * self.size + self.cx), (y * self.size + self.cy)))
	
		glColor3f(color[0], color[1], color[2])
		gui.refresh2d()
		glBegin(method)
		for i in range(len(array) - 1):
			glVertex2f(array[i][0], array[i][1])
			if i < len(array):
				glVertex2f(array[i + 1][0], array[i + 1][1])

		glEnd()
		gui.refresh3d()
		
	def show(self, obj, objid):
		Show.add(obj, objid)

class WorkThread(Thread):
	
	def __init__(self, worktype, parent=None, *args):
		super(WorkThread, self).__init__(parent)
		Thread.__init__(self, parent)
		self.type = worktype
		self.args =[]
		for arg in args:
			self.args.append(arg)
	
	def __del__(self):
		pass
	
	def run(self):
		if self.type == "NET":
			self.netstat(self.args[0])
		
		pass

	def netstat(self, interface):

		netTx = cmdline('cat /sys/class/net/{}/statistics/tx_bytes'.format(self.netIF[interface]))
		netRx = cmdline('cat /sys/class/net/{}/statistics/rx_bytes'.format(self.netIF[interface]))
		# print "1", netTx, netRx
		time.sleep(0.01)
		nextnetTx = cmdline('cat /sys/class/net/{}/statistics/tx_bytes'.format(self.netIF[interface]))
		nextnetRx = cmdline('cat /sys/class/net/{}/statistics/rx_bytes'.format(self.netIF[interface]))
		# print "2", nextnetTx, nextnetRx
		return (netTx, nextnetTx, netRx, nextnetRx)

# Already Moved Identity
class Identity(object):
	
	def __init__(self, x=70, y=119, parent=None):
		super(Identity, self).__init__()
		object.__init__(self)
		
		self.x = x
		self.y = y
		self.id = id(self)
		
		self.name = "Ptolemaios Philadelphos"#"P t o l e m y II"#"J A R V I S"#"Φιλάδελφος"#
		self.user = cmdline('whoami')[0: -1]
		self.platform = cmdline("uname -o")[0: -1]
		self.nodename = cmdline('uname -n')[0: -1]
		# CPU Stats
		self.cpuCount = psutil.cpu_count()
		self.cpuPercent = psutil.cpu_percent(None, True)
		self.cpuAngle = 360.0 / self.cpuCount
		# RAM Stats
		self.psMem = psutil.virtual_memory()
		self.memAngle = 360.0 * (self.psMem[2] / 100.)
		self.memDarkAngle = 360.0 - self.memAngle
		# SWAP Stats
		self.psSwap = psutil.swap_memory()
		self.swapAngle = 360 * (self.psSwap[3] / 100.0)
		# NET Stats
		self.netIF = cmdline('ls /sys/class/net/').split("\n")[:-1]
		self.netCount = len(self.netIF)
		self.netAngle = 360.0 / self.netCount
		# Processes and percentages
		self.proc = psutil.process_iter()
		self.procList = []
		for i in self.proc:
			self.procList.append(i)
		self.procNum = len(self.procList)
		self.procAngle = 360.0 / self.procNum
		self.procColor = 0
		self.procSquare = ceil(sqrt(self.procNum))
		self.procNetNum = len(cmdline('ls /sys/class/net/').split("\n")[:-1])
		
		self.build()
		# self.show(self, self.id)
		
	def build(self):
		glColor3f(0, 0, 1)
		gui.refresh2d()
		#Frame identity
		gui.frame(self.x - 64, self.y - 114, 134, 185)
		
		#Display Platform, User, Node Name
		gui.title(self.x - 60, self.y - 110, 120, self.nodename)
		gui.title(self.x - 60, self.y - 93, 120, self.user)
		gui.title(self.x - 60, self.y - 76, 120, self.platform)
		#70, 115
		
		#Apply Branding
		glColor3f(1, 1, 1)
		radius = 58
		sweep_angle = (len(self.name) * 10) / (radius + 2) / (pi / 180.)
		start_angle = 180 - ((180 - sweep_angle) / 2)
		
		if len(self.name.split(" ")) > 1:#FIX FOR ANY LENGTH TWO WORD NAME TODO
			gui.labelcur(self.x - 3, self.y - 5, radius, start_angle - 45, -sweep_angle/2, self.name.upper().split(" ")[0])
			gui.labelcur(self.x - 3, self.y - 5, radius, -start_angle + 45, sweep_angle/2, self.name.upper().split(" ")[1])
			
		else:
			gui.labelcur(self.x - 3, self.y - 5, radius, start_angle, -sweep_angle, self.name.upper())
		
		#Kernel
		glColor3f(1, 1, 1)
		gui.circle(self.x, self.y, 5, 36, GL_POLYGON)
		
		#CPU
		cpuRadius = 7
		for i in range(self.cpuCount):
			glColor3d(colors[i + 3][0], colors[i + 3][1], colors[i + 3][2])
			gui.partialdisk(self.x, self.y, cpuRadius, cpuRadius + 5, 36, 36, i * self.cpuAngle, self.cpuAngle * (self.cpuPercent[i] / 100.0))
		
		#RAM
		ramRadius = self.cpuCount * 7
		glColor3f(0, 1, 0)
		gui.partialdisk(self.x, self.y, ramRadius , ramRadius + 5, 36, 36, 0, self.memAngle)
		
		#VMEM
		vmemRadius = (self.cpuCount + 1) * 7
		glColor3f(1, 1, 0)
		gui.partialdisk(self.x, self.y, vmemRadius, vmemRadius + 5, 36, 36, 0, self.swapAngle)
		
		#GPU
		gpuRadius = (self.cpuCount + 2) * 7
		glColor3f(0, 0, 1)
		gui.partialdisk(self.x, self.y, gpuRadius, gpuRadius + 5, 36, 36, 0, 360)
		
		#NET
		netRadius = (self.cpuCount + 3) * 7
		for i in range(len(self.netIF)):
			netcolor = (colors[i + 3][0], colors[i + 3][1], colors[i + 3][2])
			
			netStats1 = psutil.net_io_counters(True)
			netTx = netStats1[self.netIF[i]][0]
			netRx = netStats1[self.netIF[i]][1]
			# print "1", netTx, netRx
			time.sleep(0.1)
			
			netStats2 = psutil.net_io_counters(True)
			nextnetTx = netStats2[self.netIF[i]][0]
			nextnetRx = netStats2[self.netIF[i]][1]
			# print "2", nextnetTx, nextnetRx
			
			inputTx = int(nextnetTx) - int(netTx)
			inputRx = int(nextnetRx) - int(netRx)
			# print "3", inputTx, inputRx
						
			glColor3f(colors[i + 3][0], colors[i + 3][1], colors[i + 3][2])
			
			gui.partialdisk(self.x, self.y, netRadius, netRadius + 5, 36, 36, (i * self.netAngle), self.netAngle, GLU_SILHOUETTE)
			
			if inputTx + inputRx > 0:
				gui.partialdisk(self.x, self.y, netRadius, netRadius + 5, 36, 36, (i * self.netAngle), self.netAngle)
			
		#PROC
		procRadius = (self.cpuCount + 4) * 7
		for i in range(self.procNum):
			try:
				procPercent = self.procList[i].cpu_percent()
			except psutil.NoSuchProcess:
				pass
			else:
								
				if procPercent > 0:
					glColor3f(1, 0, 0)
					gui.partialdisk(self.x, self.y, procRadius, procRadius + 9, 36, 36, i * self.procAngle, self.procAngle)
					
		
					
		glColor3f(0, 0, 0.5)
		gui.circle(self.x, self.y, 52, 36)
		gui.circle(self.x, self.y, 43, 36)
		
		gui.refresh3d()

	def show(self, obj, objid):
		Show.add(obj, objid)
		
class GUI(object):#FIX TRANCPARENCY IN IDENTITY TODO
	
	def __init__(self):
		super(GUI, self).__init__()
		object.__init__(self)
		self.user = cmdline('whoami')[0: -1]
		self.platform = cmdline("uname -o")[0: -1]
		self.nodename = cmdline('uname -n')[0: -1]
		# self.
				
	def refresh2d(self):
		glViewport(0, 0, g_Width, g_Height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0.0, g_Width, 0.0, g_Height, 0.0, 1.0)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
	
	def refresh3d(self):
		glLoadIdentity()
		gluLookAt(0, 0, g_fViewDistance, 0, 0, 0, -.1, 0, 0)  # -.1,0,0
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(zoom, float(g_Width) / float(g_Height), g_nearPlane, g_farPlane)
		glMatrixMode(GL_MODELVIEW)
		polarView()
	
	def frame(self, x, y, width, height, label=None):
		
		if label:
			self.title(x, y + height - 3, len(label) * 15, label)
			
		self.rect(x, y, width - 1, height - 1)
		self.rect(x + 2, y + 2, width - 5, height - 5)
		
	def title(self, x, y, width, label):
		
		glColor3f(1, 1, 1)
		self.label(x + 5, y, label)
		glColor3f(1, 0, 0)
		self.line(x, y + 2, x + 5 + width, y + 2)
		glColor3f(0, 0, 0.5)
		self.quad(
			x, y + 5,
			x + 5, y + 10,
			x + (width/3)*2, y + 10,
			x + (width/3) * 2, y + 5
		)
		self.quad(
			x, y,
			x + 5, y + 4,
			x + 5 + width, y + 4,
			x + width, y
		)
		
	def label(self, x, y, text, font=fonts[0]):
		blending = False
		if glIsEnabled(GL_BLEND):
			blending = True
		
		glEnable(GL_BLEND)
		glRasterPos2f(x, y)
		
		for character in text:
			glutBitmapCharacter(font, ctypes.c_int(ord(character)))

		if not blending:
			glDisable(GL_BLEND)
	
	# Already Moved
	def labelcur(self, cx, cy, radius, start_angle, sweep_angle, label):
		try:
			theta = 2.0 / (360.0 / sweep_angle) * pi / (len(label) - 1)
		except ZeroDivisionError:
			theta = pi / 180
		c = cos(theta)
		s = sin(theta)
		
		x = radius * cos(start_angle * (pi / 180.))
		y = radius * sin(start_angle * (pi / 180.))
		
		for i in range(len(label)):
			self.label(x + cx, y + cy, label[i])#.encode("utf8"))
			
			t = x
			x = c * x - s * y
			y = s * t + c * y
	
	def rect(self, x, y, width, height, method=GL_LINE_LOOP):
		glBegin(method)
		glVertex2f(x, y)
		glVertex2f(x, y + height)
		glVertex2f(x + width, y + height)
		glVertex2f(x + width, y)
		glEnd()
		glutPostRedisplay()
		
	def quad(self, x1, y1, x2, y2, x3, y3, x4, y4, method=GL_POLYGON):
	
		glBegin(method)
		glVertex2f(x1, y1)
		glVertex2f(x2, y2)
		glVertex2f(x3, y3)
		glVertex2f(x4, y4)
		glEnd()
		glutPostRedisplay()
			
	def button(self, x, y, lable=None, width=100, height=25):
		
		self.rect(x, y, width, height)
		if lable:
			self.label(x, y + (height / 2.6), lable)
		glutPostRedisplay()
	
	def circle(self, cx, cy, radius, sides, method=GL_LINE_LOOP):
		try:
			theta = 2.0 * pi / sides
		except ZeroDivisionError:
			theta = pi / 180
		c = cos(theta)
		s = sin(theta)
		
		x = radius
		y = 0
		
		glBegin(method)
		for i in range(0, sides + 1):
			glVertex2f(x + cx, y + cy)
			
			t = x
			x = c * x - s * y
			y = s * t + c * y
		
		glEnd()
	
	def partialcircle(self, cx, cy, radius, start_angle, sweep_angle, sides, method=GL_LINE_STRIP):
		try:
			theta = -2.0 / (360.0 / sweep_angle) * pi / (sides)
		except ZeroDivisionError:
			theta = pi / 180
		c = cos(theta)
		s = sin(theta)
		
		x = radius * cos(start_angle * (pi / 180.))
		y = radius * sin(start_angle * (pi / 180.))
		
		glBegin(method)
		for i in range(sides + 1):
			glVertex2f(x + cx, y + cy)
			
			t = x
			x = c * x - s * y
			y = s * t + c * y
		glEnd()
	
	def partialdisk(self, x, y, inner, outer, slices, loops, start_angle, sweep_angle, method=GL_FILL):
		
		glTranslate(x, y, 0)
		quadratic = gluNewQuadric()
		gluQuadricNormals(quadratic, GLU_SMOOTH)  # Create Smooth Normals (NEW)
		gluQuadricTexture(quadratic, GL_TRUE)
		gluQuadricDrawStyle(quadratic, method)
		gluPartialDisk(quadratic, inner, outer, slices, loops, start_angle, sweep_angle)
		glTranslate(-x, -y, 0)
		glutPostRedisplay()
	
	def line(self, x1, y1, x2, y2, method=GL_LINE_STRIP):
		glBegin(method)
		glVertex2f(x1, y1)
		glVertex2f(x2, y2)
		glEnd()
	
	def percentbar(self, x, y, width, height, percent, color, title=None, type="Horizontal"):
		self.refresh2d()
		if type == "Vertical":
			t = width
			width = height
			height = t
		
		if title:
			self.title(x, y + height, width, "{} {}".format(title, percent))
		
		percent = int(percent) / 100.0
		glColor3f(color[0], color[1], color[2])
		
		if percent != 0:
			self.rect(x, y, width, height)
			self.rect(x, y, width * percent, height, GL_POLYGON)
		self.refresh3d()
	
	def percentarc(self, x, y, inner, outer, start_angle, sweep_angle, percent, color, title=None, sides=36, loops=36, method=GL_FILL):
		self.refresh2d()
		if title:
			self.title(x - outer, y + outer, 2 * outer, "{} {}".format(title, percent))
		
		percent = int(percent) / 100.0
		glColor3f(color[0], color[1], color[2])
		
		if percent != 0:
			self.partialdisk(x, y, inner, outer, sides, loops, start_angle, sweep_angle * percent, method)
		self.refresh3d()
	
	def marquee(self, x, y, width, height, title, input, color):  # FIX MARQUEE TODO
		
		self.refresh2d()
		marqueeList = [0] * (width - 2)
		self.refresh2d()
		self.rect(x, y, width, height)
		
		for i in range(len(marqueeList)):
			self.line(x + 1 + i, y + 1, x + 1 + i, y + (height / 2))
		
		self.refresh3d()
							
	def bargraph(self, x, y, width, height, data, color, label1, title=None, type="Horizontal", method=GL_QUADS):#FIX VERTICAL TODO
		
		data = [(0, "zero"), (1, "one"), (2, "two"), (3, "three"), (4, "four")]
		# data = [
		# 	(31, "January"),
		# 	(28, "February"),
		# 	(31, "March"),
		# 	(30, "April"),
		# 	(31, "May"),
		# 	(30, "June"),
		# 	(31, "July"),
		# 	(31, "August"),
		# 	(30, "September"),
		# 	(31, "October"),
		# 	(30, "November"),
		# 	(31, "December"),
		# ]
		strlen = 0
		for i in data:
			if len(i[1]) > strlen:
				strlen = len(i[1])
		width = strlen * 9 * len(data) + 30
		numbervalue = len(data)
		maxvalue = max(data)[0]
		
		self.refresh2d()
				
		if type == "Vertical":
			glTranslate(x + width/2, y + height/2, 0)
			glRotate(90, 0, 0, 1)
			glTranslate(-x, -y, 0)
			t = width
			width = height
			height = t
		
		barwidth = (width - 15) / numbervalue
		barunit = (height - 25) / maxvalue
		
		if title:
			self.title(x, y + height, width, title)
			
		glColor3f(color[0], color[1], color[2])
		
		self.rect(x, y, width, height)



		newstring = ""
		for i in label1:
			newstring += i + " "
			
		#FIX AUTOWIDTH TODO
			
		for i in range(len(label1)):
			
			glRotate(i / 2 * (5 / len(label1)), 0, 0, 1)
			glRasterPos2f(x - 15, y + i * height/len(label1)+ 10)
			
			glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ctypes.c_int(ord(str(label1[-1 - i]))))
			glRotate(- i / 2 * (5 / len(label1)), 0, 0, 1)
		
		for i in range(len(data)):
			glColor(1, 1, 1)
			icolor = i - (i / 8) * 8#colors[i]

			if icolor == 0:
				icolor += 4

			glColor3f(colors[icolor][0], colors[icolor][1], colors[icolor][2])
			self.rect(x + (i * barwidth) + 10 + 5, y + 20, barwidth - 5, barunit * data[i][0], method)
			
			if data[i][1] != "":
				self.label(x + (i * barwidth) + 10 + 5 + (barwidth / 2 - (len(data[i][1]) * 9) / 2), y + 10, str(data[i][1]), GLUT_BITMAP_8_BY_13)
			
		
		self.refresh3d()

	def io2on1(self):
		#input/output both on one bar graph with different colors
		#as range increases change range and adjust
		pass
	
	def io2on2(self):
		#input/output on two graphs back to back same color
		pass
	
class Show(object):
	
	def __init__(self, parent=None):
		super(Show, self).__init__()
		object.__init__(self)
		
		self.showlist = []
		self.showdict = {}
		self.name = {}
		self.objnum = 0
	
	def add(self, obj, objid):
		self.showlist.append(obj)
		self.showdict[obj] = self.objnum
		self.name[objid] = obj
		self.objnum += 1
	
	def remove(self, objid):
		self.showlist.remove(self.showdict.pop(ctypes.cast(objid, ctypes.py_object)))
		self.name.pop(ctypes.cast(objid, ctypes.py_object))
		self.objnum -= 1
	
	def show(self):
		for i in self.showlist:
			i.build()
	
	def scale(self, scale):
		glScale(scale, scale, scale)


		
#Core FIX GUI FOR EACH WITH X AND Y TODO
class KernelCore(object):
	
	def __init__(self, place, size=0.5, parent=None):
		super(KernelCore, self).__init__()
		object.__init__(self)
		self.place = place
		self.size = size
		self.id = id(self)
		#Kernel Stats
		self.text = cmdline("dmesg | tail -15")
		self.txt2img(self.text)
		
		self.image = Image.open("kerneltex.jpg")  # mcp-2.jpg")#MCP_3D_Graphic.jpg")#kerneltex.jpg")
		self.ix = self.image.size[0]
		self.iy = self.image.size[1]
		self.image = self.image.convert("RGBA").tobytes("raw", "RGBA")
		
		self.LoadTextures(self.image)
		
		self.build()
		# self.show(self, self.id)
				
	def build(self):
		# Kernel
		glColor3f(0.5, 0.5, 0.5)
		glScale(self.size, self.size, self.size)
		# apply texture
		glEnable(GL_TEXTURE_2D)
		glPushMatrix()
		# glEnable(GL_TEXTURE_GEN_S)
		# glEnable(GL_TEXTURE_GEN_T)

		Cylinder(0, 0, 0, 2, 2, 8, 36, 36)
		# Cylinder(0, 0, 0, 1, 1, 1, 36, 36)
		# glTranslate(0, 0, 1)
		# Cylinder(0, 0, 0, 1, 0, 1, 36, 36)
		# glTranslate(0, 0, 1)
		# Cylinder(0, 0, 0, 0, 1, 1, 36, 36)
		# glTranslate(0, 0, 1)
		# Cylinder(0, 0, 0, 1, 1, 2, 36, 36)

		# arcCylinder(0, 0, 0, self.place, self.place + 1, 36, 36, 0, 360, 5, GLU_FILL)

		glPopMatrix()
		# glDisable(GL_TEXTURE_GEN_S)
		# glDisable(GL_TEXTURE_GEN_T)
		glDisable(GL_TEXTURE_2D)
		glutPostRedisplay()
		glScale(1/self.size, 1/self.size, 1/self.size)
		
	def buildGUI(self):
		gui.refresh2d()
		# glColor3f(1, 1, 1)
		# gui.partialdisk(70, 115, 0, 5, 36, 36, 0, 360)
		gui.refresh3d()
	
	def LoadTextures(self, image):

		# Create Texture
		textures = glGenTextures(3)
		glBindTexture(GL_TEXTURE_2D, int(textures[1]))  # 2d texture (x and y size)
		
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, self.ix, self.iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
		
		# # Create MipMapped Texture
		# glBindTexture(GL_TEXTURE_2D, int(textures[2]))
		# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
		# gluBuild2DMipmaps(GL_TEXTURE_2D, 3, self.ix, self.iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
		
		# Create Linear Filtered Texture
		glBindTexture(GL_TEXTURE_2D, int(textures[1]))
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, self.ix, self.iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
	
	def loadimage(self, imagename):
		image = Image.open(imagename)  # mcp-2.jpg")#MCP_3D_Graphic.jpg")#kerneltex.jpg")
		self.ix = image.size[0]
		self.iy = image.size[1]
		image = image.convert("RGBA").tobytes("raw", "RGBA")
		
		return image
	
	def getdmesg(self):
		text = ""
		with open("/var/log/dmesg", "r") as f:
			text = f.read()
		
		return text
	
	def txt2img(self, text, rotate_angle=180):
		
		"""Render label as image."""
		font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
		imgOut = Image.new("RGBA", (20, 49), (0, 0, 0))
		
		# calculate space needed to render text
		draw = ImageDraw.Draw(imgOut)
		sizex, sizey = draw.textsize(text, font)
		
		imgOut = imgOut.resize((sizex, sizey))
		
		# render label into image draw area
		draw = ImageDraw.Draw(imgOut)
		# item = random.randrange(6)
		# print item
		# if item == 0: item = 1
		draw.text((0, 0), text, (255, 255, 255), font)
		# draw.text((0, 0), text, (colors[item + 1][0] * (254/item), colors[item + 1][1] * (254/item), colors[item + 1][2] * (254/item)), font)
		imgOut = imgOut.transpose(Image.FLIP_LEFT_RIGHT)
		if rotate_angle:
			imgOut = imgOut.rotate(rotate_angle)
			
		
		imgOut.save('kerneltex.jpg')
		# return imgOut
	
	def show(self, object, objid):
		Show.add(object, objid)
		
	def hide(self):
		Show.remove(self.id)
		
class CPUCore(object):
	
	def __init__(self, place, size=0.5, parent=None):
		super(CPUCore, self).__init__()
		object.__init__(self)
		self.place = (place + 1) * 0.5
		self.place0 = place
		self.size = size
		self.id = id(self)
		#CPU Stats
		self.cpuCount = psutil.cpu_count()
		self.cpuPercent = psutil.cpu_percent(None, True)
		self.cpuAngle = 360.0/self.cpuCount
		
		self.build()
		# self.show(self, self.id)
		
	def build(self):#ADD COLOR CHANGES FOR HEIGHT DEPENDENT SHAPES TODO
		#Build CPUs
		glScale(self.size, self.size, self.size)
		for i in range(self.cpuCount):
			glColor3f(colors[i + 3][0], colors[i + 3][1], colors[i + 3][2])
			percentarc3d(0, 0, 0, self.place, (self.place + 0.5), (i * self.cpuAngle), self.cpuAngle, 2, 2, self.cpuPercent[i])
		glutPostRedisplay()
		glScale(1/self.size, 1/self.size, 1/self.size)
		
	def buildGUI(self):
		# Gui Setup
		gui.refresh2d()
		for i in range(self.cpuCount):
			height = ((i + self.place0) * 25) + 15
			
			cpucolor = (colors[i + 3][0] * 0.5, colors[i + 3][1] * 0.5, colors[i + 3][2] * 0.5)
			gui.percentbar(g_Width - 210, g_Height - height, 200, 15, self.cpuPercent[i], cpucolor, "CPU {}".format((i + 1)))
		
		gui.refresh3d()
		glutPostRedisplay()
	
	def show(self, object, objid):
		Show.add(object, objid)

class RAMCore(object):
	
	def __init__(self, place, size=0.5, parent=None):
		super(RAMCore, self).__init__()
		object.__init__(self)
		self.place = (place + 1) * 0.5
		self.place0 = place
		self.size = size
		self.id = id(self)
		# RAM Stats
		self.psMem = psutil.virtual_memory()
		self.memAngle = 360.0 * (self.psMem[2] / 100.)
		
		self.build()
		# self.show(self, self.id)
		
	def build(self):
		# Build RAM Memory
		glColor3f(0, 1, 0)
		glScale(self.size, self.size, self.size)
		percentarc3d(0, 0, 0, self.place, self.place + 0.5, 0, 360, 1, 0, self.psMem[2])
		glScale(1/self.size, 1/self.size, 1/self.size)
		glutPostRedisplay()
		
	def buildGUI(self):
		height = ((self.place0 + psutil.cpu_count() - 1) * 25) + 15
		gui.refresh2d()
		glColor(0, 0.5,0)
		gui.percentbar(g_Width - 210, g_Height - height, 200, 15, self.psMem[2], (0, 0.5, 0), "RAM")
		gui.refresh3d()
		glutPostRedisplay()
		
	def show(self, object):
		Show.add(object)
	
class VMEMCore(object):#ADD PLATFORM IDENTIFICATION FOR PROPER CALLS TODO
	
	def __init__(self, place, size=0.5, parent=None):
		super(VMEMCore, self).__init__()
		object.__init__(self)
		self.place = (place + 1) * 0.5
		self.place0 = place
		self.size = size
		self.id = id(self)
		# SWAP Stats
		self.psSwap = psutil.swap_memory()
		
		self.build()
		# self.show(self, self.id)
		
	def build(self):
		# Build SWAP/Virtual Memory
		glColor3f(1, 1, 0)
		percentarc3d(0, 0, 0, self.place, self.place + 0.5, 0, 360, 1, 0, self.psSwap[3])
		glutPostRedisplay()
		
	def buildGUI(self):
		# Gui Setup
		height = ((self.place0 + psutil.cpu_count() - 1) * 25) + 15
		gui.refresh2d()
		gui.percentbar(g_Width - 210, g_Height - height, 200, 15, self.psSwap[3], (0.5, 0.5, 0), "VMEM/SWAP")
		gui.refresh3d()
		glutPostRedisplay()
	
	def show(self, object):
		Show.add(object)
		
class NETCore(object):#FIX MARQUEE MONITOR FUNCTION, PUT FILE MONITORING INTO A WORKTHREAD. TODO
	
	def __init__(self, place, size=0.5, parent=None):
		super(NETCore, self).__init__()
		object.__init__(self)
		self.place0 = place
		self.place = (place + 1) * 0.5
		self.size = size
		self.id = id(self)
		#NET Stats
		self.netIF = cmdline('ls /sys/class/net/').split("\n")[:-1]
		self.netCount = len(self.netIF)
		self.netAngle = 360.0 / self.netCount
		
		self.build()
		# self.show(self, self.id)
		
	def build(self):#CREATE DUAL INPUT OPPOSING ARC TODO
		
		# Build Interfaces
		glScale(self.size, self.size, self.size)
		for i in range(len(self.netIF)):
			glColor3f(colors[i + 3][0], colors[i + 3][1], colors[i + 3][2])
			
			arcCylinder(0, 0, 0, self.place, (self.place + 0.5), 36, 45, (i * self.netAngle), self.netAngle, 0, GLU_SILHOUETTE)
			glColor3f(1, 1, 1)
			
			netRate = self.rate(self.netIF[i])
			if netRate[0] + netRate[1] > 0:
				arcCylinder(0, 0, 0, self.place, (self.place + 0.5), 36, 36, (i * self.netAngle), self.netAngle, 1)
		glScale(1/self.size, 1/self.size, 1/self.size)
		glutPostRedisplay()

	def buildGUI(self):#create marquee monitor TODO
		# Gui Setup
		gui.refresh2d()
		for i in range(len(self.netIF)):
			height = ((i + self.place0 + 1) * 25) + 15
			netcolor = (colors[i + 3][0] * 0.5, colors[i + 3][1] * 0.5, colors[i + 3][2] * 0.5)
			
			# netRate = self.rate()
			
			#marquee(g_Width - 210, g_Height - height + 15, 200, 15, input)
			
			gui.title(g_Width - 210, g_Height - height + 15, 200, "{}".format(self.netIF[i]))
			gui.rect(g_Width - 210, g_Height - height, 200, 15)
			
		gui.refresh3d()
		glutPostRedisplay()
	
	def rate(self, interface):
		netStats1 = psutil.net_io_counters(True)
		netTx = netStats1[interface][0]
		netRx = netStats1[interface][1]
		time.sleep(0.1)
		
		netStats2 = psutil.net_io_counters(True)
		nextnetTx = netStats2[interface][0]
		nextnetRx = netStats2[interface][1]
		
		inputTx = int(nextnetTx) - int(netTx)
		inputRx = int(nextnetRx) - int(netRx)
	
		return (inputTx , inputRx)
	
	def show(self, object):
		Show.add(object)
		
class PROCCore(object):
	
	def __init__(self, place, size=0.5, parent=None):
		super(PROCCore, self).__init__()
		object.__init__(self)
		self.place = (place + 1) * 0.5
		self.place0 = place
		self.size = size
		self.id = id(self)
		# Processes and percentages
		self.proc = psutil.process_iter()
		self.procList = []
		for i in self.proc:
			self.procList.append(i)
		self.procNum = len(self.procList)
		self.procAngle = 360.0 / self.procNum
		self.procColor = 0
		self.procSquare = ceil(sqrt(self.procNum))
		self.procNetNum = len(cmdline('ls /sys/class/net/').split("\n")[:-1])
		
		# self.buildGUI()
		self.build()
		# self.show(self, self.id)
		
	def build(self):
		# Build Processes
		glScale(self.size, self.size, self.size)
		for i in range(self.procNum):
			try:
				procPercent = self.procList[i].cpu_percent()
				procStat = self.procList[i].status()
			except psutil.NoSuchProcess:
				pass
			else:
				if procStat == 'running':  # psutil.STATUS_RUNNING green 0
					glColor3f(0, 1, 0)
				
				elif procStat == 'sleeping':  # psutil.STATUS_SLEEPING blue 1
					glColor3f(0, 0.5, 0.5)
				
				elif procStat == 'stopped':  # psutil.STATUS_STOPPED red 2
					glColor3f(1, 0, 0)
				
				elif procStat == 'zombie':  # psutil.STATUS_ZOMBIE grey 3
					glColor3f(0.5, 0.5, 0.5)
				
				elif procStat == 'dead':  # psutil.STATUS_DEAD dark grey 4
					glColor3f(0.1, 0.1, 0.1)
				
				elif procPercent > 0:
					glColor3f(1, 1, 1)

				#Clock Version
				partialDisk(0, 0, 0, 0, (self.place + 0.5) * (procPercent / 100.0), 36, 36, i * self.procAngle, self.procAngle, GLU_FILL)
				
				#Ring Version
				arcCylinder(0, 0, 0, self.place, (self.place + 0.5), 36, 36, i * self.procAngle, self.procAngle, 2 * (procPercent / 100.0), GLU_FILL)
				
				if procPercent > 0:
					glColor3f(0, 1, 0)
					partialDisk(0, 0, 1, self.place, (self.place + 0.5), 36, 36, i * self.procAngle, self.procAngle, GLU_FILL)
				
				else:
					glColor3f(0.5, 0.5, 0.5)
					partialDisk(0, 0, 1, self.place, (self.place + 0.5), 36, 36, i * self.procAngle, self.procAngle, GLU_SILHOUETTE)
		glScale(1/self.size, 1/self.size, 1/self.size)
		glutPostRedisplay()
		
	def buildGUI(self):#ADD COLORS FOR TYPE OF PROCESS (IE GREEN FOR ZOMBIE) TODO
		# height =
		gui.refresh2d()
		gui.title(g_Width - 210, g_Height - ((self.place0 + psutil.cpu_count() + self.procNetNum - 2) * 25), 200, "Proc #{} ({})".format(self.procNum, self.procSquare))
		glColor3f(1, 1, 1)
		gui.rect(g_Width - 210, g_Height - ((self.place0 + psutil.cpu_count() + self.procNetNum - 2) * 25), self.procSquare * 10 - 1, -self.procSquare * 10 - 1)
		
		
		count = self.procNum
		gridList = [(x, y) for x in range(int(self.procSquare)) for y in range(int(self.procSquare))]
		for i in range(len(self.procList)):
			try:
				procstat = self.procList[i].status()
				procpercent = self.procList[i].cpu_percent()
			except psutil.NoSuchProcess:
				pass
			else:

				if procstat == 'running':# psutil.STATUS_RUNNING green 0
					glColor3f(0, 1, 0)
				
				elif procstat == 'sleeping':# psutil.STATUS_SLEEPING blue 1
					glColor3f(0, 0, 1)
					
				elif procstat == 'stopped':# psutil.STATUS_STOPPED red 2
					glColor3f(1, 0, 0)
					
				elif procstat == 'zombie':# psutil.STATUS_ZOMBIE grey 3
					glColor3f(0.5, 0.5, 0.5)
					
				elif procstat == 'dead':# psutil.STATUS_DEAD dark grey 4
					glColor3f(0.1, 0.1, 0.1)
					
				elif procpercent > 0:
					glColor3f(1, 1, 1)
				
				elif count <= 0:# unused black 5
					glColor3f(0, 0, 0)
					
				
				
					
				gui.rect(g_Width - 210 + (gridList[i][0] * 10), g_Height - ((self.place0 + psutil.cpu_count() + self.procNetNum - 2) * 25) - (gridList[i][1] * 10),  8, -8)
				count -= 1
		
	def show(self, object, objid):
		Show.add(object, objid)
	
class GPUCore(object):#TODO
	
	def __init__(self, place, size=0.5, parent=None):
		super(GPUCore, self).__init__()
		object.__init__(self)
		self.place = (place + 1) * 0.5
		self.size = size
		self.id = id(self)
		# GPU Stats
	
		self.build()
		# self.show(self, self.id)
		
	def build(self):
		# Build GPU RAM
		glScale(self.size, self.size, self.size)
		gpuInfo = cmdline("glxinfo | grep 'Video memory'")
		# code = "glxinfo | grep 'Video memory' > tmp.txt"
		# os.system(code)
		# f = open("tmp.txt", "r")
		# gpuInfo = f.read()
		gpuNum = []
		[gpuNum.append(i) for i in gpuInfo if i.isdigit()]
		gpuMem = "".join(gpuNum)
		code2 = "intel_gpu_top"
		glColor3f(0, 0, 0.5)
		arcCylinder(0, 0, 0, self.place, self.place + 0.5, 36, 36, 0, 360, 0, GLU_SILHOUETTE)
		glScale(1/self.size, 1/self.size, 1/self.size)
		glutPostRedisplay()
	
	def buildGUI(self):
		pass
	
	def show(self, object):
		Show.add(object)


class Slider(object):  # TODO
	
	def __init__(self, parent=None):
		super(Slider, self).__init__()
		object.__init__(self)
	
	def initUI(self):
		pass

class Menu(object):
	
	def __init__(self, parent=None):
		super(Menu, self).__init__()
		object.__init__(self)
		glutCreateMenu(self.processMenuEvents)
		glutAttachMenu(GLUT_RIGHT_BUTTON)
		
		self.addmenuitems()
	
	def addmenuitems(self):
		
		glutAddMenuEntry("Identity", ctypes.c_int(1))
		glutAddMenuEntry("Two", ctypes.c_int(2))
		
		# Add the following line to fix your code
		return ctypes.c_int(0)
	
	def processMenuEvents(option):
		
		if option == 1:
			print "Well Lookie Here"
		
		if option == 2:
			print "Tarnations"
		
		print "Menu pressed"
		print str(option)
		
		return ctypes.c_int(0)
				
class Command(object):
	
	def __init__(self, parent=None):
		super(Command, self).__init__()
		object.__init__(self)
		
		self.initUI()
		
	def initUI(self):
		gui.refresh2d()
		glColor3f(0, 0, 1)
		gui.rect(6, g_Height - 27, 150, 17)
		
		gui.refresh3d()
	
	def input(self):
		
		pass
	

class Core(object):

	def __init__(self, size=0.5, parent=None):
		super(Core, self).__init__()
		object.__init__(self)
		self.size = size
		# glRotate(90, 0, 0, 1)
		
		self.Kernel = KernelCore(0)
		self.CPU = CPUCore(3)
		self.RAM = RAMCore(4)
		self.VMEM = VMEMCore(5)
		self.GPU = GPUCore(6)
		self.NET = NETCore(7)
		self.PROC = PROCCore(8)
		
		# self.show(KernelCore(0))
		# self.show(CPUCore(7))
		# # self.show(CPUCore(7))
		# self.show(RAMCore(8))
		# self.show(VMEMCore(9))
		# self.show(GPUCore(10))
		# # self.show(NETCore(11))
		# self.show(PROCCore(12))
		
		self.initUI()
				
	def initUI(self):
		
		self.Kernel.build()
		self.CPU.build()
		self.RAM.build()
		self.VMEM.build()
		self.GPU.build()
		self.NET.build()
		self.PROC.build()
		pass

	def show(self, obj):
		Show.add(obj)

# --------
# VIEWER
# --------

def printHelp():
	print """\n\n
		 -------------------------------------------------------------------\n
		 Left Mousebutton       - move eye position (+ Shift for third axis)\n
		 Middle Mousebutton     - translate the scene\n
		 Right Mousebutton      - move up / down to zoom in / out\n
		  Key                - reset viewpoint\n
		  Key                - exit the program\n
		 -------------------------------------------------------------------\n
		 \n"""

def init():
	glEnable(GL_NORMALIZE)
	# glLightfv(GL_LIGHT0, GL_POSITION, [.0, 10.0, 10., 0.])
	# glLightfv(GL_LIGHT0, GL_AMBIENT, [1.0, 1.0, 1.0, 1.0]);
	# glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0]);
	# glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0]);
	# glEnable(GL_LIGHT0)
	# glEnable(GL_LIGHTING)
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LESS)
	glShadeModel(GL_SMOOTH)
	glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
	glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
	
	resetView()

def resetView():
	global zoom, xRotate, yRotate, zRotate, xTrans, yTrans
	zoom = 65.
	xRotate = 0.
	yRotate = 0.
	zRotate = 0.
	xTrans = 0.
	yTrans = 0.
	glutPostRedisplay()

def display():
	# Clear frame buffer and depth buffer
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	# Set up viewing transformation, looking down -Z axis
	glLoadIdentity()
	gluLookAt(0, 0, g_fViewDistance, 0, 0, 0, -.1, 0, 0)
	# Set perspective (also zoom)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(zoom, float(g_Width) / float(g_Height), g_nearPlane, g_farPlane)
	glMatrixMode(GL_MODELVIEW)
	glColor3f(1,1,1)
	# Render the scene
	polarView()
	# glRotate(-90, 0, 1, 0)
	# scenemodel()
	# Cube(cube_nodes, cube_edges)
	# backGrid(-10, 10, 1, -10, 10, 1, -10, 10, 1)
	
	# glColor3f(grey[0], grey[1], grey[2])
	# cityGrid(-10, 10, 1, -10, 10, 1)
	# for i in range(0, 9):
	# 	Circle(0, 0, 0, i+1, 36)
	
	# gui.bargraph(150, g_Height/2, 350, 150, [(0, "zero"), (1, "one"), (2, "two"), (3, "three"), (4, "four")], (1, 0, 0), "nexttime", "trythis")#, "Vertical")
	#~ Plot2d = GraphPlot(center=(g_Width/2, g_Height/2), size=2)
	#~ Plot2d = GraphPlot(['sqrt(3364 - x ** 2)', '-(sqrt(3364 - x ** 2))', "50 * sin(0.1 * x)"], center=(g_Width/2, g_Height/2), size=2)
	# Show.add(Plot2d, id(Plot2d))
	#~ Plot3d = GraphPlot((0, 0, 0), 10, 1, ["sin(x) + cos(y)", "x + y"], (1, 0, 0), 0.25)
	Plot3d = GraphPlot(equation = ["sin(x) + cos(y)", "x + y"])
	
	# ctypes.cast(id(a), ctypes.py_object).value
	
	
	# Input = Command()

	Globe = Earth()
	# CORE = Core()
	# ID = Identity()
	# Show.show()
	
	# Make sure changes appear onscreen
	glutSwapBuffers()
	
	
	
def reshape(width, height):
	global g_Width, g_Height
	g_Width = width
	g_Height = height
	glViewport(0, 0, g_Width, g_Height)

def polarView():
	glTranslatef(yTrans / 100., 0.0, 0.0)
	glTranslatef(0.0, -xTrans / 100., 0.0)
	glRotatef(-zRotate, 0.0, 0.0, 1.0)
	glRotatef(-xRotate, 1.0, 0.0, 0.0)
	glRotatef(-yRotate, 0.0, 1.0, 0.0)

def keyboard(key, x, y):
	global zTr, yTr, xTr
	if (key == 'r'): resetView()
	if (key == 'o'): Kernel.hide()
	if (key == 'q'): exit(0)
	glutPostRedisplay()

def mouse(button, state, x, y):
	global action, xStart, yStart
	if (button == GLUT_LEFT_BUTTON):
		if (glutGetModifiers() == GLUT_ACTIVE_SHIFT):
			action = "MOVE_EYE_2"
		else:
			action = "MOVE_EYE"
	elif (button == GLUT_MIDDLE_BUTTON):
		action = "ZOOM"
	elif (button == GLUT_RIGHT_BUTTON):
		action = "ZOOM"
	#~ elif (button == ctypes.c_int(3)):
		#~ action = "ZOOM"
		#~ print "positive"
	#~ elif (button == ctypes.c_int(4)):
		#~ action = "ZOOM"
		#~ print "negative"
	xStart = x
	yStart = y

def motion(x, y):
	global zoom, xStart, yStart, xRotate, yRotate, zRotate, xTrans, yTrans
	if (action == "MOVE_EYE"):
		xRotate += x - xStart
		yRotate -= y - yStart
	elif (action == "MOVE_EYE_2"):
		zRotate += x - xStart
		# yRotate -= y - yStart
	elif (action == "TRANS"):
		xTrans += x - xStart
		yTrans -= y - yStart
	elif (action == "ZOOM"):
		zoom -= y - yStart
		if zoom > 200.:
			zoom = 200.
		elif zoom < 1.1:
			zoom = 1.1
	else:
		print("unknown action\n", action)
	xStart = x
	yStart = y
	glutPostRedisplay()


# ------
# MAIN
# ------
if __name__ == "__main__":
	
	
	# GLUT Window Initialization
	glutInit()
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # zBuffer
	glutInitWindowSize(g_Width, g_Height)
	glutInitWindowPosition(0 + 4, g_Height / 4)
	glutCreateWindow("PTOLEMY II Core")
	# Initialize OpenGL graphics state
	
	init()
	
	# Register callbacks
	glutReshapeFunc(reshape)
	glutDisplayFunc(display)
	glutMouseFunc(mouse)
	glutMotionFunc(motion)
	glutKeyboardFunc(keyboard)
	glutIdleFunc(glutPostRedisplay())
	# glutCreateMenu(processMenuEvents)
	printHelp()
	# glutTimerFunc(10, timerEvent, 1)
	
	gui = GUI()
	# Show = Show()
	
	Menu = Menu()
	
	
	# Turn the flow of control over to GLUT
	glutMainLoop()
	
	
