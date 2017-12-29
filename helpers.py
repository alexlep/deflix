from math import ceil
from yaml import load, dump

def parseLevel(levelFile):
    try:
        with open(levelFile) as level_file:
            level_data = load(level_file)
            level_file.close()
    except ValueError as ve:
        print "Error in level file {0}: {1}".format(levelFile, ve)
        level_file.close()
        sys.exit(1)
    except IOError as ie:
        print "Error in opening level file {0}: {1}".format(levelFile, ie)
        sys.exit(1)
    level = draftClass(level_data)
    for item in level.__dict__.keys():
        if type(getattr(level, item)) is dict:
            setattr(level, item, draftClass(getattr(level, item)))
	return level

class draftClass:
	def ololo(self):
		for i in self.__dict__:
			print self.__dict__[i], type(self.__dict__[i])

	def __init__(self, dictdata = dict()):
		self.__dict__.update(dictdata)

	def updateWithDict(self, dictdata):
		self.__dict__.update(dictdata)

	def getTeleportOut(self, x, y):
		for t in self.teleports:
			if t["in"] == [x, y]:
				return t["out"]

	def expandPaths(self):
		for key in self.__dict__.keys():
			try:
				setattr(self, key, os.path.expanduser(getattr(self, key)))
			except:
				pass


class Point(object):
	def __init__(self, x, y, endPoint=False, split=False, wander=False):
		try:
			self.x = int(ceil(x))
			self.y = int(ceil(y))
		except TypeError:
			self.x = int(x)
			self.y = int(y)
		self.endPoint = endPoint
		self.split = split
		self.wander = wander

	def getCoordPair(self, xRatio=None, yRatio=None):
		return (self.x, self.y)

	def __unicode__(self):
		return "({1},{2})".format(self.x, self.y)

class Line(object):
	def __init__(self, aP, bP):
		self.aP = aP
		self.bP = bP

	def points(self):
		return (self.aP, self.bP)
