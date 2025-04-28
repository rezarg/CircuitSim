from pygame import *
import pygame, time
import logic
from logic import Block, drawConnection, init as initLogic
from data import encodeData, decodeData, init as initData

pygame.init()
pygame.font.init()

window = display.set_mode((1280, 720))
display.set_caption("Circuit Sim")

font = font.Font()

RUNNING = True
TPS = 100

mouseX, mouseY = 0, 0
dragStartX, dragStartY = 0, 0
lastTick = 0
m2 = False
connecting = False

blockTypes = ["and", "nand", "or", "nor", "xor", "xnor", "t_flip-flop", "LED"]
currentBlockType = 0
blocks: list[Block] = []

initLogic(window, font, blocks)
initData(blocks)

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
				for logic in blocks:
					if logic.x - 10 < mouseX < logic.x + 10 and logic.y - 10 < mouseY < logic.y + 10:
						logic.value = not logic.value
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
		if event.type == MOUSEBUTTONUP:
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