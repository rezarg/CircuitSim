import pygame, time

from logic import Block, drawConnection, init as initLogic
from data import encodeData, decodeData, init as initData
from button import Button

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
m2 = False
connecting = False
buttons = []
suppressClicks = False

blockTypes = ["and", "nand", "or", "nor", "xor", "xnor", "t_flip-flop", "LED-W", "LED-R", "LED-G", "LED-B"]
blockLabels = ["and", "nand", "or", "nor", "xor", "xnor", "TFF", "LED W", "LED R", "LED G", "LED B"]
currentBlockType = 0
blocks: list[Block] = []

initLogic(window, font, blocks)
initData(blocks)

def addTuple(t1: tuple, t2: tuple) -> tuple:
	res = []
	for i in range(len(t1)):
		res.append(t1[i] + t2[i])
	return tuple(res)

for i in range(len(blockTypes)):
	buttonSize = (72, 32)
	y = (window.get_height() - len(blockTypes) * buttonSize[1]) / 2 + i * buttonSize[1] + 2
	newButton = Button(blockLabels[i], (4, y), addTuple(buttonSize, (-4, -4)), (32, 32, 48))
	newButton.margin = 2
	def action(blockType=i):
		global currentBlockType
		currentBlockType = blockType
	newButton.action1 = action
	buttons.append(newButton)

while RUNNING:
	mouseDX, mouseDY = 0, 0
	mouseX, mouseY = addTuple(pygame.mouse.get_pos(), (-camX, -camY))

	suppressClicks = False
	for event in pygame.event.get():
		suppressClicks = any([button.check(event) for button in buttons])
		if event.type == pygame.QUIT:
			open("save-backup.txt", "w+").write(encodeData())
			RUNNING = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_e:
				for logic in blocks:
					if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
						logic.value = not logic.value
						break
			elif event.key == pygame.K_i:
				decodeData(input("Enter block data: "))
			elif event.key == pygame.K_o:
				encodeData()
			elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
				TPS += 5
				if TPS > 1000: TPS = 1000
			elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
				TPS -= 5
				if TPS < 5: TPS = 5
		if event.type == pygame.MOUSEBUTTONDOWN and not suppressClicks:
			dragStartX, dragStartY = mouseX, mouseY
			if event.button == 1:
				for logic in blocks:
					if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
						break
				else:
					Block(blockTypes[currentBlockType], mouseX, mouseY)
			elif event.button == 2:
				for logic in blocks:
					bounding = 8
					if logic.x - bounding < mouseX < logic.x + bounding and logic.y - bounding < mouseY < logic.y + bounding:
						for x in blocks:
							if logic in x.inputs:
								x.inputs.remove(logic)
						blocks.remove(logic)
						del logic
						break
					for input in logic.inputs:
						centerX, centerY = (logic.x + input.x) / 2, (logic.y + input.y) / 2
						if centerX - bounding < mouseX < centerX + bounding and centerY - bounding < mouseY < centerY + bounding:
							logic.inputs.remove(input)
							break
			elif event.button == 3:
				m2 = True
				for logic in blocks:
					if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
						connecting = True
						break
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 3:
				m2 = False
				connecting = False
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

	mouseDX, mouseDY = addTuple(pygame.mouse.get_pos(), (-lastMousePos[0], -lastMousePos[1]))

	window.fill((0, 0, 0))

	if m2 and connecting: drawConnection(dragStartX, dragStartY, mouseX, mouseY, camX, camY)
	elif m2: camX += mouseDX; camY += mouseDY
	
	doTick = time.time() - lastTick > 1 / TPS
	for block in blocks:
		block.drawInputs(camX, camY)
		if doTick: block.updateIn()
	for block in blocks:
		block.draw(camX, camY)
		if doTick: block.updateOut()
	if doTick: lastTick = time.time()

	pygame.draw.rect(window, (128, 128, 128), (mouseX-8+camX, mouseY-8+camY, 16, 16), 1)

	for i in range(len(buttons)):
		button = buttons[i]
		if i == currentBlockType: button.color = (64, 64, 72)
		else: button.color = (32, 32, 48)
		button.draw(window)

	text = font.render("TPS: " + str(TPS), True, (255, 255, 255))
	window.blit(text, (window.get_width() - text.get_width() - 4, 4))

	lastMousePos = pygame.mouse.get_pos()

	pygame.display.flip()

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