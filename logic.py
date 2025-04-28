import pygame, math

window = None
font = None
blocks = None

def init(window_: pygame.Window, font_: pygame.font.Font, blocks_: list):
	global window, font, blocks
	window = window_
	font = font_
	blocks = blocks_

def drawConnection(x1, y1, x2, y2, color = (128, 128, 128)):
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

		blocks.append(self)
	
	def draw(self):
		typeColors = {
			"and": (128, 128, 255),
			"nand": (255, 32, 128),
			"or": (128, 255, 128),
			"nor": (255, 128, 32),
			"xor": (128, 255, 255),
			"xnor": (255, 255, 128),
			"t_flip-flop": (64, 64, 64),
			"LED": (64, 64, 64),
			"default": (255, 255, 255),
		}

		if self.type in typeColors:
			color = typeColors[self.type]
		else:
			color = typeColors["default"]
		
		if self.value:
			color = (255, 255, 255)
		
		pygame.draw.rect(window, color, (self.x-9, self.y-9, 18, 18))

	def drawInputs(self):
		for block in self.inputs:
			drawConnection(block.x, block.y, self.x, self.y, block.value and (255, 255, 255) or (128, 128, 128))

	def updateIn(self):
		if self.type == "and":
			self.nextValue = all(input.value for input in self.inputs) and len(self.inputs) > 0
		elif self.type == "nand":
			self.nextValue = not all(input.value for input in self.inputs) or len(self.inputs) == 0
		elif self.type == "or" or self.type == "LED":
			self.nextValue = any(input.value for input in self.inputs)
		elif self.type == "nor":
			self.nextValue = not any(input.value for input in self.inputs)
		elif self.type == "xor":
			self.nextValue = len([input for input in self.inputs if input.value]) % 2 == 1
		elif self.type == "xnor":
			self.nextValue = len([input for input in self.inputs if input.value]) % 2 == 0
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