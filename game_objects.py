from collections import deque
import pygame

import snake
Game = snake.Game

class Player():
    def __init__(self, x, y, direction, color):
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
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

        # Check if player is out of bounds
        if self.x < 0:
            self.x = Game.BOARD_WIDTH
        if self.x > Game.BOARD_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = Game.BOARD_HEIGHT
        if self.y > Game.BOARD_HEIGHT:
            self.y = 0

        # Check if player collided with herself or other players
        for player in Game().players:
            if head.rect.collidelist([part.rect for part in player.parts]) != -1:
                Game().players.remove(self)
                return

        # Check if player ate an apple
        for apple in Game().apples:
            if apple.rect.colliderect(head.rect):
                Game().apples.remove(apple)
                self.grow = True

        self.parts.append(head)

        # Pop the tail
        if self.grow:
            self.grow = False
        else:
            self.parts.popleft()

    def draw(self):
        for part in self.parts:
            pygame.draw.rect(Game().screen, self.color, part.rect)

    def set_direction(self, direction):
        if (direction == Game.LEFT and self.direction != Game.RIGHT) or \
            (direction == Game.RIGHT and self.direction != Game.LEFT) or \
            (direction == Game.UP and self.direction != Game.DOWN) or \
            (direction == Game.DOWN and self.direction != Game.UP):
            self.direction = direction

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
        self.is_glowing = False

    def update(self):
        # if self.is_glowing
        pass


        