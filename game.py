import ConfigParser
import multiprocessing
from ctypes import c_char
from random import randrange, randint

import pygame
from pygame.locals import *
import game_objects
import game_effects
import process
serializer = process.Serializer()

NAME = "Battle Snake %i" % (randint(3, 9) * 1000)  # Choose a random futuristic-looking year :)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
SCOREBOARD_HEIGHT = 80
BOARD_WIDTH = 80
BOARD_HEIGHT = 45
CELL_WIDTH = WINDOW_WIDTH / BOARD_WIDTH
CELL_HEIGHT = (WINDOW_HEIGHT-SCOREBOARD_HEIGHT) / BOARD_HEIGHT
LEFT, RIGHT, UP, DOWN = range(4)

player_controls = {
    0: [K_LEFT, K_RIGHT, K_UP, K_DOWN],
    1: [K_a, K_d, K_w, K_s],
    2: [K_j, K_l, K_i, K_k],
    3: [K_f, K_h, K_t, K_g],
}

num_players = None
level = None
# player_colors = {
#     '1': pygame.Color(0, 255, 0),
#     '2': pygame.Color(0, 0, 255),
#     '3': pygame.Color(255, 0, 255),
#     '4': pygame.Color(0, 128, 128),
# }

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

# Set frame rate
frames_per_second = config.getint('snake', 'frames_per_second')

# Set full screen mode
flags = 0
if config.getboolean('snake', 'full_screen'):
    flags |= pygame.FULLSCREEN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)

ai_index = config.getint('snake', 'ai_index')
use_multiprocessing= config.getboolean('snake', 'use_multiprocessing')

class CollisionError(Exception):
    def __init__(self, collider, collidee):
        self.collider = collider
        self.collidee = collidee

class BoardRow(list):
    def __setitem__(self, key, value):
        if value and self.__getitem__(key):
            raise CollisionError(value, self.__getitem__(key))
        super(BoardRow, self).__setitem__(key, value)
        shared_board[board.index(self)][key] = serializer.translate_board_obj(value)

# Board in shared memory used by AI processes
shared_board = multiprocessing.Array(c_char * BOARD_HEIGHT,
        ((c_char * BOARD_HEIGHT) * BOARD_WIDTH)())

board = []
for i in range(BOARD_WIDTH):
    board.append(BoardRow([None,] * BOARD_HEIGHT))

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

def init_level():
    global players, apples, walls, missiles, effects, board, log_screen

    players = []
    apples = []
    walls = []
    missiles = []
    effects = []
    board = []
    log_screen = game_objects.LogScreen()

    for i in range(BOARD_WIDTH):
        board.append(BoardRow([None,] * BOARD_HEIGHT))

    # Load level
    level.parse_layout()

def add_apple():
    try:
        a = game_objects.Apple(randrange(BOARD_WIDTH), randrange(BOARD_HEIGHT))
    except CollisionError, ce:
        add_apple()
    else:
        apples.append(a)
