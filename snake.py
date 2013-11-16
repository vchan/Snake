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
        self.num_players = 4
        self.load_level()

    def load_level(self):
        self.apples = [Apple(randrange(Game.BOARD_WIDTH), randrange(Game.BOARD_HEIGHT)) for i in range(80)]

        self.players = []
        for i in range(self.num_players):

            if i == 0:
                x, y, direction = 0, 0, Game.RIGHT
            elif i == 1:
                x, y, direction = Game.BOARD_WIDTH-1, Game.BOARD_HEIGHT-1, Game.LEFT
            elif i == 2:
                x, y, direction = 0, Game.BOARD_HEIGHT-1, Game.UP
            elif i == 3:
                x, y, direction = Game.BOARD_WIDTH-1, 0, Game.DOWN

            self.players.append(Player(x, y, direction))

    def update(self):
        for player in self.players:
            player.update()

    def draw(self):
        for player in self.players:
            player.draw()

        for apple in self.apples:
            pygame.draw.rect(self.screen, apple.color, apple.rect)

    def reset(self):
        self.load_level()

class Player():
    def __init__(self, x, y, direction):
        self.color = (0, 255, 0)
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

        # Check if player collided with herself
        if head.rect.collidelist([p.rect for p in self.parts]) != -1:
            Game().reset()
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

def main_loop():
    pygame.init()
    pygame.display.set_caption("Jason's Snake Game")
    clock = pygame.time.Clock()

    background = pygame.Surface(Game().screen.get_size()).convert()
    background.fill((0, 0, 0))

    player1_controls = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
    player2_controls = [K_a, K_d, K_w, K_s]
    player3_controls = [K_j, K_l, K_i, K_k]
    player4_controls = [K_f, K_h, K_t, K_g]

    while True:
        clock.tick(9)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_SPACE:
                    Game().players[0].grow = True
                elif event.key in player1_controls:
                    Game().players[0].set_direction(player1_controls.index(event.key))
                elif event.key in player2_controls and Game().num_players > 1:
                    Game().players[1].set_direction(player2_controls.index(event.key))
                elif event.key in player3_controls and Game().num_players > 2:
                    Game().players[2].set_direction(player3_controls.index(event.key))
                elif event.key in player4_controls and Game().num_players > 3:
                    Game().players[3].set_direction(player4_controls.index(event.key))

        Game().screen.blit(background, (0, 0))
        Game().update()
        Game().draw()
        pygame.display.flip()

if __name__ == '__main__':
    main_loop()
