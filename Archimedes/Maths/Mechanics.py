#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'rendier'
import math
from decimal import Decimal
import inspect
from PyQt4 import QtCore

class Classical(QtCore.QObject):
	
	def __init__(self, parent=None):
		super(Classical, self).__init__()
		QtCore.QObject.__init__(self)
		
		self.parent = parent
		Ptolemy = parent
		print('Classical Parent', parent)
		self.output = Ptolemy.Philadelphos.setoutput
		
		# Tuple for base functions (Value, Units)
		# ie: (10, 'm')
		
		# > Pharos.Archimedes.Mechanics.Classical(parent=self).trythese()
		
		# List for Units
		# [[Numerator Units], [Denominator Units], [Acceleration Units]]
		
		# Returns:
		# Vectors : (value, vector, unitlist)
		
		self.units = [[], [], []]
		
		# Constant: [Value, Uncertainty, UVal, Units, Base SI Units, Name]
		self.constants = {
			'c': [299792458, None, None,
			      [['m'], ['s'], []], [['m'], ['s'], []],
			      'Speed of Light in a Vacuum'],
			
			'G': [Decimal(6.67384e-11), Decimal(4.7e-5), 31,
			      [['m^3'], ['kg', 's'], []], [['m^3'], ['kg', 's'], []],
			      'Newtonian Gravity Constant'],
			
			'g': [9.80665, None, None,
			      [['m'], ['s', 's'], []], [['m'], ['s', 's'], []],
			      'Gravity on the surface of Earth'],
		}
	
	def clearunits(self):
		self.units = [[], [], []]
	
	def makelist(self):
		
		pass
	
	def speed(self, ddistance, dtime, unitlist=None):
		if unitlist:
			unitlist[0].append(ddistance[1])
			unitlist[1].append(dtime[1])
		
		speed = (ddistance[0] / dtime[0], unitlist)
		
		return speed
	
	def displacementV(self, distance, vector, unitlist=None):
		if unitlist:
			unitlist[0].append(distance[1])
		
		displacement = (distance[0], vector, unitlist)
		
		return displacement
	
	def velocityV(self, displacementV, dtime, unitlist=None):
		if displacementV[2]:
			unitlist = displacementV[2]
		unitlist[1].append(dtime[1])
		
		velocity = (displacementV[0] / dtime[0], displacementV[1], unitlist)
		
		return velocity
	
	def accelerationV(self, dvelocityV, dtime, unitlist=None):
		if dvelocityV[2]:
			unitlist = dvelocityV[2]
		unitlist[1].append(dtime[1])
		
		acceleration = (dvelocityV[0] / dtime[0], dvelocityV[1], unitlist)
		return acceleration
	
	def forceV(self, accelerationV, mass, unitlist=None):
		if accelerationV[2]:
			unitlist = accelerationV[2]
		unitlist[0].append(mass[1])
		
		force = (mass[0] * accelerationV[0], accelerationV[1], unitlist)
		return force
	
	def trythese(self):
		
		thisone = self.forceV(
			self.accelerationV(
				self.velocityV(
					self.displacementV(
						(45, 'm'), (75, 'deg'), self.units),
					(1, 's'), self.units),
				(1, 's'), self.units),
			(1, 'kg'), self.units)
		
		self.output("ATTENTION ONLOOKERS\n" + str(thisone))
		return thisone
	
	def gravityV(self, m1, m2=None, r=None, unitlist=None):
		G = self.constants['G'][0]
		g = self.constants['g'][0]
		
		unitlist = [['m'], ['s'], ['s']]
		
		if m2:
			gravity = ((G * ((m1 * m2) / r ** 2)), -90, unitlist)
			
			pass
		
		else:
			gravity = ((g * m1), -90, unitlist)
		
		return gravity
		pass
	
	def newtons1stlaw(self):
		
		pass
	
	def newtons2ndlaw(self):
		
		pass


C = Classical()