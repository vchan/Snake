from multiprocessing import Process, Event
from ctypes import Structure, c_int, c_char

from pygame.locals import *

import game
import game_objects

player_controls = {
    0: [K_LEFT, K_RIGHT, K_UP, K_DOWN],
    1: [K_a, K_d, K_w, K_s],
    2: [K_j, K_l, K_i, K_k],
    3: [K_f, K_h, K_t, K_g],
}

class GameObject(Structure):
    _fields_ = [('x', c_int), ('y', c_int)]

    def __repr__(self):
        return '(%d, %d)' % (self.x, self.y,)

class MovableGameObject(Structure):
    _anonymous_ = ('game_object',)
    _fields_ = [('game_object', GameObject), ('direction', c_int)]

    def __repr__(self):
        return '(%d, %d) %d' % (self.x, self.y, self.direction,)

board = (c_char * game.BOARD_HEIGHT) * game.BOARD_WIDTH

class Serializer(object):
    def serialize_board(self, board, _board):
        for x, row in enumerate(board):
            for y, obj in enumerate(row):
                c = ' '
                if isinstance(obj, game_objects.Wall):
                    c = 'W'
                elif isinstance(obj, game_objects.IndestructableWall):
                    c = 'I'
                elif isinstance(obj, game_objects.Apple):
                    c = 'A'
                elif isinstance(obj, game_objects.SnakePart):
                    c = str(game.players.index(obj.player) + 1)
                elif isinstance(obj, game_objects.Missile):
                    c = 'M'
                _board[x][y] = c
        return _board

class AIProcess(Process):
    """ Wrapper class for a python process. """
    def __init__(self, player_index, board, players, apples, *args, **kwargs):
        super(AIProcess, self).__init__(*args, **kwargs)
        self.player_index = player_index
        self.input_queue = kwargs['args'][0]
        self.board = board
        self.apples = list(apples)
        self._players = players
        self.stop = Event()

    @property
    def player(self):
        return self._players[self.player_index]

    def run(self):
        while not self.stop.is_set():
            self.execute()

    def shutdown(self):
        self.stop.set()

    def _press(self, key):
        self.input_queue.put_nowait(key)

    def press_left(self):
        self._press(player_controls[self.player_index][0])

    def press_right(self):
        self._press(player_controls[self.player_index][1])

    def press_up(self):
        self._press(player_controls[self.player_index][2])

    def press_down(self):
        self._press(player_controls[self.player_index][3])

    def execute(self):
        """ Override this method to control your snake. Use a press_* function
            to submit a key press on behalf of the player. """
        pass
