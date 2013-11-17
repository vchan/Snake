import ConfigParser
from random import randrange

import pygame
import game_objects
import game_effects

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BOARD_WIDTH = 80
BOARD_HEIGHT = 50
LEFT, RIGHT, UP, DOWN = range(4)

players = []
apples = []
walls = []
missiles = []
effects = []

log_screen = game_objects.LogScreen()

player_colors = {
    '1': (0, 255, 0),
    '2': (0, 0, 255),
    '3': (255, 0, 255),
    '4': (0, 128, 128),
}

config = ConfigParser.SafeConfigParser()
config.read('snake.ini')
config.read('local.ini')
flags = 0
if config.getboolean('snake', 'full_screen'):
        flags |= pygame.FULLSCREEN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

def load_level(level):
    layout = level.layout.split('\n')[1:]
    for y, row in enumerate(layout):
        for x, column in enumerate(row):
            if column == 'W':
                walls.append(game_objects.Wall(x, y))
            elif column in ('1', '2', '3', '4'):
                if int(column) <= level.num_players:
                    players.append(game_objects.Player('Player %s' % column, x, y,
                        level.player_directions[column], player_colors[column]))

    for i in range(level.num_apples):
        add_apple()

def get_collidables():
    collidables = []
    for player in players:
        if not player.is_dead:
            for parts in player.parts:
                collidables.append(parts)

    collidables.extend(walls)
    collidables.extend(missiles)

    return collidables

def update():
    for obj in apples + missiles:
        obj.update()

    for player in players:
        if not player.is_dead:
            player.update()

def draw():
    for drawable in apples + walls + missiles:
        drawable.draw()

    for player in players:
        if not player.is_dead:
            player.draw()

    log_screen.draw()

def reset():
    load_level()

def add_apple():
    a = game_objects.Apple(randrange(BOARD_WIDTH), randrange(BOARD_HEIGHT))
    if a.collides_with(get_collidables()):
        add_apple()
    else:
        apples.append(a)
