from pygame import Rect, Surface, font
from pygame.sprite import Sprite
from consts import BG_COLOR, LVIOLET, SHIFT
from helpers import Point, Line

class Cell(Sprite):
    def __init__(self, xstart, ystart, size, cellType):
        super(Cell, self).__init__()
        self.sP = Point(xstart + SHIFT, ystart + SHIFT)
        xend, yend = self.sP.x + size -1, self.sP.y + size -1
        #if xstart == 0:
        #    xend -= 1
        #if ystart == 0:
        #    yend -= 1
        self.eP = Point(xend, yend)
        self.size = size
        self.radius = int(self.size / 2)
        self.rect = Rect(self.sP.getCoordPair(),
        						(self.eP.x - self.sP.x,
        						 self.eP.y - self.sP.y))
        self.relRect = Rect((0, 0),
        						   (self.eP.x - self.sP.x,
        						    self.eP.y - self.sP.y))
        self.cellType = cellType
        self.center = Point(xstart + self.radius,
        			   ystart + self.radius)
        self.image = Surface((self.size, self.size))
        self.dist = int(self.size * 0.33)
        self.q1 = range(0,90)
        self.q2 = range(90,180)
        self.q3 = range(180,270)
        self.q4 = range(270,360)
        self.myfont = font.SysFont("arial", 10)
        self.defBG()

    def defBG(self):
    	self.image.fill(BG_COLOR)
    	for x in range(self.size / self.dist):
    		for y in range(self.size / self.dist):
    			self.image.set_at((self.dist * x, self.dist * y), LVIOLET)
    			#label2 = self.myfont.render("({0},{1})".format(self.rect.left, self.rect.top), 1, (255,255,0))
    			#label3 = self.myfont.render("({0},{1})".format(self.rect.right, self.rect.bottom), 1, (255,255,0))
    			#self.image.blit(label2, (0, 10))
    			#self.image.blit(label3, (0, 20))


    def getRatioStartCoords(self, xRatio, yRatio):
    	'''
    	for drawing line inside the cell
    	'''
    	return Point(self.sP.x + self.size * xRatio,
    				 self.sP.y + self.size * yRatio)

    def ccw(self, A, B, C):
    	return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

    def intersect(self, line1, line2):
    	return self.ccw(line1.aP,line2.aP,line2.bP) != self.ccw(line1.bP,line2.aP,line2.bP) and \
    		   self.ccw(line1.aP,line1.bP,line2.aP) != self.ccw(line1.aP,line1.bP,line2.bP)

    def lineIntersection(self, line1, line2):
    	xdiff = (line1.aP.x - line1.bP.x, line2.aP.x - line2.bP.x)
    	ydiff = (line1.aP.y - line1.bP.y, line2.aP.y - line2.bP.y)

    	def det(a, b):
    		return a[0] * b[1] - a[1] * b[0]

    	div = det(xdiff, ydiff)
    	if div == 0:
    	   raise Exception('lines do not intersect')

    	d = (det(*map(lambda x: x.getCoordPair(), line1.points())),
    		 det(*map(lambda x: x.getCoordPair(), line2.points())))
    	x = det(d, xdiff) / div
    	y = det(d, ydiff) / div
    	return Point(x, y)

    def getReflAngle(self, point, angle):
    	angle = angle % 360
    	revAngle = angle % 90
    	if angle in self.q4:
    		diff = revAngle + 90 - self.tempAngle
    		if diff < 0:
    			nAngle = self.tempAngle + 180 + abs(diff)
    		else:
    			nAngle = self.tempAngle + 180 - diff
    	elif angle in self.q3:
    		diff = revAngle - self.tempAngle
    		if diff < 0:
    			nAngle = self.tempAngle + 180 + abs(diff)
    		else:
    			nAngle = self.tempAngle + 180 - diff
    	elif angle in self.q2:
    		diff = 90 + revAngle - self.tempAngle
    		if diff < 0:
    			nAngle = self.tempAngle + abs(diff)
    		else:
    			nAngle = self.tempAngle - diff
    	elif angle in self.q1:
    		diff = revAngle - self.tempAngle
    		if diff < 0:
    			nAngle = self.tempAngle + abs(diff)
    		else:
    			nAngle = self.tempAngle - diff
    	return nAngle
