from collections import deque

import pygame

import game

class GameObject(object):
    def __init__(self, x, y, color):
        self.width = game.WINDOW_WIDTH / game.BOARD_WIDTH
        self.height = game.WINDOW_HEIGHT / game.BOARD_HEIGHT
        self.rect = pygame.Rect(x*self.width, y*self.height, self.width, self.height)
        self.color = color

    def draw(self):
        pygame.draw.rect(game.screen, self.color, self.rect)

    def update(self):
        raise NotImplemented('Not implemented')

class SnakePart(GameObject):
    def update(self):
        pass

class Apple(GameObject):
    def update(self):
        pass

class Wall(GameObject):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y, (192, 192, 192))

class Player(object):
    def __init__(self, x, y, direction, color):
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
        self.parts = deque()
        self.parts.append(SnakePart(self.x, self.y, color))
        self.grow = False

    def update(self):
        if self.direction == game.LEFT:
            self.x -= 1
        elif self.direction == game.RIGHT:
            self.x += 1
        elif self.direction == game.UP:
            self.y -= 1
        elif self.direction == game.DOWN:
            self.y += 1

        head = SnakePart(self.x, self.y, self.color)

        # Check if player is out of bounds
        if self.x < 0:
            self.x = game.BOARD_WIDTH-1
        if self.x >= game.BOARD_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = game.BOARD_HEIGHT-1
        if self.y >= game.BOARD_HEIGHT:
            self.y = 0

        # Check if player collided with herself or other players
        solid_objs = [parts for player in game.players for parts in player.parts] + game.walls
        if head.rect.collidelist([obj.rect for obj in solid_objs]) != -1:
            game.players.remove(self)
            return

        # Check if player ate an apple
        for apple in game.apples:
            if apple.rect.colliderect(head.rect):
                game.apples.remove(apple)
                self.grow = True

        self.parts.append(head)

        # Pop the tail
        if self.grow:
            self.grow = False
        else:
            self.parts.popleft()

    def draw(self):
        for part in self.parts:
            part.draw()

    def set_direction(self, direction):
        if (direction == game.LEFT and self.direction != game.RIGHT) or \
            (direction == game.RIGHT and self.direction != game.LEFT) or \
            (direction == game.UP and self.direction != game.DOWN) or \
            (direction == game.DOWN and self.direction != game.UP):
            self.direction = direction
