from random import randrange
from collections import deque

import pygame
from pygame.locals import *

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Game():
	__metaclass__ = Singleton
	WINDOW_WIDTH = 800
	WINDOW_HEIGHT = 600
	BOARD_WIDTH = 80
	BOARD_HEIGHT = 60
	LEFT, RIGHT, UP, DOWN = range(4)

	def __init__(self):
		self.screen = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT))
		self.apples = [Apple(randrange(Game.BOARD_WIDTH), randrange(Game.BOARD_HEIGHT)) for i in range(20)]
		self.snake = Snake()

	def update(self):
		self.snake.update()

	def draw(self):
		self.snake.draw()

		for apple in self.apples:
			pygame.draw.rect(self.screen, apple.color, apple.rect)

	def reset(self):
		self.__init__()


class Snake():
	def __init__(self):
		self.color = (0, 255, 0)
		self.x = 0
		self.y = 0
		self.direction = Game.RIGHT
		self.parts = deque()
		self.parts.append(SnakePart(self.x, self.y))
		self.grow = False

	def update(self):
		if self.direction == Game.LEFT:
			self.x -= 1
		elif self.direction == Game.RIGHT:
			self.x += 1
		elif self.direction == Game.UP:
			self.y -= 1
		elif self.direction == Game.DOWN:
			self.y += 1

		head = SnakePart(self.x, self.y)

		# Check if snake ate an apple		
		for apple in Game().apples:
			if apple.rect.colliderect(head.rect):
				Game().apples.remove(apple)
				self.grow = True

		# Check if snake collided with itself
		if head.rect.collidelist([p.rect for p in self.parts]) != -1:
			Game().reset()

		self.parts.append(head)

		# Pop the tail
		if self.grow:
			self.grow = False
		else:
			self.parts.popleft()

	def draw(self):
		for part in self.parts:
			pygame.draw.rect(Game().screen, self.color, part.rect)

class SnakePart():
	def __init__(self, x, y):		
		self.width = Game.WINDOW_WIDTH / Game.BOARD_WIDTH
		self.height = Game.WINDOW_HEIGHT / Game.BOARD_HEIGHT
		self.rect = pygame.Rect(x*self.width, y*self.height, self.width, self.height)

class Apple():
	def __init__(self, x, y):
		self.width = Game.WINDOW_WIDTH / Game.BOARD_WIDTH
		self.height = Game.WINDOW_HEIGHT / Game.BOARD_HEIGHT
		self.rect = pygame.Rect(x*self.width, y*self.height, self.width, self.height)
		self.color = (255, 0, 0)


def main():
	pygame.init()
	pygame.display.set_caption("Jason's Snake Game")
	clock = pygame.time.Clock()

	background = pygame.Surface(Game().screen.get_size()).convert()
	background.fill((0, 0, 0))

	while True:
		clock.tick(8)

		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					return
				elif event.key == K_SPACE:
					Game().snake.grow = True
				elif event.key == K_LEFT:
					Game().snake.direction = Game.LEFT
				elif event.key == K_RIGHT:
					Game().snake.direction = Game.RIGHT
				elif event.key == K_UP:
					Game().snake.direction = Game.UP
				elif event.key == K_DOWN:
					Game().snake.direction = Game.DOWN

		Game().screen.blit(background, (0, 0))
		Game().update()
		Game().draw()
		pygame.display.flip()

main()