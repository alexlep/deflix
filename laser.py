import pygame
import math
import random
from itertools import groupby
from helpers import Point, Line
from consts import VIOLET, RED, BLUE, ORANGE, WHITE, BLACK,\
				   ECELL, GENERATOR, DEFLECTOR, MINE, BRICK, SDEFLECTOR,\
				   SBRICK, TIN, TOUT, RBRICK, RT, SHIFT

class Laser(pygame.sprite.Sprite):
	def __init__(self, field):
		self.field = field
		self.recalc = True
		self.startAngle = field.g.startAngle
		self.cellSize = field.cellSize
		self.step = 3
		self.widthDiff = 1
		self.zeroP = Point(0, 0)
		self.cellP = Point(self.cellSize-1, self.cellSize-1)
		self.done = False
		self.diff = 1
		self.laserWidth = 4
		self.minWidth, self.maxWidth = self.laserWidth, 8
		self.screen = pygame.display.get_surface()

	def getFullPath(self, sP, angle):
		"""
		Prepares full laser path.
		Executes in loop checkLaserPath, which checks one direction for
		for one angle. Once direction is processed - last point and next angle
		are returned. If endPoint for last point is True - this is the last
		point in whole path. If new Angle is False - the angle is opposite,
		so overheat is starting.
		If wander parameter for some point in path is True - path is
		recalculated constantly, for example for spinning deflectors.
		If there are teleport point in the path - path is splitted into small
		chunks, anf laser laser is drawn by parts.
		"""
		path = [sP]
		self.overHeat = False
		while not path[-1].endPoint:
			point, angle = self.checkLaserPath(path[-1], angle)
			if isinstance(point, (tuple)):
				path.extend(point)
			else:
				path.append(point)
			if angle is False:
				self.overHeat = True
				break
		self.recalc = any(x.wander for x in path)
		teleports = [i for i in range(len(path)) if path[i].split]
		if teleports:
			res = self.splitPath(path, teleports)
		else:
			res = [path]
		return res

	def splitPath(self, path, ts):
		"""
		Splits path by teleport points
		https://stackoverflow.com/a/1198876
		"""
		return [path[i:j] for i, j in zip([0]+ts, ts+[None])]

	def drawLaser(self):
		"""
		Draws the laser on screen surface, by parts or whole at a time.
		Constantly recalculates the path, if spinning deflectors or random
		teleports are in the path.
		Activates/deactivates generator overheat.
		"""
		if self.recalc:
			self.path = self.getFullPath(self.field.g.gStartP,
									   self.field.g.startAngle)
		for route in self.path:
			width = self.getLaserWidth() if self.overHeat else self.minWidth
			pygame.draw.lines(self.screen,
						  VIOLET, False,
						  map(lambda x: x.getCoordPair(), route),
						  width)

		for route in self.path:
			for elem in route[1:-1]:
				pygame.gfxdraw.filled_circle(self.screen,
											 elem.x, elem.y,1,
											 random.choice([RED,ORANGE,WHITE]))

		if self.overHeat:
			self.field.g.overHeat()
		else:
			self.field.g.coolDown()

	def getLaserWidth(self):
		"""
		Simple helper to calculate laser dynamic width during overheat
		"""
		self.laserWidth += self.diff
		if self.laserWidth == self.maxWidth:
			self.diff = -1
		elif self.laserWidth == self.minWidth:
			self.diff = 1
		return self.laserWidth

	def getDestinaton(self, startP, angle, minP, maxP):
		angle = angle % 360
		radAngle = math.radians(angle)
		if 90 <= angle < 180:
			radAngle = math.radians(angle - 90)
			cathB = startP.y - minP.y
			cathA = cathB * math.tan(radAngle)
			if startP.x - cathA < minP.y:
				cathA = startP.x - minP.x
				cathB = cathA / math.tan(radAngle)
			position = (startP.x - cathA, startP.y - cathB)
		elif 180 <= angle < 270:
			cathA = startP.x - minP.x
			cathB = math.tan(radAngle) * cathA
			if startP.y + cathB > maxP.y:
				cathB = maxP.y - startP.y
				cathA = cathB / math.tan(radAngle)
			position = (startP.x - cathA, startP.y + cathB)
		elif 270 <= angle < 360:
			radAngle = math.radians(angle - 90)
			cathB = maxP.y - startP.y
			cathA = cathB * math.tan(radAngle)
			if startP.x + cathA > maxP.x:
				cathA = maxP.x - startP.x
				cathB = cathA / math.tan(radAngle)
			position = (startP.x + cathA, startP.y + cathB)
		elif 0 <= angle < 90:
			cathA = maxP.x - startP.x
			cathB = math.tan(radAngle) * cathA
			if startP.y - cathB < minP.x:
				cathB = startP.y - minP.y
				cathA = cathB / math.tan(radAngle)
			position = (startP.x + cathA, startP.y - cathB)
		return Point(*position)

	def getNextCellStartPoint(self, eP, angle):
		"""
		Gets start point of laser for the next cell
		"""
		step = 1
		nAngle = angle % 360
		if nAngle == 0:
			p = Point(eP.x + step, eP.y)
		elif nAngle == 90:
			p = Point(eP.x, eP.y - step)
		elif nAngle == 180:
			p = Point(eP.x - step, eP.y)
		elif nAngle == 270:
			p = Point(eP.x, eP.y + step)
		else:
			radAngle = -math.radians(nAngle)
			dX = step * math.cos(radAngle)
			dY = step * math.sin(radAngle)
			p = Point(eP.x + math.copysign(step, dX),
					  eP.y + math.copysign(step, dY))
		return p

	def pointAbsToRel(self, p):
		return Point(p.x % self.cellSize, p.y % self.cellSize)

	def getLastCellPoint(self, elem, fPoint, angle):
		"""
		Gets last point of laser in current cell
		"""
		diff = self.getDestinaton(self.pointAbsToRel(fPoint),
								  angle, self.zeroP, self.cellP)
		return Point(elem.sP.x + diff.x, elem.sP.y + diff.y)

	def checkLaserPath(self, sCellP, angle):
		workingP = sCellP
		nextP, refAngle = False, True
		while not nextP:
			#try:
			elem = self.field.getCell(workingP)
			#print workingP.getCoordPair(), elem, angle, elem.cellType

			#except:
			#	points[-1].endPoint = True
			#	break
			eCellP = self.getLastCellPoint(elem, workingP, angle)
			if (workingP == sCellP)\
				and (elem.cellType in (GENERATOR, RBRICK,
									   DEFLECTOR, SDEFLECTOR, RT)):
				workingP = self.getNextCellStartPoint(eCellP, angle)
				continue
			if elem.cellType == BRICK:
				nextP = workingP
				nextP.endPoint = True
			elif elem.cellType == SBRICK:
				if elem.role == 1:
					nextP = workingP
					nextP.wander = True
					elem.hit(workingP)
					nextP.endPoint = True
				else:
					workingP = self.getNextCellStartPoint(eCellP, angle)
					continue
			elif elem.cellType == RT:
				tPoint, refAngle = elem.getRandom(workingP)
				if not refAngle:
					nextP = workingP
					nextP.endPoint, nextP.wander = True, True
					refAngle = True
				else:
					nextP = (workingP, tPoint)
			elif elem.cellType == RBRICK:
				nextP = workingP
				refAngle = elem.newRefAngleTest(nextP, angle)
			elif (elem.cellType in (DEFLECTOR, SDEFLECTOR)) \
				and (elem.defIntersect(workingP, eCellP)):
				nextP = elem.getIntersectP(workingP, eCellP)
				if elem.cellType == SDEFLECTOR:
					nextP.wander = True
				refAngle = elem.getReflAngle(nextP, angle)
				if (int(refAngle % 180) == int(angle % 180)):
					nextP.endPoint = True
					refAngle = False
			elif (elem.cellType == MINE) and (elem.role == 1) and \
				(elem.mineIntersect(workingP, eCellP)):
					elem.changeRole()
			elif (elem.cellType == TIN):
				nextP = (workingP, elem.outCoords)
				refAngle = angle
			if nextP:
				return nextP, refAngle
			else:
				workingP = self.getNextCellStartPoint(eCellP, angle)
				if self.field.isPointOutOfScr(workingP):
					nextP = eCellP
					nextP.endPoint = True
		return nextP, angle
