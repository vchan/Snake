from multiprocessing import Process, Event
from ctypes import Structure, c_int

from pygame.locals import *

import game
import game_objects

class GameObject(Structure):
    _fields_ = [('x', c_int), ('y', c_int)]

    def __repr__(self):
        return '(%d, %d)' % (self.x, self.y,)

class MovableGameObject(Structure):
    _anonymous_ = ('game_object',)
    _fields_ = [('game_object', GameObject), ('direction', c_int),
            ('length', c_int),]

    def __repr__(self):
        return '(%d, %d) %d' % (self.x, self.y, self.direction,)

class Serializer(object):
    def serialize_board(self, board, _board):
        for x, row in enumerate(board):
            for y, obj in enumerate(row):
                _board[x][y] = self.translate_board_obj(obj)
        return _board

    def translate_board_obj(self, obj):
        if isinstance(obj, game_objects.Wall):
            return 'W'
        elif isinstance(obj, game_objects.IndestructableWall):
            return 'I'
        elif isinstance(obj, game_objects.Apple):
            return 'A'
        elif isinstance(obj, game_objects.SnakePart):
            return 'S'
        elif isinstance(obj, game_objects.Missile):
            return 'M'
        return ' '

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
        self._press(game.player_controls[self.player_index][game.LEFT])

    def press_right(self):
        self._press(game.player_controls[self.player_index][game.RIGHT])

    def press_up(self):
        self._press(game.player_controls[self.player_index][game.UP])

    def press_down(self):
        self._press(game.player_controls[self.player_index][game.DOWN])

    def execute(self):
        """ Override this method to control your snake. Use a press_* function
            to submit a key press on behalf of the player. """
        pass
