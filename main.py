from pygame import *
import pygame, time, math

pygame.init()
pygame.font.init()

window = display.set_mode((1280, 720))
display.set_caption("Circuit Sim")

font = font.Font()

number = int | float

RUNNING = True
TPS = 100

mouseX, mouseY = 0, 0
dragStartX, dragStartY = 0, 0
lastTick = 0
m2 = False
connecting = False

blockTypes = ["and", "nand", "or", "nor", "xor", "xnor", "t_flip-flop", "LED"]
currentBlockType = 0
blocks = []

class Block:
	def __init__(self, type: str, x: number = 0, y: number = 0):
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
		
		draw.rect(window, color, (self.x-9, self.y-9, 18, 18))

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

def drawConnection(x1, y1, x2, y2, color = (128, 128, 128)):
	pygame.draw.line(window, color, (x1, y1), (x2, y2), 10)
	angle = math.atan2(y2-y1, x2-x1)
	text = font.render("> > >", True, (0, 0, 0))
	text = transform.rotate(text, -math.degrees(angle))
	textRect = text.get_rect(center=((x1+x2)/2, (y1+y2)/2))
	window.blit(text, textRect)

def encodeData():
	outputStr = ""
	for block in blocks:
		inputsStr = ",".join([f"{input.x},{input.y}" for input in block.inputs])
		outputStr += f"{block.type},{block.x},{block.y},{block.value},{inputsStr};"
	print(outputStr[:-1])
	return outputStr[:-1]

def decodeData(inputStr: str):
	if inputStr.strip() == "": return
	inputStr = inputStr.split(";")
	for blockData in inputStr:
		blockData = blockData.split(",")
		blockType = blockData[0]
		blockX = int(blockData[1])
		blockY = int(blockData[2])
		blockValue = bool(blockData[3])
		newBlock = Block(blockType, blockX, blockY)
		newBlock.value = blockValue
	for blockData in inputStr:
		blockData = blockData.split(",")
		blockX = int(blockData[1])
		blockY = int(blockData[2])
		thisBlock = None
		for block in blocks:
			if block.x == blockX and block.y == blockY:
				thisBlock = block
		if thisBlock is None: continue
		inputsStr = blockData[4:]
		inputs = []
		x, y = 0, 0
		for i in range(len(inputsStr)):
			inputStr = inputsStr[i]
			if inputStr == "": continue
			if i%2 == 0:
				x = int(inputStr)
			else:
				y = int(inputStr)
				for block in blocks:
					if block.x == x and block.y == y:
						inputs.append(block)
						break
		thisBlock.inputs = inputs

while RUNNING:
	for event in pygame.event.get():
		if event.type == QUIT:
			encoded = encodeData()
			open("save-backup.txt", "w+").write(encoded)
			RUNNING = False
		if event.type == KEYDOWN:
			if event.key == K_w:
				currentBlockType = (currentBlockType - 1) % len(blockTypes)
			elif event.key == K_s:
				currentBlockType = (currentBlockType + 1) % len(blockTypes)
			elif event.key == K_e:
				for block in blocks:
					if block.x - 10 < mouseX < block.x + 10 and block.y - 10 < mouseY < block.y + 10:
						block.value = not block.value
						break
			elif event.key == K_i:
				inputStr = input("Enter block data: ")
				decodeData(inputStr)
			elif event.key == K_o:
				encodeData()
			elif event.key == K_EQUALS or event.key == K_PLUS or event.key == K_KP_PLUS:
				TPS += 5
				if TPS > 1000: TPS = 1000
			elif event.key == K_MINUS or event.key == K_KP_MINUS:
				TPS -= 5
				if TPS < 5: TPS = 5
		if event.type == MOUSEBUTTONDOWN:
			dragStartX, dragStartY = mouseX, mouseY
			if event.button == 1:
				for block in blocks:
					if block.x - 10 < mouseX < block.x + 10 and block.y - 10 < mouseY < block.y + 10:
						break
				else:
					Block(blockTypes[currentBlockType], mouseX, mouseY)
			elif event.button == 2:
				for block in blocks:
					bounding = 8
					if block.x - bounding < mouseX < block.x + bounding and block.y - bounding < mouseY < block.y + bounding:
						for x in blocks:
							if block in x.inputs:
								x.inputs.remove(block)
						blocks.remove(block)
						del block
						break
					for input in block.inputs:
						centerX, centerY = (block.x + input.x) / 2, (block.y + input.y) / 2
						if centerX - bounding < mouseX < centerX + bounding and centerY - bounding < mouseY < centerY + bounding:
							block.inputs.remove(input)
							break
			elif event.button == 3:
				m2 = True
				for block in blocks:
					if block.x - 10 < mouseX < block.x + 10 and block.y - 10 < mouseY < block.y + 10:
						connecting = True
						break
		if event.type == MOUSEBUTTONUP:
			if event.button == 3:
				m2 = False
				connecting = False
				start = None
				end = None
				for block in blocks:
					if block.x - 10 < dragStartX < block.x + 10 and block.y - 10 < dragStartY < block.y + 10:
						start = block
						break
				for block in blocks:
					if block.x - 10 < mouseX < block.x + 10 and block.y - 10 < mouseY < block.y + 10:
						end = block
						break
				if start and end and start != end:
					if end not in start.inputs:
						end.inputs.append(start)
		if event.type == MOUSEMOTION:
			x, y = event.pos
			mouseX = x // 20 * 20 + 10
			mouseY = y // 20 * 20 + 10

	window.fill((0, 0, 0))

	if m2 and connecting:
		drawConnection(dragStartX, dragStartY, mouseX, mouseY)
	
	doTick = time.time() - lastTick > 1 / TPS

	for block in blocks:
		if doTick: block.updateIn()
		block.drawInputs()

	for block in blocks:
		block.draw()
		if doTick: block.updateOut()
	
	if doTick:
		lastTick = time.time()

	pygame.draw.rect(window, (128, 128, 128), (mouseX-8, mouseY-8, 16, 16), 1)

	for i in range(len(blockTypes)):
		window.blit(font.render(blockTypes[i], True, (255, 255, 255)), (26, i*24+4))
		if i == currentBlockType:
			draw.rect(window, (255, 255, 255), (4, i*24+3, 20, 20))
		else:
			draw.rect(window, (128, 128, 128), (4, i*24+4, 20, 20))

	text = font.render("TPS: " + str(TPS), True, (255, 255, 255))
	window.blit(text, (window.get_width() - text.get_width() - 4, 4))

	display.flip()

# ➖🟩🟩🟩
# ➖🟩🟩⬛
# ➖🟩🟩🟩
# ➖➖🟦➖⬜⬜
# ➖➖🟦🟩⬜⬛
# ➖➖🟦➖⬜⬜🟧
# ⬜⬜⬜🟦⬜⬜🟥
# ⬜⬜⬜⬜⬜
# ⬜⬜⬜⬜⬜
# ➖➖🟨
# ➖➖🟨🟨