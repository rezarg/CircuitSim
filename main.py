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
dragStartX, dragStartY = 0, 0
lastTick = 0
m2 = False
connecting = False
buttons = []
suppressClicks = False

blockTypes = ["and", "nand", "or", "nor", "xor", "xnor", "t_flip-flop", "LED-W", "LED-R", "LED-G", "LED-B"]
blockLabels = ["&", "!&", "|", "!|", "^", "!^", "T", "W", "R", "G", "B"]
currentBlockType = 0
blocks: list[Block] = []

initLogic(window, font, blocks)
initData(blocks)

def subTuple(t1: tuple, t2: tuple) -> tuple:
	res = []
	for i in range(len(t1)):
		res.append(t1[i] - t2[i])
	return tuple(res)

for i in range(len(blockTypes)):
	tempBlock = Block(blockTypes[i], 0, 0)
	newButton = Button(blockLabels[i], (4, i*24+4), (20, 20), tempBlock.colorOff)
	newButton.fontColor = subTuple((255, 255, 255), tempBlock.colorOn)
	newButton.margin = 2
	def action(blockType=i):
		global currentBlockType
		print("Selected block type:", blockType)
		currentBlockType = blockType
	newButton.action1 = action
	buttons.append(newButton)
	blocks.remove(tempBlock)
	del tempBlock

while RUNNING:
	suppressClicks = False
	for event in pygame.event.get():
		for button in buttons:
			if button.check(event):
				suppressClicks = True
				break
		if event.type == pygame.QUIT:
			encoded = encodeData()
			open("save-backup.txt", "w+").write(encoded)
			RUNNING = False
			quit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				currentBlockType = (currentBlockType - 1) % len(blockTypes)
			elif event.key == pygame.K_s:
				currentBlockType = (currentBlockType + 1) % len(blockTypes)
			elif event.key == pygame.K_e:
				for logic in blocks:
					if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
						logic.value = not logic.value
						break
			elif event.key == pygame.K_i:
				inputStr = input("Enter block data: ")
				decodeData(inputStr)
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
		if event.type == pygame.MOUSEMOTION:
			x, y = event.pos
			mouseX = x // 20 * 20 + 10
			mouseY = y // 20 * 20 + 10

	window.fill((0, 0, 0))

	if m2 and connecting: drawConnection(dragStartX, dragStartY, mouseX, mouseY)
	
	doTick = time.time() - lastTick > 1 / TPS
	for block in blocks:
		block.drawInputs()
		if doTick: block.updateIn()
	for block in blocks:
		block.draw()
		if doTick: block.updateOut()
	if doTick: lastTick = time.time()

	pygame.draw.rect(window, (128, 128, 128), (mouseX-8, mouseY-8, 16, 16), 1)

	for button in buttons:
		button.draw(window)

	#for i in range(len(blockTypes)):
	#	window.blit(font.render(blockTypes[i], True, (255, 255, 255)), (26, i*24+4))
	#	if i == currentBlockType:
	#		pygame.draw.rect(window, (255, 255, 255), (4, i*24+3, 20, 20))
	#	else:
	#		pygame.draw.rect(window, (128, 128, 128), (4, i*24+4, 20, 20))

	text = font.render("TPS: " + str(TPS), True, (255, 255, 255))
	window.blit(text, (window.get_width() - text.get_width() - 4, 4))

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