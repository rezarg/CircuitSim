import pygame

class Button:
	def __init__(self, label: str, position: tuple[int, int], size: tuple[int, int], color: tuple[int, int, int], action1: callable = None, action2: callable = None):
		self.label = label
		self.position = position
		self.size = size
		self.color = color
		self.action1 = action1
		self.action2 = action2

		self.bbcolor = pygame.Color((0, 0, 0))
		self.bbcolor.hsva = (hash(self.label) % 360, 100, 100, 100)

		self.fontSize = 16
		self.fontColor = (255, 255, 255)

		self.margin = 0
	
	def drawBoundingBox(self, window: pygame.Surface):
		pygame.draw.rect(window, self.bbcolor, (self.position[0]-self.margin, self.position[1]-self.margin, self.size[0]+self.margin*2, self.size[1]+self.margin*2))
	
	def draw(self, window: pygame.Surface):
		pygame.draw.rect(window, self.color, (self.position[0], self.position[1], self.size[0], self.size[1]))
		font = pygame.font.Font(None, self.fontSize)
		text = font.render(self.label, True, self.fontColor)
		text_rect = text.get_rect(center=(self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2))
		window.blit(text, text_rect)
	
	def check(self, event: pygame.event.Event) -> bool:
		if event.type != pygame.MOUSEBUTTONDOWN: return False
		mouseX, mouseY = event.pos
		inBB = self.position[0] - self.margin < mouseX < self.position[0] + self.size[0] + self.margin and self.position[1] - self.margin < mouseY < self.position[1] + self.size[1] + self.margin
		if event.button == 1 and inBB:
			if self.action1: self.action1()
			return True
		elif event.button == 3 and inBB:
			if self.action2: self.action2()
			return True