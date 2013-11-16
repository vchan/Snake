from random import randrange
from collections import deque

import pygame
from pygame.locals import *

import game_objects

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
        self.num_players = 3
        self.load_level()

    def load_level(self):
        self.apples = [game_objects.Apple(randrange(Game.BOARD_WIDTH), randrange(Game.BOARD_HEIGHT)) for i in range(80)]

        self.players = []
        for i in range(self.num_players):

            if i == 0:
                x, y, direction, color = 0, 0, Game.RIGHT, (0, 255, 0)
            elif i == 1:
                x, y, direction, color = Game.BOARD_WIDTH-1, Game.BOARD_HEIGHT-1, Game.LEFT, (0, 0, 255)
            elif i == 2:
                x, y, direction, color = 0, Game.BOARD_HEIGHT-1, Game.UP, (255, 0, 255)
            elif i == 3:
                x, y, direction, color = Game.BOARD_WIDTH-1, 0, Game.DOWN, (0, 128, 128)

            self.players.append(game_objects.Player(x, y, direction, color))

    def update(self):
        for player in self.players:
            player.update()

        for apple in self.apples:
            apple.update()

    def draw(self):
        for player in self.players:
            player.draw()

        for apple in self.apples:
            pygame.draw.rect(self.screen, apple.color, apple.rect)

    def reset(self):
        self.load_level()

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
