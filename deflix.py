import pygame
from helpers import parseLevel
from field import Field
from laser import Laser
from pygame.sprite import GroupSingle as gs
from consts import RED, BG_COLOR, GREY, WHITE, GREEN, YELLOW, BLACK

screen_size = [800, 680]
levelFile = "./levels/level1.yaml"

class Cursor(pygame.sprite.Sprite):
	def __init__(self, screen, startPoint, size):
		super(Cursor, self).__init__()
		self.shift = size
		self.screen = screen
		self.rect = pygame.Rect(startPoint.getCoordPair(),
							    (self.shift, self.shift))
		self.move = [startPoint.x, startPoint.y]

	def update(self, control):
		if control == "up":
			self.move[1] -= self.shift
		elif control == "down":
			self.move[1] += self.shift
		elif control == "right":
			self.move[0] += self.shift
		elif control == "left":
			self.move[0] -= self.shift
		self.rect.topleft = self.move

	def draw(self):
		pygame.draw.rect(self.screen, RED, self.rect, 2)

class LCD(pygame.sprite.Sprite):
	def __init__(self, startP, w, h, g, screen):
		super(LCD, self).__init__()
		self.rect = pygame.Rect(startP, (w, h - 1))
		self.powerRect = pygame.Rect((10, 25), (204, 15))
		self.ohRect = pygame.Rect((10, 60), (204, 15))
		self.frameRect = pygame.Rect((0, 0),(w, h - 1))
		self.powerLine = pygame.Rect((12, 27),(200,11))
		self.ohLine = pygame.Rect((12, 62),(200,11))
		self.image = pygame.Surface((w, h - 1))
		self.g = g
		self.myfont = pygame.font.SysFont("terminus", 14)
		self.initLCD()

	def initLCD(self):
		self.image.fill(BG_COLOR, self.frameRect)
		pygame.draw.rect(self.image, GREY, self.frameRect, 4)
		ohLabel = self.myfont.render("OVERHEAT", 1, (255,255,0))
		healthLabel = self.myfont.render("HEALTH", 1, (255,255,0))
		self.image.blit(healthLabel, (10, 10))
		self.image.blit(ohLabel, (10, 45))
		pygame.draw.rect(self.image, WHITE, self.powerRect, 1)
		pygame.draw.rect(self.image, WHITE, self.ohRect, 1)

	def update(self):
		self.image.fill(BLACK, self.powerLine)
		self.powerLine.width = self.g.power * 2
		if self.g.power in range(70, 101):
			self.image.fill(GREEN, self.powerLine)
		elif self.g.power in range(30, 70):
			self.image.fill(YELLOW, self.powerLine)
		else:
			self.image.fill(RED, self.powerLine)
		self.image.fill(BLACK, self.ohLine)
		self.ohLine.width = self.g.temp * 2
		if self.g.temp in range(60, 101):
			self.image.fill(RED, self.ohLine)
		elif self.g.temp in range(10, 60):
			self.image.fill(YELLOW, self.ohLine)
		elif self.g.temp in range(0, 10):
			self.image.fill(GREEN, self.ohLine)

class Player(object):
	def __init__(self, screen, level):
		self.screen = screen
		self.field = Field(level,
						   (screen.get_width(), screen.get_height()))
		self.laser = Laser(self.field)
		self.lcd = LCD(self.field.lcdStartP,
					   self.field.scrWidth,
					   self.field.lcdHeight,
					   self.field.g,
					   self.screen)
		self.lcdG = gs(self.lcd)
		self.cursor = Cursor(screen,
							 self.field.g.sP,
							 self.field.g.size)
		self.step = 15

	def draw(self):
		self.drawField()
		self.cursor.draw()
		self.laser.drawLaser()
		self.lcdG.update()
		self.lcdG.draw(self.screen)

	def update(self, control):
		self.cursor.update(control)
		print control
		if control == "rotate_left":
			if pygame.sprite.spritecollide(self.cursor, self.field.genGroup, False):
				self.field.g.startAngle -= self.step
				print "boom"
				self.field.update()
			else:
				try:
					spr = pygame.sprite.spritecollide(self.cursor, self.field.defGroup, False)[0]
					spr.Angle += self.step
					spr.updateCoords()
				except IndexError:
					pass
			self.laser.recalc = True
		elif control == "rotate_right":
			if pygame.sprite.spritecollide(self.cursor,
										   self.field.genGroup,
										   False):
				self.field.g.startAngle += self.step
				self.field.update()
			else:
				try:
					spr = pygame.sprite.spritecollide(self.cursor,
													  self.field.defGroup,
													  False)[0]
					spr.Angle -= self.step
					spr.updateCoords()
				except IndexError:
					pass
			self.laser.recalc = True

	def drawField(self):
		#self.screen.fill(BG_COLOR)
		self.field.update()
		self.field.draw(self.screen)

	def remove(self, screen_rect):
		if not self.rect.colliderect(screen_rect):
			self.kill()


if __name__ == "__main__":
	pygame.display.init()
	pygame.font.init()
	pygame.display.set_caption("Deflix")
	screen = pygame.display.set_mode(screen_size)
	done = False
	clock = pygame.time.Clock()
	DefPlayer = Player(screen, parseLevel(levelFile=levelFile))

	SPIN_DICT = {pygame.K_LEFT  :	"left",
			 pygame.K_RIGHT : 	"right",
			 pygame.K_UP :		"up",
			 pygame.K_DOWN : 	"down",
			 pygame.K_COMMA :  "rotate_left",
			 pygame.K_PERIOD :  "rotate_right"}

	while not done:
		clock.tick(30)
		DefPlayer.draw()
		pygame.display.flip()
		for event in pygame.event.get():
			keys = pygame.key.get_pressed()
			if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
				done = True
			elif event.type == pygame.KEYDOWN:
				if event.key in SPIN_DICT.keys():
					DefPlayer.update(SPIN_DICT[event.key])

	pygame.quit()
