import ConfigParser
from random import randrange

import pygame
import game_objects
import game_effects

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BOARD_WIDTH = 80
BOARD_HEIGHT = 50
CELL_WIDTH = WINDOW_WIDTH / BOARD_WIDTH
CELL_HEIGHT = WINDOW_HEIGHT / BOARD_HEIGHT
LEFT, RIGHT, UP, DOWN = range(4)

num_players = 1
player_colors = {
    '1': pygame.Color(0, 255, 0),
    '2': pygame.Color(0, 0, 255),
    '3': pygame.Color(255, 0, 255),
    '4': pygame.Color(0, 128, 128),
}

players = []
apples = []
walls = []
missiles = []
effects = []
log_screen = game_objects.LogScreen()

# Load config variables
config = ConfigParser.SafeConfigParser()
config.read('snake.ini')
config.read('local.ini')
flags = 0
if config.getboolean('snake', 'full_screen'):
    flags |= pygame.FULLSCREEN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)


def load_level(level):
    reset()
    layout = level.layout.split('\n')[1:]
    for y, row in enumerate(layout):
        for x, column in enumerate(row):
            if column == 'W':
                walls.append(game_objects.Wall(x, y))
            if column == 'I':
                walls.append(game_objects.IndestructableWall(x, y))
            elif column in ('1', '2', '3', '4'):
                if int(column) <= num_players:
                    players.append(game_objects.Player('Player %s' % column, x, y,
                        level.player_directions[column], player_colors[column]))

    for i in range(level.num_apples):
        add_apple()

def get_collidables(exclude=None):
    collidables = []
    for player in players:
        if not player.is_dead:
            for parts in player.parts:
                collidables.append(parts)
    collidables.extend(walls)
    collidables.extend(missiles)

    if isinstance(exclude, game_objects.GameObject) and exclude in collidables:
        collidables.remove(exclude)

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
    global players, apples, walls, missiles, effects, log_screen

    players = []
    apples = []
    walls = []
    missiles = []
    effects = []
    log_screen = game_objects.LogScreen()

def add_apple():
    a = game_objects.Apple(randrange(BOARD_WIDTH), randrange(BOARD_HEIGHT))
    if a.collides_with(get_collidables()):
        add_apple()
    else:
        apples.append(a)




