import pygame, time

from logic import Block, drawConnection, init as initLogic
from data import encodeData, decodeData, init as initData
from button import Button
from help import howtouse

howtouse()

pygame.init()
pygame.font.init()

window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Circuit Sim")

font = pygame.font.Font()

RUNNING = True
TPS = 100

mouseX, mouseY = 0, 0
lastMousePos = (0, 0)
dragStartX, dragStartY = 0, 0
camX, camY, camZoom = 0, 0, 1
lastTick = 0
dragging = False
suppressClicks = False
lastFrame = time.time()

blockTypes = ["and", "nand", "or", "nor", "xor", "xnor", "rng", "t_flip-flop", "LED-W", "LED-R", "LED-G", "LED-B"]
blockLabels = ["and", "nand", "or", "nor", "xor", "xnor", "RNG", "TFF", "LED W", "LED R", "LED G", "LED B"]
currentBlockType = -1

toolTypes = ["select", "connect", "pulse", "pan", "move", "delete"]
toolLabels = ["select", "connect", "pulse", "pan", "move", "delete"]
currentToolType = 0

renderingMode = 1

blocks: list[Block] = []
selection: list[Block] = []
selectionCopy: list[Block] = []
buttonsLeft: list[Button] = []
buttonsRight: list[Button] = []

initLogic(window, font)
initData(blocks)

def addTuple(t1: tuple, t2: tuple) -> tuple:
	res = []
	for i in range(len(t1)):
		res.append(t1[i] + t2[i])
	return tuple(res)

def copySelection():
	global selectionCopy
	selectionCopy = []
	keyON: dict[Block, Block] = {} # Old -> New
	keyNO: dict[Block, Block] = {} # Old <- New
	for block in selection:
		newBlock = Block(block.type, block.x, block.y)
		newBlock.value = block.value
		newBlock.nextValue = block.nextValue
		selectionCopy.append(newBlock)
		keyON[block] = newBlock
		keyNO[newBlock] = block
	for block in selectionCopy:
		for x in keyNO[block].inputs:
			if x in keyON:
				block.inputs.append(keyON[x])

for i in range(len(blockTypes)):
	buttonSize = (72, 32)
	y = (window.get_height() - len(blockTypes) * buttonSize[1]) / 2 + i * buttonSize[1] + 2
	newButton = Button(blockLabels[i], (4, y), addTuple(buttonSize, (-4, -4)), (32, 32, 48))
	newButton.marginX = 8
	newButton.marginY = 4
	def action(blockType=i):
		global currentBlockType, currentToolType
		currentToolType = -1
		currentBlockType = blockType
	newButton.action1 = action
	buttonsLeft.append(newButton)

for i in range(len(toolTypes)):
	buttonSize = (72, 32)
	y = (window.get_height() - len(toolTypes) * buttonSize[1]) / 2 + i * buttonSize[1] + 2
	newButton = Button(toolLabels[i], (window.get_width() - buttonSize[0] - 4, y), addTuple(buttonSize, (-4, -4)), (32, 32, 48))
	newButton.marginX = 8
	newButton.marginY = 4
	def action(toolType=i):
		global currentToolType, currentBlockType
		currentBlockType = -1
		currentToolType = toolType
	newButton.action1 = action
	buttonsRight.append(newButton)

while RUNNING:
	thisFrame = time.time()
	deltaTime = thisFrame - lastFrame
	mouseDX, mouseDY = 0, 0
	mouseX, mouseY = addTuple(pygame.mouse.get_pos(), (-camX, -camY))

	if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
		mouseX = mouseX // 20 * 20 + 10
		mouseY = mouseY // 20 * 20 + 10

	suppressClicks = False
	for event in pygame.event.get():
		suppressClicks = any([button.check(event) for button in buttonsLeft]) or any([button.check(event) for button in buttonsRight])
		if event.type == pygame.QUIT:
			with open("save-backup.txt", "w+") as f: f.write(encodeData())
			RUNNING = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_i:
				decodeData(input("Enter block data: "))
			elif event.key == pygame.K_o:
				encodeData()
			elif event.key == pygame.K_s:
				fileName = input("Save file name: ").strip()
				if fileName == "": continue
				data = encodeData()
				with open(f"{fileName}.txt", "w+") as f: f.write(data)
			elif event.key == pygame.K_l:
				fileName = input("Load file name: ")
				with open(f"{fileName}.txt", "r") as f: decodeData(f.read())
			elif event.key == pygame.K_t:
				tpsInput = int(input("TPS: "))
				if not tpsInput: continue
				if tpsInput < 5: tpsInput = 5
				if tpsInput > 1000: tpsInput = 1000
				TPS = tpsInput
			elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
				TPS += 5
				if TPS > 1000: TPS = 1000
			elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
				TPS -= 5
				if TPS < 5: TPS = 5
			elif event.key == pygame.K_h:
				howtouse()
			elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
				for block in selection.copy():
					blocks.remove(block)
					selection.remove(block)
					del block
			elif event.key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LCTRL]:
				copySelection()
				print("Copied selection.")
			elif event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
				selection = selectionCopy.copy()
				for block in selection:
					block.x += 20
					block.y += 20
				blocks.extend(selection)
				print("Pasted selection.")
				copySelection()
			elif event.key == pygame.K_1:
				renderingMode = 1
			elif event.key == pygame.K_2:
				renderingMode = 2
			elif event.key == pygame.K_3:
				renderingMode = 3
		if event.type == pygame.MOUSEBUTTONDOWN and not suppressClicks:
			if event.button != 1: continue
			dragStartX, dragStartY = mouseX, mouseY
			dragging = True
			if currentBlockType != -1:
				for logic in blocks:
					if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
						break
				else:
					blocks.append(Block(blockTypes[currentBlockType], mouseX, mouseY))
			elif currentToolType != -1:
				if toolTypes[currentToolType] == "connect":
					for logic in blocks:
						if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
							connecting = True
							break
				elif toolTypes[currentToolType] == "pulse":
					for logic in blocks:
						if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
							logic.value = not logic.value
							break
				elif toolTypes[currentToolType] == "delete":
					for logic in blocks:
						bounding = 8
						if logic.x - bounding < mouseX < logic.x + bounding and logic.y - bounding < mouseY < logic.y + bounding:
							for x in blocks:
								if logic in x.inputs:
									x.inputs.remove(logic)
							blocks.remove(logic)
							del logic
							break
						for block in logic.inputs:
							centerX, centerY = (logic.x + block.x) / 2, (logic.y + block.y) / 2
							if centerX - bounding < mouseX < centerX + bounding and centerY - bounding < mouseY < centerY + bounding:
								logic.inputs.remove(block)
								break
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button != 1: continue
			dragging = False
			if currentToolType != -1:
				if toolTypes[currentToolType] == "connect":
					start = None
					end = None
					for logic in blocks:
						if logic.x - 10 < dragStartX < logic.x + 10 and logic.y - 10 < dragStartY < logic.y + 10:
							start = logic
							break
					for logic in blocks:
						if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
							end = logic
							break
					if start and end and start != end:
						if end not in start.inputs:
							end.inputs.append(start)
				elif toolTypes[currentToolType] == "select":
					selection = []
					if mouseX > dragStartX:
						x1 = dragStartX
						x2 = mouseX
					else:
						x1 = mouseX
						x2 = dragStartX
					if mouseY > dragStartY:
						y1 = dragStartY
						y2 = mouseY
					else:
						y1 = mouseY
						y2 = dragStartY
					for block in blocks:
						if x1 < block.x < x2 and y1 < block.y < y2:
							selection.append(block)
				elif toolTypes[currentToolType] == "move":
					for block in selection:
						block.x = block.x // 20 * 20 + 10
						block.y = block.y // 20 * 20 + 10

	mouseDX, mouseDY = addTuple(pygame.mouse.get_pos(), (-lastMousePos[0], -lastMousePos[1]))

	window.fill((0, 0, 0))

	if dragging and currentToolType != -1:
		if toolTypes[currentToolType] == "connect": drawConnection(dragStartX, dragStartY, mouseX, mouseY, camX, camY)
		elif toolTypes[currentToolType] == "pan": camX += mouseDX; camY += mouseDY
		elif toolTypes[currentToolType] == "select":
			if mouseX > dragStartX:
				x = dragStartX
				w = mouseX - x
			else:
				x = mouseX
				w = dragStartX - x
			if mouseY > dragStartY:
				y = dragStartY
				h = mouseY - y
			else:
				y = mouseY
				h = dragStartY - y
			pygame.draw.rect(window, (128, 128, 128), (x+camX, y+camY, w, h), 1)
		elif toolTypes[currentToolType] == "move":
			for block in selection:
				block.x += mouseDX
				block.y += mouseDY
	
	doTick = time.time() - lastTick > 1 / TPS
	for block in blocks:
		if renderingMode == 1:
			block.drawInputs(camX, camY)
		if doTick: block.updateIn()
	for block in blocks:
		if renderingMode != 3 or block.type.startswith("LED"):
			block.draw(camX, camY)
		if doTick: block.updateOut()
	if doTick: lastTick = time.time()

	for block in selection:
		pygame.draw.rect(window, (0, 255, 255), (block.x-12+camX, block.y-12+camY, 24, 24), 2)

	pygame.draw.rect(window, (128, 128, 128), (mouseX-8+camX, mouseY-8+camY, 16, 16), 1)

	for i in range(len(buttonsLeft)):
		button = buttonsLeft[i]
		if i == currentBlockType: button.color = (64, 64, 72)
		else: button.color = (32, 32, 48)
		button.draw(window)

	for i in range(len(buttonsRight)):
		button = buttonsRight[i]
		if i == currentToolType: button.color = (64, 64, 72)
		else: button.color = (32, 32, 48)
		button.draw(window)

	text = font.render("TPS: " + str(TPS), True, (255, 255, 255))
	window.blit(text, (window.get_width() - text.get_width() - 4, 4))

	if deltaTime != 0: text = font.render("FPS: " + str(int(1/deltaTime)), True, (255, 255, 255))
	else: text = font.render("FPS: ?", True, (255, 255, 255))
	window.blit(text, (window.get_width() - text.get_width() - 4, 20))

	lastMousePos = pygame.mouse.get_pos()

	pygame.display.flip()
	lastFrame = thisFrame

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