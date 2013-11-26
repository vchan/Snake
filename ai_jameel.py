from process import AIProcess

import game

from random import randint

import time

class JameelAI(AIProcess):
    
    def __init__(self, player_index, *args, **kwargs):
        super(JameelAI, self).__init__(player_index, *args, **kwargs)
        self.lastx = -1
        self.lasty = -1
        self.count = 0
        self.starttime = 0

    def execute(self):

        '''
        self.player
        current_milli_time = lambda: int(round(time.time() * 1000))
        self.count += 1
        if current_milli_time() - self.starttime > 100:
            print ".", self.count
            self.count = 0
            self.starttime = current_milli_time()
        self.count += 1
        if self.count == 200:
            self.count = 0
            print "---------"
        return
        if self.player.x == self.lastx and self.player.y == self.lasty:
            self.count += 1
            return
        else:
            print self.count
            self.count = 0
            self.lastx = self.player.x
            self.lasty = self.player.y

        return

    	moved = False
    	val = randint(1, 4)
    	if val == 1:
    		moved = True
    		self.press_up()
    	elif val == 2:
    		moved = True
    		self.press_down()
    	elif val == 3:
    		moved = True
    		self.press_left()
    	elif val == 4:
    		moved = True
    		self.press_right()

    	#if moved:
    	#		print self._player.x, ' = ', self._player.y
        '''
        pass

