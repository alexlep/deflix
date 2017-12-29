from pygame.sprite import Group as lGroup
from cells import EmptyCell, Brick, Generator, Teleport, RandomT, Deflector
from consts import ECELL, GENERATOR, DEFLECTOR, MINE, BRICK, SDEFLECTOR,\
				   SBRICK, GREY, TIN, TOUT, RBRICK, RT, SHIFT

class Field (object):
	def __init__(self, level, endPoint):
		self.level = level
		self.hor = len(self.level.field[0])
		self.ver = len(self.level.field)
		mx = max((self.hor, self.ver))
		self.cellSize = int((endPoint[0] - (SHIFT * 2) - 1) / mx)
		self.scrWidth = self.cellSize * self.hor
		self.scrHeight = self.cellSize * self.ver
		self.lcdStartP = (0 + SHIFT, self.scrHeight + 2)
		self.lcdHeight = endPoint[1] - self.scrHeight
		self.prepareGroups()
		self.matrix = self.prepareMatrix(self.level.field)
		self.g = self.genGroup.sprites()[0]

	def prepareGroups(self):
		self.defGroup = lGroup()
		self.genGroup = lGroup()
		self.brickGroup = lGroup()
		self.sBrickGroup = lGroup()
		self.mineGroup = lGroup()
		self.eCellGroup = lGroup()
		self.Tele = lGroup()
		self.groups = (self.genGroup, self.defGroup, self.mineGroup,
					   self.eCellGroup, self.brickGroup, self.sBrickGroup,
					   self.Tele)

	def matrixTemplate(self):
		"""
		Preparing template for matrix with empty values, to
		avoid issues with teleport out cells
		"""
		matrix = []
		for h in range(self.hor):
			matrix.append([0 for _ in range(self.ver)])
		return matrix

	def prepareMatrix(self, level):
		"""
		Filling matrix and sprite groups.
		Matrix is used for quick element search, since groups methods
		are not working as expected, and workaround with rect loops
		is not efficient.
		For teleports - out cells are taken from level configuration.
		"""
		matrix = self.matrixTemplate()
		for x in range(self.hor):
			for y in range(self.ver):
				try:
					cellType = int(level[y][x])
				except:
					cellType = str(level[y][x])
				if cellType in (ECELL, MINE):
					cell = EmptyCell(self.cellSize * x,
									 self.cellSize * y,
									 self.cellSize,
									 cellType)
					self.eCellGroup.add(cell)
				elif cellType == GENERATOR:
					cell = Generator(self.cellSize * x,
									 self.cellSize * y,
									 self.cellSize,
									 GENERATOR)
					self.genGroup.add(cell)
				elif cellType in (DEFLECTOR, SDEFLECTOR):
					cell = Deflector(self.cellSize * x,
									 self.cellSize * y,
									 self.cellSize,
									 cellType)
					self.defGroup.add(cell)
				elif cellType in (BRICK, RBRICK, SBRICK):
					cell = Brick(self.cellSize * x,
								 self.cellSize * y,
								 self.cellSize,
								 cellType)
					self.brickGroup.add(cell)
				elif cellType == TIN:
					outX, outY = self.level.getTeleportOut(x, y)
					cell = Teleport((x,y),
									self.cellSize,
								 	cellType,
									(outX, outY))
					self.Tele.add(cell)
					outCell = Teleport((outX, outY),
										   self.cellSize,
										   TOUT)
					self.Tele.add(outCell)
				elif cellType == RT:
					cell = RandomT(self.cellSize * x,
								   self.cellSize * y,
								   self.cellSize,
								   cellType)
					self.Tele.add(cell)
				matrix[x][y] = cell
				if cellType == TIN:
					matrix[outX][outY] = outCell
		return matrix

	def getCell(self, point):
		"""
		Quick search for element in matrix
		"""
		x = int(point.x / self.cellSize)
		y = abs(int(point.y / self.cellSize))
		return self.matrix[x][y]
	"""
	def getCell_(self, point):
		for g in self.groups:
			for s in g.sprites():
				if s.rect.collidepoint(point.getCoordPair()) != 0:
					#print s
					return s
		raise Exception("No cell found for point({0},{1})".format(*point.getCoordPair()))
		#print point.getCoordPair()
		#for g in self.groups:
		#	res = g.get_sprites_at(point.getCoordPair())
		#	if len(res):
		#		break
		#return res[0]
	"""
	def isPointOutOfScr(self, p):
		"""
		True if point is out of screen surface
		"""
		res = False
		if (p.x <= SHIFT) or (p.y <= SHIFT) or (p.x >= self.scrWidth) \
			or (p.y >= self.scrHeight):
			res = True
		return res

	def update(self):
		for g in self.groups:
			g.update()

	def draw(self, surface):
		for g in self.groups:
			g.draw(surface)
