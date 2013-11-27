from process import AIProcess

import game
import sys
import time
import datetime
import heapq
import pygame
from random import randint

VISUALIZE = False
DEBUG = False

DIRECTION_SET = {}
DIRECTION_SET[game.LEFT]  = [(0,-1,game.UP),(0,1,game.DOWN),(-1,0,game.LEFT)]
DIRECTION_SET[game.RIGHT] = [(0,-1,game.UP),(0,1,game.DOWN),(1,0,game.RIGHT)]
DIRECTION_SET[game.UP]    = [(-1,0,game.LEFT),(1,0,game.RIGHT),(0,-1,game.UP)]
DIRECTION_SET[game.DOWN]  = [(-1,0,game.LEFT),(1,0,game.RIGHT),(0,1,game.DOWN)]


class Node(object):
    def __init__(self, x, y, direction, cost=0, hcost=0, fcost=0):
        self.parent = None
        self.x = x
        self.y = y
        self.cost  = cost
        self.hcost = hcost
        self.fcost = fcost
        self.direction = direction
        self.rect = pygame.Rect(self.x*game.CELL_WIDTH, self.y*game.CELL_HEIGHT, game.CELL_WIDTH, game.CELL_HEIGHT)

    def __gt__(self, other):
        if self.fcost == other.fcost:
            return self.hcost > other.hcost
        return self.fcost > other.fcost

    def __lt__(self, other):
        if self.fcost == other.fcost:
            return self.hcost < other.hcost
        return self.fcost < other.fcost

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return int('9%d%d' % (self.x, self.y))

    def __repr__(self):
        return '(%d %d %d, %d + %d = %d)' % (self.x, self.y, self.direction, self.cost, self.host, self.fcost)

    def distance(self, other):
        dt_x = abs(other.x - self.x)
        dt_y = abs(other.y - self.y)
        return min(dt_x, game.BOARD_WIDTH - dt_x) + min(dt_y, game.BOARD_HEIGHT - dt_y)

    def draw(self, color):
        if VISUALIZE:
            pygame.draw.rect(game.screen, color, self.rect)

def heuristic_cost_estimate( node1, node2 ):
    return node1.distance(node2) * 8

class JameelAI(AIProcess):

    def __init__(self, player, *args, **kwargs):
        super(JameelAI, self).__init__(*args, **kwargs)
        self.last_known_position = None
        self.previous_move = None
        self.update_position()
        self._goal = None
        self._path = None
        self.last_shot = 0

    def update_position(self):
        self.last_known_position = (self.player.x, self.player.y)

    def adjust_coordinates(self, x, y):
        return (x % game.BOARD_WIDTH, y % game.BOARD_HEIGHT)

    def calculate_distance(self, coordinates1, coordinates2):
        dt_x = abs(coordinates1[0] - coordinates2[0])
        dt_y = abs(coordinates1[1] - coordinates2[1])
        return min(dt_x, game.BOARD_WIDTH-dt_x) + min(dt_y, game.BOARD_HEIGHT-dt_y)

    def neighbor_nodes(self, x, y, direction):
        def is_okay(x, y):
            return self.board[x][y] not in ('W', 'S', 'M', "I")
        for (_x, _y, _direction) in DIRECTION_SET[direction]:
            _x, _y = self.adjust_coordinates( x+_x, y+_y )
            if is_okay(_x, _y):
                yield Node(_x, _y, _direction)

    def closest_apple(self, x, y):
        return min([(self.calculate_distance((x,y), (apple.x,apple.y)), apple) for apple in self.apples])[1]

    def closest_player(self, x, y):
        min([(self.calculate_distance((player.x, player.y), (x, y)), player) for player in self._players if player != self.player ])[1]

    def get_real_neighbor(self, openset, neighbor):
        try:
            real_neighbor = [ n for n in openset if n == neighbor ][0]
            return real_neighbor
        except IndexError:
            return neighbor


    def reconstruct_path(self, current):
        astar_path = []     
        currentNode = current
        astar_path.append((currentNode.x, currentNode.y, currentNode.direction))
        while currentNode.parent != None:
            currentNode = currentNode.parent
            astar_path.append((currentNode.x, currentNode.y, currentNode.direction))
        astar_path.pop()
        astar_path.reverse()
        return astar_path

    def astar(self, goal):

        self._goal = goal

        def is_apple(node):
            return self.board[node.x][node.y] == 'A'

        start = Node(self.player.x, self.player.y, self.player.direction)
        
        openset   = [start]
        closedset = set()

        start.cost  = 0
        start.hcost = goal.distance(start)
        start.fcost = start.cost + start.hcost
    
        start = time.time()

        while openset:
            current = heapq.heappop(openset)
            
            #if is_apple(current):
            #   goal = current

            if current == goal:
                return self.reconstruct_path(current)

            closedset.add(current)
            current.draw(pygame.Color(55, 55, 55))

            for neighbor in self.neighbor_nodes(current.x, current.y, current.direction):

                if self.time_passed() > 95000: #150000: 
                    break

                if is_apple(neighbor):
                    goal = neighbor
                    self._goal = goal

                tentative_cost  = current.cost + current.distance(neighbor)
                tentative_hcost = heuristic_cost_estimate(goal, neighbor)
                tentative_fcost = tentative_cost + tentative_hcost
                
                if neighbor in closedset and tentative_fcost >= neighbor.fcost:
                    continue

                neighbor_not_in_openset = neighbor not in openset
                if neighbor_not_in_openset or tentative_fcost < neighbor.fcost:
                    neighbor.parent    = current
                    neighbor.cost      = tentative_cost
                    neighbor.hcost     = tentative_hcost
                    neighbor.fcost     = tentative_cost + tentative_hcost

                    neighbor.direction = neighbor.direction
                    if neighbor_not_in_openset:
                        heapq.heappush(openset, neighbor)
                        neighbor.draw(pygame.Color(100, 100, 100))
                '''
                real_neighbor = self.get_real_neighbor(openset, neighbor)
                tentative_cost  = current.cost + current.distance(neighbor)
                tentative_hcost = heuristic_cost_estimate(goal, neighbor)
                tentative_fcost = tentative_cost + tentative_hcost
                if neighbor in closedset and tentative_fcost >= real_neighbor.fcost:
                    continue
                neighbor_not_in_openset = neighbor not in openset
                if neighbor_not_in_openset or tentative_fcost < real_neighbor.fcost:
                    real_neighbor.parent    = current
                    real_neighbor.cost      = tentative_cost
                    real_neighbor.hcost     = tentative_hcost
                    neighbor.fcost          = tentative_cost + tentative_hcost
                    real_neighbor.direction = neighbor.direction
                    if neighbor_not_in_openset:
                        heapq.heappush(openset, real_neighbor)
                        real_neighbor.draw(pygame.Color(100, 100, 100))
                '''
                
            if VISUALIZE:
                pygame.display.flip()

    def opponent_ahead(self, next_direction):
        if next_direction != self.player.direction:
            return False
        if self.player.direction == game.UP:
            for opponent in self.player_positions:
                if opponent[1] < self.player.y and self.player.x - 3 <= opponent[0] and opponent[0] <= self.player.x+3:
                    return True
        elif self.player.direction == game.DOWN:
            for opponent in self.player_positions:
                if opponent[1] > self.player.y and self.player.x-3 <= opponent[0] and opponent[0] <= self.player.x+3:
                    return True
        elif self.player.direction == game.LEFT:
            for opponent in self.player_positions:
                if opponent[0] < self.player.x and self.player.y-3 <= opponent[1] and opponent[1] <= self.player.y+3:
                    return True
        elif self.player.direction == game.RIGHT:
            for opponent in self.player_positions:
                if opponent[0] > self.player.x and self.player.y-3 <= opponent[1] and opponent[1] <= self.player.y+3:
                    return True
        return False

    def missile_will_strike(self, x, y):
        for missile in game.missiles:
            if missile.x == x and missile.direction in (game.UP, game.DOWN) and self.calculate_distance( (missile.x,missile.y), (x,y) ) <= 6:
                if DEBUG: print '+%d:' % self.player_index, "Will Strike", (missile.x, missile.y), (x,y), self.calculate_distance( (missile.x,missile.y), (x,y) ) 
                return True
            elif missile.y == y and missile.direction in (game.LEFT, game.RIGHT) and self.calculate_distance( (missile.x,missile.y), (x,y) ) <= 6:
                if DEBUG: print '+%d:' % self.player_index, "Will Strike", (missile.x, missile.y), (x,y), self.calculate_distance( (missile.x,missile.y), (x,y) ) 
                return True
            else:
                if DEBUG: print '+%d:' % self.player_index, "No Strike", (missile.x, missile.y), (x,y), self.calculate_distance( (missile.x,missile.y), (x,y) ) 
        return False

    def protect_urself(self, direction):


        def is_okay(x, y, strict=True):
            if strict:
                for opponents in self.player_positions:
                    if self.calculate_distance( (opponents[0],opponents[1]), (x,y) ) <= 6:
                        if DEBUG: print '+%d:' % self.player_index, opponents, (x,y), self.calculate_distance( (opponents[0],opponents[1]), (x,y) )
                        return False
                '''
                for x1 in (-1, 1):
                    if self.adjust_coordinates(x+x1, y) in self.player_positions:
                        return False
                for y1 in (-1, 1):
                    if self.adjust_coordinates(x, y+y1) in self.player_positions:
                        return False
                '''
            if self.missile_will_strike(x, y):
                return False
            return self.board[x][y] not in ('W', 'S', 'M', "I")

        modes = [True, False]
        if direction == game.UP:
            x,y = self.adjust_coordinates( self.player.x, self.player.y-1 )
        elif direction == game.DOWN:
            x,y = self.adjust_coordinates( self.player.x, self.player.y+1 )
        elif direction == game.LEFT:
            x,y = self.adjust_coordinates( self.player.x-1, self.player.y )
        elif direction == game.RIGHT:   
            x,y = self.adjust_coordinates( self.player.x+1, self.player.y )
        if DEBUG: print '+%d:' % self.player_index, "current:", (self.player.x, self.player.y), "error(x,y,direction)=", (x,y,direction), "board=[", self.board[x][y], "],", is_okay(x,y)
        if is_okay(x,y,True) == False:
            if DEBUG: print '+%d:' % self.player_index, "run Into Something [", self.board[x][y], "] current direction:", self.player.direction, "should direction:", direction
            for (_x, _y, _direction) in DIRECTION_SET[self.player.direction]:
                _x, _y = self.adjust_coordinates( self.player.x+_x, self.player.y+_y )
                for mode in modes:
                    if is_okay(_x, _y,mode):
                        if DEBUG: print '+%d:' % self.player_index, "new direction:", _direction, "current direction:", self.player.direction, "should direction:", direction
                        return _direction
            if DEBUG: print '+%d:' % self.player_index, "no Safe Move:"
        return direction

    def time_passed(self):
        return (datetime.datetime.now() - self.start).microseconds

    def execute(self):


        if self.last_known_position == (self.player.x, self.player.y):
            return
    
        if DEBUG: print '+%d:' % self.player_index, "enter execute"
        self.start = datetime.datetime.now()

        if DEBUG: 
            if self.calculate_distance( self.last_known_position, (self.player.x, self.player.y) ) > 1:
                print '+%d:' % self.player_index, "position change > 1:", self.last_known_position, (self.player.x, self.player.y)

        self.update_position()
        self.player_positions = [(self._players[i].x, self._players[i].y)  for i in range(len(self._players)) if i != self.player_index]
        
        #print self.player_positions, (self.player.x, self.player.y, self.player.direction), self.player_index
        
        goal = self.closest_apple(self.player.x, self.player.y)
        goal = Node(goal.x, goal.y, -1)
        
        if not self._path:
            self._path = self.astar(goal)
        else:
            if self.previous_move != None and self.previous_move != (self.player.x, self.player.y, self.player.direction):
                self._path = []
                self.previous_move = None
            if self._goal != None and self.board[self._goal.x][self._goal.y] != 'A':
                self._path = []
                self.previous_move = None

        if not self._path:
            next_direction = self.player.direction
        else:
            next_move = self._path.pop(0)
            self.previous_move = next_move
            next_direction = next_move[2]

        next_direction = self.protect_urself(next_direction)

        if DEBUG: print '+%d:' % self.player_index, "next_direction:", next_direction

        should_shoot = self.opponent_ahead(next_direction)
        if should_shoot:
            if time.time()-self.last_shot < 1:
                should_shoot = False
            else:
                self.last_shot = time.time()

        if next_direction != self.player.direction or should_shoot:
            if next_direction == game.UP:
                if DEBUG: print '+%d:' % self.player_index, "+sending up"
                self.press_up()
            elif next_direction == game.DOWN:
                if DEBUG: print '+%d:' % self.player_index, "+sending down"
                self.press_down()
            elif next_direction == game.LEFT:
                if DEBUG: print '+%d:' % self.player_index, "+sending left"
                self.press_left()
            elif next_direction == game.RIGHT:
                if DEBUG: print '+%d:' % self.player_index, "+sending right"
                self.press_right()
        else:
            pass

        if DEBUG: print '+%d:' % self.player_index, "exit execute, time_passed=",self.time_passed()

