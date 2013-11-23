import heapq
import time
from collections import deque

import pygame

from process import AIProcess
import game

VISUALIZE = False

class Node(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.f_score = 0
        self.g_score = 0
        self.h_score = 0
        self.width = game.CELL_WIDTH
        self.height = game.CELL_HEIGHT
        self.rect = pygame.Rect(x*self.width, y*self.height, self.width, self.height)

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
        if not self.path or self.goal != self.get_closest_apple()[1]:
            self.goal = self.get_closest_apple()[1]
            self.path = self.a_star(self.goal)
            if not self.path:
                return
        next_move = self.path.pop()
        if next_move[0] > self.player.x and self.player.direction != game.RIGHT:
            self.press_right()
        elif next_move[0] < self.player.x and self.player.direction != game.LEFT:
            self.press_left()
        elif next_move[1] < self.player.y and self.player.direction != game.UP:
            self.press_up()
        elif next_move[1] > self.player.y and self.player.direction != game.DOWN:
            self.press_down()

    def get_closest_apple(self):
        """ Returns closest apple and its distance to player. """
        return min((self.dist_between(self.player, apple), apple) for apple in self.apples)

    def dist_between(self, node1, node2):
        """ Calculate the least number of steps between node1 and node2. Takes into
            account board wrapping but not obstacles. """
        distance_x = abs(node2.x - node1.x)
        distance_y = abs(node2.y - node1.y)
        return min(distance_x, game.BOARD_WIDTH - distance_x) + \
            min(distance_y, game.BOARD_HEIGHT - distance_y)

    def a_star(self, goal):
        start = Node(self.player.x, self.player.y)
        goal = Node(goal.x, goal.y)
        closed_set = set() # The set of nodes already evaluated
        open_heap = [start] # The set of tentative nodes to be evaluated
        came_from = {} # The map of navigated nodes

        start.g_score = 0 # Cost from start along best known path
        start.h_score = self.heuristic_cost_estimate(start, goal)
        # Estimated total cost from start to goal through y
        start.f_score = start.g_score + start.h_score

        while open_heap:
            current = heapq.heappop(open_heap)
            if current == goal:
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
            if VISUALIZE:
                pygame.display.flip()
        # No path found

    def get_walkable_neighbors(self, node):
        """ Evaluate the node's 4 neighbors and return the walkable ones. """
        def check_node(x, y):
            # Account for board wrapping
            if x < 0:
                x = game.BOARD_WIDTH-1
            if x >= game.BOARD_WIDTH:
                x = 0
            if y < 0:
                y = game.BOARD_HEIGHT-1
            if y >= game.BOARD_HEIGHT:
                y = 0
            if self.board[x][y] not in ('W', 'S', 'M'):
                return Node(x, y)

        for offset in (-1, 1):
            neighbor = check_node(node.x + offset, node.y)
            if neighbor:
                yield neighbor
            neighbor = check_node(node.x, node.y + offset)
            if neighbor:
                yield neighbor

    def heuristic_cost_estimate(self, start, goal):
        return self.dist_between(start, goal) * 8

    def reconstruct_path(self, came_from, current_node):
        path = deque()
        while current_node in came_from:
            path.append(current_node)
            current_node = came_from[current_node]
        return path
