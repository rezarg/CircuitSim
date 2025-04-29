import pygame, math, random

window = None
font = None
blocks = None

typeColorsOff = {
	"default": (192, 192, 192),
	"and": (128, 128, 255),
	"nand": (192, 0, 64),
	"or": (128, 255, 128),
	"nor": (255, 128, 32),
	"xor": (128, 255, 255),
	"xnor": (255, 255, 128),
	"rng": (192, 128, 48),
	"t_flip-flop": (48, 48, 48),
	"LED-W": (48, 48, 48),
	"LED-R": (48, 32, 32),
	"LED-G": (32, 48, 32),
	"LED-B": (32, 32, 48),
}

typeColorsOn = {
	"default": (255, 255, 255),
	"and": (0, 0, 255),
	"nand": (255, 64, 192),
	"or": (192, 255, 192),
	"nor": (255, 255, 128),
	"xor": (0, 255, 255),
	"xnor": (255, 255, 0),
	"rng": (255, 192, 128),
	"t_flip-flop": (192, 192, 192),
	"LED-W": (255, 255, 255),
	"LED-R": (255, 0, 0),
	"LED-G": (0, 255, 0),
	"LED-B": (0, 0, 255),
}

def init(window_: pygame.Window, font_: pygame.font.Font, blocks_: list):
	global window, font, blocks
	window = window_
	font = font_
	blocks = blocks_

def drawConnection(x1, y1, x2, y2, camX, camY, color=(128, 128, 128)):
	x1, y1 = x1 + camX, y1 + camY
	x2, y2 = x2 + camX, y2 + camY
	pygame.draw.line(window, color, (x1, y1), (x2, y2), 10)
	angle = math.atan2(y2-y1, x2-x1)
	text = font.render("> > >", True, (0, 0, 0))
	text = pygame.transform.rotate(text, -math.degrees(angle))
	textRect = text.get_rect(center=((x1+x2)/2, (y1+y2)/2))
	window.blit(text, textRect)

class Block:
	def __init__(self, type: str, x: int = 0, y: int = 0):
		self.type = type
		self.x = x
		self.y = y

		self.inputs = []

		self.powerBefore = False
		self.value = False
		self.nextValue = False

		if type in typeColorsOff: self.colorOff = typeColorsOff[type]
		else: self.colorOff = typeColorsOff["default"]
		if type in typeColorsOn: self.colorOn = typeColorsOn[type]
		else: self.colorOn = typeColorsOn["default"]

		blocks.append(self)
	
	def draw(self, camX, camY):
		if self.value: color = self.colorOn
		else: color = self.colorOff
		pygame.draw.rect(window, color, (self.x-9+camX, self.y-9+camY, 18, 18))

	def drawInputs(self, camX, camY):
		for block in self.inputs:
			drawConnection(block.x, block.y, self.x, self.y, camX, camY, block.value and (255, 255, 255) or (128, 128, 128))

	def updateIn(self):
		if self.type == "and":
			self.nextValue = all(input.value for input in self.inputs) and len(self.inputs) > 0
		elif self.type == "nand":
			self.nextValue = not all(input.value for input in self.inputs) or len(self.inputs) == 0
		elif self.type == "or" or self.type.startswith("LED-"):
			self.nextValue = any(input.value for input in self.inputs)
		elif self.type == "nor":
			self.nextValue = not any(input.value for input in self.inputs)
		elif self.type == "xor":
			self.nextValue = len([input for input in self.inputs if input.value]) % 2 == 1
		elif self.type == "xnor":
			self.nextValue = len([input for input in self.inputs if input.value]) % 2 == 0
		elif self.type == "rng":
			self.nextValue = any(input.value for input in self.inputs) or random.randint(0, 1)
		elif self.type == "t_flip-flop":
			power = any(input.value for input in self.inputs)
			if power and not self.powerBefore:
				self.powerBefore = True
				self.nextValue = not self.value
			elif not power:
				self.powerBefore = False
				self.nextValue = self.value

	def updateOut(self):
		self.value = self.nextValue