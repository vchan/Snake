import heapq
import time
from collections import deque

import pygame

from process import AIProcess
import game

VISUALIZE = True
OPPOSITE_DIRECTIONS = [game.RIGHT, game.LEFT, game.DOWN, game.UP,]
_DIRECTIONS = ['left', 'right', 'up', 'down']

class Node(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.f_score = 0
        self.g_score = 0
        self.h_score = 0

        width = game.CELL_WIDTH
        height = game.CELL_HEIGHT
        self.rect = pygame.Rect(x*width, y*height, width, height)

    def __lt__(self, other):
        """ Used by heapq for maintaining the priority queue. """
        if self.f_score == other.f_score:
            return self.h_score < other.h_score
        return self.f_score < other.f_score

    def __eq__(self, other):
        """ Used to compare nodes. Nodes are the same if their coordinates are
            the same."""
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        """ Used on members of hashed collections, i.e. sets and dictionaries.
            Here we want nodes to be unique by their coodinates in the
            closed_set. """
        return int('1%d%d' % (self.x, self.y))

    def __repr__(self):
        return '%d, %d, %d, %d' % (self.x, self.y, self.g_score, self.f_score)

    def get_coordinates(self):
        return (self.x, self.y)

    def draw(self, color):
        if VISUALIZE:
            pygame.draw.rect(game.screen, color, self.rect)

class VincentAI(AIProcess):
    def __init__(self, *args, **kwargs):
        super(VincentAI, self).__init__(*args, **kwargs)
        self.update_position()
        self.goal = None
        self.path = None

    def update_position(self):
        self.last_known_position = (self.player.x, self.player.y)

    def execute(self):
        if self.last_known_position == (self.player.x, self.player.y):
            # Player has not moved yet. No need to do anything.
            return
        self.update_position()
        if not self.path:
            apple = self.get_best_apples()[0][1]
            self.goal = Node(apple.x, apple.y)
            self.path = self.a_star(self.goal)
            if not self.path:
                return

        next_move = self.path.pop()
        player_node = Node(self.player.x, self.player.y)
        moved = False
        for direction in [game.LEFT, game.RIGHT, game.UP, game.DOWN,]:
            if self.get_node_in_direction(player_node, direction).get_coordinates() == next_move:
                moved = True
                if self.player.direction != direction:
                    getattr(self, 'press_%s' % _DIRECTIONS[direction])()
                break
        if not moved or self.reconsider_path():
            self.path = None

    def reconsider_path(self):
        if not self.path or self.board[self.goal.x][self.goal.y] != 'A':
            return True
        for i in range(-1, -6, -1):
            if i < -len(self.path):
                break
            step = self.path[i]
            x, y = step
            if self.board[x][y] in ('W', 'I', 'S', 'M',):
                return True
        return False

    def get_apples(self, player, apples=None):
        """ Returns list of apples sorted by distance from player. """
        apples = apples or self.apples
        apples = [(self.dist_between(player, apple), apple) for apple in apples]
        return sorted(apples)

    def get_players_apples(self):
        """ Get list of players and the their closest apples. """
        return [(player, self.get_apples(player)[0]) for player in self._players]

    def get_viable_apples(self):
        """ Filter out apples that are closer to other players than you. """
        apples = self.apples[:]
        for player, data in self.get_players_apples():
            dist, apple = data
            if player != self.player and apple in apples and dist <= self.dist_between(self.player, apple):
                apples.remove(apple)
        return apples

    def get_best_apples(self):
        """ Get apples from list of viable apples sorted by distance from
            player. """
        apples = self.get_viable_apples() or self.apples
        return self.get_apples(self.player, apples)

    def dist_between(self, node1, node2):
        """ Calculate the least number of steps between node1 and node2. Takes into
            account board wrapping but not obstacles. """
        distance_x = abs(node2.x - node1.x)
        distance_y = abs(node2.y - node1.y)
        return min(distance_x, game.BOARD_WIDTH - distance_x) + \
            min(distance_y, game.BOARD_HEIGHT - distance_y)

    def a_star(self, goal):
        start = Node(self.player.x, self.player.y)
        behind_node = self.get_node_in_direction(start, OPPOSITE_DIRECTIONS[self.player.direction])
        closed_set = set([behind_node,]) # The set of nodes already evaluated
        open_heap = [start] # The set of tentative nodes to be evaluated
        came_from = {} # The map of navigated nodes

        start.g_score = 0 # Cost from start along best known path
        start.h_score = self.heuristic_cost_estimate(start, goal)
        # Estimated total cost from start to goal through y
        start.f_score = start.g_score + start.h_score

        while open_heap:
            current = heapq.heappop(open_heap)
            if current == goal:
                if VISUALIZE:
                    pygame.display.flip()
                return self.reconstruct_path(came_from, goal.get_coordinates())
            closed_set.add(current)
            current.draw(pygame.Color(55, 55, 55))

            for neighbor in self.get_walkable_neighbors(current):
                tentative_g_score = current.g_score + self.dist_between(current, neighbor)
                tentative_h_score = self.heuristic_cost_estimate(neighbor, goal)
                tentative_f_score = tentative_g_score + tentative_h_score
                if neighbor in closed_set and tentative_f_score >= neighbor.f_score:
                    continue

                if neighbor not in open_heap or tentative_f_score < neighbor.f_score:
                    came_from[neighbor.get_coordinates()] = current.get_coordinates()
                    neighbor.g_score = tentative_g_score
                    neighbor.h_score = tentative_h_score
                    neighbor.f_score = tentative_f_score
                    if neighbor not in open_heap:
                        heapq.heappush(open_heap, neighbor)
                        neighbor.draw(pygame.Color(100, 100, 100))
        # No path found
        self.path = None

    def get_walkable_neighbors(self, node):
        """ Evaluate the node's 4 neighbors and return the walkable ones. """
        for direction in [game.LEFT, game.RIGHT, game.UP, game.DOWN,]:
            neighbor = self.get_node_in_direction(node, direction)
            x, y = neighbor.x, neighbor.y
            if self.board[x][y] not in ('W', 'I', 'S', 'M'):
                yield neighbor

    def heuristic_cost_estimate(self, start, goal):
        return self.dist_between(start, goal) * 0

    def reconstruct_path(self, came_from, current_node):
        path = deque()
        while current_node in came_from:
            path.append(current_node)
            current_node = came_from[current_node]
        return path

    def get_node_in_direction(self, node, direction):
        x, y = node.x, node.y
        if direction == game.LEFT:
            x -= 1
        elif direction == game.RIGHT:
            x += 1
        elif direction == game.UP:
            y -= 1
        elif direction == game.DOWN:
            y += 1

        # Account for board wrapping
        if x < 0:
            x = game.BOARD_WIDTH-1
        if x >= game.BOARD_WIDTH:
            x = 0
        if y < 0:
            y = game.BOARD_HEIGHT-1
        if y >= game.BOARD_HEIGHT:
            y = 0
        return Node(x, y)
