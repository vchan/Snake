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
    def __init__(self, x, y, color):
        super(Apple, self).__init__(x, y, color)
        self.color_change = (0, 30, 0)

    def update(self):
        if self.color[1] > 200:
            self.color_change = (0, -30, 0)
        elif self.color[1] <= 0:
            self.color_change = (0, 30, 0)

        self.color = (self.color[0]+self.color_change[0], self.color[1]+self.color_change[1], self.color[2]+self.color_change[2])

class Wall(GameObject):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y, (192, 192, 192))

class Player(object):
    def __init__(self, name, x, y, direction, color):
        self.name = name
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
        self.parts = deque()
        self.parts.append(SnakePart(self.x, self.y, color))
        self.grow = False
        self.is_dead = False

    def update(self):
        if self.is_dead:
            return

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
            self.is_dead = True
            return

        # Check if player ate an apple
        for apple in game.apples:
            if apple.rect.colliderect(head.rect):
                game.apples.remove(apple)
                game.add_apple()
                self.grow = True
                game.log_screen.add(self.name + " grew!")

        self.parts.append(head)

        # Pop the tail
        if self.grow:
            self.grow = False
        else:
            self.parts.popleft()

        # Reset any locks
        self._lock_set_direction = False

    def draw(self):
        if self.is_dead:
            return

        for part in self.parts:
            part.draw()

    def set_direction(self, direction):
        if self._lock_set_direction:
            return

        if (direction == game.LEFT and self.direction != game.RIGHT) or \
            (direction == game.RIGHT and self.direction != game.LEFT) or \
            (direction == game.UP and self.direction != game.DOWN) or \
            (direction == game.DOWN and self.direction != game.UP):
            self.direction = direction
            self._lock_set_direction = True

class LogScreen(object):
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("verdana", 12)
        self.log = deque()
        self.size = 5

    def draw(self):
        for i, text in enumerate(self.log):
            text = self.font.render(text, 1, (255, 255, 255))
            textpos = text.get_rect(top = 20 + i*20, left = game.WINDOW_WIDTH-150)
            game.screen.blit(text, textpos)

    def add(self, text):
        self.log.append(text)
        if len(self.log) > self.size:
            self.log.popleft()
