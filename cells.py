import pygame
import pygame.gfxdraw
import math, random

from helpers import Point, Line
from cell import Cell
from consts import BG_COLOR, LVIOLET, BLUE, BLACK,\
				   YELLOW, ORANGE, VIOLET, RED, WHITE, GREEN,\
				   ECELL, GENERATOR, DEFLECTOR, MINE, BRICK, SDEFLECTOR,\
				   SBRICK, GREY, TIN, TOUT, RBRICK, RT, SHIFT

class EmptyCell(Cell):
	def __init__(self, xstart, ystart, size, cellType):
		super(EmptyCell, self).__init__(xstart, ystart, size, cellType)
		if cellType == MINE:
			self.hitLineHor = Line(self.getRatioStartCoords(0.3, 0.3),
						  self.getRatioStartCoords(0.7, 0.7))
			self.hitLineVer = Line(self.getRatioStartCoords(0.3, 0.7),
						  self.getRatioStartCoords(0.7, 0.3))
			pygame.gfxdraw.filled_circle(self.image,
										 self.radius, self.radius,
										 int(self.radius * 0.4), BLUE)
			pygame.gfxdraw.aacircle(self.image,
									self.radius, self.radius,
									int(self.radius * 0.4), BLUE)
			pygame.draw.line(self.image, BLUE,
							 (self.radius, self.size * 0.25),
							 (self.radius, self.size * 0.75), 1)
			pygame.draw.line(self.image, BLUE,
							 (self.size * 0.25, self.radius),
							 (self.size * 0.75, self.radius), 1)
			pygame.draw.line(self.image, BLUE,
							 (self.size * 0.3, self.size * 0.3),
							 (self.size * 0.7, self.size * 0.7), 1)
			pygame.draw.line(self.image, BLUE,
							 (self.size * 0.3, self.size * 0.7),
							 (self.size * 0.7, self.size * 0.3), 1)
			self.image.set_at((self.radius, self.radius), BLACK)
			self.counter = 10
			self.role = 1
		else:
			self.role = 0

	def changeRole(self):
		self.role = 3

	def update(self):
		if self.role == 3:
			self.BOOM()

	def BOOM(self):
		radius = random.randint (int(self.size * 0.1), int(self.size * 0.45))
		colors = [RED, ORANGE, WHITE, YELLOW]
		color = random.choice(colors)
		pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius,
									 radius, color)
		self.counter -= 1
		if self.counter == 0:
			self.role = 0
			self.defBG()

	def mineIntersect(self, startP, endP):
		res = False
		lasLine = Line(startP, endP)
		if (self.intersect(lasLine, self.hitLineHor))\
			or (self.intersect(lasLine, self.hitLineVer)):
			res = True
		return res

class Generator(Cell):
	def __init__(self, xstart, ystart, size, cellType):
		super(Generator, self).__init__(xstart, ystart, size, cellType)
		self.color = (255,255,0)
		self.startAngle = 180
		self.power = 100
		self.powerCounter = 1
		self.tempMax = 100
		self.temp = 0
		self.counter = 0
		self.powerWarn = 10
		self.minRad = int(self.radius * 0.15)
		self.maxRad = int(self.radius * 0.8)
		self.gStartP = Point(self.sP.x + size / 2, self.sP.y + size / 2)
		pygame.draw.rect(self.image, self.color, self.relRect, 1)
		pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius,
									 self.maxRad, (25,25,25))
		pygame.gfxdraw.aacircle(self.image, self.radius, self.radius,
								self.maxRad, BLACK)
		pygame.gfxdraw.aacircle(self.image, self.radius, self.radius,
								self.minRad, VIOLET)
		pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius,
									 self.minRad, VIOLET)

	def update(self):
		self.powerCounter += 1
		if self.powerCounter % 20 == 0:
			self.power -= 1

	def overHeat(self):
		self.temp += 1

	def coolDown(self):
		if self.temp != 0:
			self.temp -= 1

class RandomT(Cell):
	def __init__(self, xstart, ystart, size, cellType):
		super(RandomT, self).__init__(xstart, ystart, size, cellType)
		self.image.fill(RED)
		self.dist = 3
		self.rightRange = range(-85,86,1)
		self.leftRange = range(95,266,1)
		self.topRange = range(5,176,1)
		self.bottomRange = range(185,356,1)
		self.counter = 1
		self.previousAngle = False
		for x in range(self.size / self.dist):
			for y in range(self.size / self.dist):
				self.image.set_at((self.dist * x, self.dist * y), WHITE)
		pygame.draw.rect(self.image, WHITE, self.relRect, 1)

	def getRandom(self, point):
		tPoint, angle = False, False
		if self.counter % 4 == 0:
			tPoint, angle = self.getAngleAndPoint(point)
			self.counter = 1
		else:
			self.counter += 1
		return tPoint, angle

	def getAngleAndPoint(self, p):
		if p.x == self.sP.x:
			print "left"
			angle = random.choice(self.rightRange)
			tPoint = Point(self.eP.x, self.sP.y + self.size / 2,
						   split=True, wander=True)
		elif p.x == self.eP.x:
			print "right"
			angle = random.choice(self.leftRange)
			tPoint = Point(self.sP.x, self.sP.y + self.size / 2,
						   split=True, wander=True)
		elif p.y == self.sP.y:
			print "top"
			angle = random.choice(self.bottomRange)
			tPoint = Point(self.sP.x + self.size / 2, self.eP.y,
						   split=True, wander=True)
		elif p.y == self.eP.y:
			print "bottom"
			angle = random.choice(self.topRange)
			tPoint = Point(self.sP.x + self.size / 2, self.sP.y,
						   split=True, wander=True)
		return tPoint, angle

class Teleport(Cell):
	def __init__(self, cell, size, cellType, tOut=None):
		super(Teleport, self).__init__(size*cell[0],
									   size*cell[1],
									   size, cellType)
		if cellType == TIN:
			self.outCoords = Point(size*tOut[0] + self.radius + SHIFT,
								   size*tOut[1] + self.radius + SHIFT,
								   split=True)
		self.diff = 1
		self.rad = 0
		self.minRad = int(self.radius * 0.1)
		self.maxRad = self.radius - 2
		if self.cellType == TOUT:
			pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius,
										 self.maxRad, (25,25,25))
			pygame.gfxdraw.aacircle(self.image, self.radius, self.radius,
									self.maxRad, BLACK)
			pygame.gfxdraw.aacircle(self.image, self.radius, self.radius,
									self.minRad, LVIOLET)
			pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius,
										 self.minRad, LVIOLET)
		else:
			self.update()

	def update(self):
		if self.cellType == TIN:
			pygame.draw.rect(self.image, LVIOLET, self.relRect, 1)
			pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius,
										 self.maxRad, (25,25,25))
			pygame.gfxdraw.aacircle(self.image, self.radius, self.radius,
									self.maxRad, LVIOLET)
			self.rad += self.diff
			pygame.gfxdraw.aacircle(self.image, self.radius, self.radius,
									self.rad, WHITE)
			if self.rad == self.maxRad:
				self.diff = -1
			elif self.rad == self.minRad:
				self.diff = 1


class Deflector(Cell):
	def __init__(self, xstart, ystart, size, cellType):
		super(Deflector, self).__init__(xstart, ystart, size, cellType)
		self.Angle = random.choice(range(0,360,30))
		if self.cellType == SDEFLECTOR:
			self.counter = 12
		self.step = 15
		self.updateCoords()

	def updateCoords(self):
		self.tempAngle = self.Angle % 180
		self.coord1 = Point(self.radius + math.cos(-math.radians(self.tempAngle)) * self.radius,
					   		self.radius + math.sin(-math.radians(self.tempAngle)) * self.radius)
		self.coord2 = Point(self.radius + math.cos(-math.radians(self.tempAngle + 180)) * self.radius,
							self.radius + math.sin(-math.radians(self.tempAngle + 180)) * self.radius)
		self.absCoord1 = Point(self.sP.x + self.coord1.x,
							   self.sP.y + self.coord1.y)
		self.absCoord2 = Point(self.sP.x + self.coord2.x,
							   self.sP.y + self.coord2.y)
		self.image.fill(BG_COLOR)
		pygame.draw.rect(self.image, GREEN, self.relRect, 1)
		pygame.draw.line(self.image, GREEN,
						 self.coord1.getCoordPair(),
						 self.coord2.getCoordPair(), 4)

	def update(self):
		if self.cellType == SDEFLECTOR:
			self.counter -= 1
			if self.counter % 4 == 0:
				self.Angle += self.step
				self.updateCoords()
			if self.counter == 0:
				self.counter = 12
				self.Angle = self.Angle % 360

	def defIntersect(self, startP, endP):
		line1 = Line(startP, endP)
		line2 = Line(self.absCoord1, self.absCoord2)
		return self.intersect(line1, line2)

	def getIntersectP(self, startP, endP):
		line1 = Line(startP, endP)
		line2 = Line(self.absCoord1, self.absCoord2)
		return self.lineIntersection(line1, line2)

class Brick(Cell):
	def __init__(self, xstart, ystart, size, cellType):
		super(Brick, self).__init__(xstart, ystart, size, cellType)
		if cellType == BRICK:
			self.image.fill(YELLOW)
			self.dist = 3
			for x in range(self.size / self.dist):
				for y in range(self.size / self.dist):
					self.image.set_at((self.dist * x, self.dist * y), BLACK)
			pygame.draw.rect(self.image, ORANGE, self.relRect, 1)
		elif cellType == RBRICK:
			self.image.fill(ORANGE)
			self.dist = 3
			for x in range(self.size / self.dist):
				for y in range(self.size / self.dist):
					self.image.set_at((self.dist * x, self.dist * y), GREY)
		elif cellType == SBRICK:
			self.myfont = pygame.font.SysFont("terminus", 14)
			self.role = 1
			self.health = 101
			self.counter = 0
			self.dist = 5
			self.cracks = []
			self.refresh()

	def hit(self, fP):
		self.counter +=1
		if self.counter % 4 == 0:
			self.health -= 1
		if self.health % 20 == 0:
			p = Point(*map(lambda x: int(x % self.size), fP.getCoordPair()))
			self.cracks.append(self.genCrack(p))
		if self.health == 0:
			self.role = 0
			self.dist = int(self.size * 0.33)
			self.defBG()
		else:
			self.refresh(withCracks=True)

	def genCrack(self, firstP):
		crack = [firstP]
		for p in range(1):
			x = random.randint(0, self.size)
			y = random.randint(0, self.size)
			crack.append(Point(x,y))
		return crack

	def update(self):
		if self.cellType == SBRICK:
			if self.role == 1:
				self.refresh(withCracks=True)

	def refresh(self, withCracks=False):
		self.image.fill(GREY)
		for x in range(self.size / self.dist):
			for y in range(self.size / self.dist):
				self.image.set_at((self.dist * x, self.dist * y), BLACK)
		if withCracks:
			for crack in self.cracks:
				pygame.draw.lines(self.image,
								  (100,100,100), False,
								  map(lambda x: x.getCoordPair(), crack),
								  1)
		pygame.draw.rect(self.image, GREY, self.relRect, 1)
		label = self.myfont.render("{0}".format(self.health), 1, (255,255,0))
		self.image.blit(label, (0, 0))

	def newRefAngleTest(self, p, angle):
		if ((p.x == self.sP.x) or (p.x == self.eP.x)) \
			and ((p.y == self.sP.y) or (p.y == self.eP.y)):
			self.tempAngle = 0 # corner
			print "1"
		elif (p.x == self.sP.x) or (p.x == self.eP.x):
			self.tempAngle = 90 # left-right side
			print "2"
		else:
			print "point ({0},{1})".format(p.x, p.y)
			print "elem ({0},{1})".format(self.eP.x, self.eP.y)
			self.tempAngle = 0 # up-bottom
			print "3"
		return self.getReflAngle(p, angle)
	"""
	def getBrickHit(self, p):
		if ((p.x == self.sP.x) or (p.x == self.eP.x)) \
			and ((p.y == self.sP.y) or (p.y == self.eP.y)):
			hit = 3 # corner
		elif (p.x == self.sP.x) or (p.x == self.eP.x):
			hit = 1 # left-right side
		else:
			hit = 2 # up-bottom
		return hit

	def getReflAngle_(self, point, angle):
		angle = angle % 360
		hit = self.getBrickHit(point)
		if (hit == 1) or ((hit == 3) and (angle in range (0,46))) or \
			((hit == 3) and (angle in range (316, 360))) or \
			((hit == 3) and (angle in range (136,226))): # left_right'''
			if angle in range(180,270):
				reflectedAngle = 360 - math.fabs(angle - 180)
			elif angle in range(270,360):
				reflectedAngle = 180 + (360 - angle)
			else:
				reflectedAngle = math.fabs(180 - angle)
		elif (hit == 2) or ((hit == 3) and (angle in range (46, 136))) or \
			((hit == 3) and (angle in range (226, 316))):
			reflectedAngle = math.fabs(360 - angle)
		return reflectedAngle
	"""
