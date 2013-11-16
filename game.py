from random import randrange

import pygame

import game_objects

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BOARD_WIDTH = 80
BOARD_HEIGHT = 50
LEFT, RIGHT, UP, DOWN = range(4)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
num_players = 4
players = []
apples = []
walls = []

player_colors = {
        1: (0, 255, 0),
        2: (0, 0, 255),
        3: (255, 0, 255),
        4: (0, 128, 128),
}

def load_level(level):
    layout = level.layout.split('\n')[1:-1]
    for y, row in enumerate(layout):
        for x, column in enumerate(row):
            if column == 'W':
                walls.append(game_objects.Wall(x, y))
            elif column in ('1', '2', '3', '4'):
                column = int(column)
                if column <= num_players:
                    players.append(game_objects.Player(x, y,
                        level.player_directions[column], player_colors[column]))

    apples.extend([game_objects.Apple(randrange(BOARD_WIDTH), randrange(BOARD_HEIGHT), (255, 0, 0)) for i in range(80)])

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

    for wall in walls:
        wall.draw()

def reset():
    load_level()

