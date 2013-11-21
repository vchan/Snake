from multiprocessing import Process, Event

from pygame.locals import *

player_controls = {
    0: [K_LEFT, K_RIGHT, K_UP, K_DOWN],
    1: [K_a, K_d, K_w, K_s],
    2: [K_j, K_l, K_i, K_k],
    3: [K_f, K_h, K_t, K_g],
}

class AIProcess(Process):
    """ Wrapper class for a python process. """
    def __init__(self, player_index, *args, **kwargs):
        super(AIProcess, self).__init__(*args, **kwargs)
        self.player_index = player_index
        self.data = kwargs['args'][0]
        self.input_queue = kwargs['args'][1]
        self.stop = Event()

    def run(self):
        while not self.stop.is_set():
            self.execute(self.data[0]['players'][self.player_index], self.data[0]['board'])

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

    def execute(self, player, board):
        """ Override this method to control your snake. Use a press_* function
            to submit a key press on behalf of the player. """
        pass
