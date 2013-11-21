from multiprocessing import Process, Event

import game

class AIProcess(Process):
    """ Wrapper class for a python process. """
    def __init__(self, *args, **kwargs):
        super(AIProcess, self).__init__(*args, **kwargs)
        self.data = kwargs['args'][0]
        self.input_queue = kwargs['args'][1]
        self.stop = Event()

    def run(self):
        while not self.stop.is_set():
            self.execute(**self.data[0])

    def shutdown(self):
        self.stop.set()

    def execute(self, board):
        """ Override this method to control your snake. Put a keypress value
        into the input queue to submit a move on behalf of your snake.
                E.g. self.input_queue.put_nowait(K_DOWN) """
        pass
