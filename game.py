from random import randrange

import pygame

import game_objects

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_WIDTH = 80
BOARD_HEIGHT = 60
LEFT, RIGHT, UP, DOWN = range(4)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
num_players = 3
players = []

def load_level():
    global apples

    apples = [game_objects.Apple(randrange(BOARD_WIDTH), randrange(BOARD_HEIGHT), (255, 0, 0)) for i in range(80)]

    for i in range(num_players):
        if i == 0:
            x, y, direction, color = 0, 0, RIGHT, (0, 255, 0)
        elif i == 1:
            x, y, direction, color = BOARD_WIDTH-1, BOARD_HEIGHT-1, LEFT, (0, 0, 255)
        elif i == 2:
            x, y, direction, color = 0, BOARD_HEIGHT-1, UP, (255, 0, 255)
        elif i == 3:
            x, y, direction, color = BOARD_WIDTH-1, 0, DOWN, (0, 128, 128)
        players.append(game_objects.Player(x, y, direction, color))

def update():
    for player in players:
        player.update()

    for apple in apples:
        apple.update()

def draw():
    for player in players:
        player.draw()

    for apple in apples:
        apple.draw()

def reset():
    load_level()

