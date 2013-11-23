from collections import deque
from heapq import heappush, heappop

import pygame
from pygame.locals import *

import game
import game_objects

def normalize_coordinate(c):
    x, y = c
    if x < 0:
        x += game.BOARD_WIDTH
    if y < 0:
        y += game.BOARD_HEIGHT
    if x >= game.BOARD_WIDTH:
        x -= game.BOARD_WIDTH
    if y >= game.BOARD_HEIGHT:
        y -= game.BOARD_HEIGHT
    return (x, y)

def draw_node(node, color):
    pygame.draw.rect(game.screen, color, pygame.Rect(node[0]*game.CELL_WIDTH, node[1]*game.CELL_HEIGHT, game.CELL_WIDTH, game.CELL_HEIGHT))

def is_apple(node):
    return isinstance(game.board[node[0]][node[1]], game_objects.Apple)

def is_valid_coordinate(c):
    return 0 <= c[0] < game.BOARD_WIDTH and 0 <= c[1] < game.BOARD_HEIGHT

class AStar(object):
    def __init__(self):
        self.open_set = set()  # We use set for fast membership tests
        self.open_heap = []  # We use heap for fast min checks
        self.closed_set = set()
        self.nodes = {}

        self.enable_visualization = True
        self.enable_wrap_coordinates = False
        self.retarget_alternate_goals = True

    def retrace_path(self, node):
        if self.nodes[node]['parent'] is None:
            return [node]
        else:
            return self.retrace_path(self.nodes[node]['parent']) + [node]

    def open_set_add(self, node):
        heappush(self.open_heap, (self.nodes[node]['f'], self.nodes[node]['h'], node))
        self.open_set.add(node)

    def open_set_remove(self, node):
        self.open_heap.remove((self.nodes[node]['f'], self.nodes[node]['h'], node))
        self.open_set.remove(node)

    def open_set_pop_lowest_f_score(self):
        node = heappop(self.open_heap)[2]
        self.open_set.remove(node)
        return node

    def is_traversable(self, node):
        return game.board[node[0]][node[1]] is None or is_apple(node)

    def is_alternate_goal(self, node):
        return is_apple(node)

    def movement_cost(self, node1, node2):
        return 1

    def heuristic_estimate_cost(self, start, goal):
        x_distance = abs(start[0]-goal[0])
        y_distance = abs(start[1]-goal[1])
        if self.enable_wrap_coordinates:
            x_distance = min(x_distance, game.BOARD_WIDTH - x_distance)
            y_distance = min(y_distance, game.BOARD_HEIGHT - y_distance)
        return (x_distance + y_distance)

    def get_path(self, start, goal):
        path = []

        # Add start node to the open set
        h = self.heuristic_estimate_cost(start, goal)
        self.nodes[start] = {'g': 0, 'h': h, 'f': h, 'parent': None}
        self.open_set_add(start)        
 
        while self.open_set:
            # Choose lowest f-score in the open list. Use h-score as a tie-breaker
            current = self.open_set_pop_lowest_f_score()
            self.closed_set.add(current)
            if current == goal:
                path = self.retrace_path(current)
                break

            # Draw the closed set
            if self.enable_visualization:
                draw_node(current, pygame.Color("green"))

            # Get neighbors
            neighbors = []
            direction_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, right, up, down
            for ox, oy in direction_offsets:
                neighbor = (current[0]+ox, current[1]+oy) 
                if self.enable_wrap_coordinates:
                    neighbor = normalize_coordinate(neighbor)
                if is_valid_coordinate(neighbor) and self.is_traversable(neighbor):
                    neighbors.append(neighbor)

            # Calculate path scores
            for neighbor in neighbors:
                g = self.nodes[current]['g'] + self.movement_cost(current, neighbor)
                if neighbor in self.open_set and g < self.nodes[neighbor]['g']:
                    self.open_set_remove(neighbor)
                if neighbor in self.closed_set and g < self.nodes[neighbor]['g']:
                    self.closed_set.remove(neighbor)
                if neighbor not in self.open_set and neighbor not in self.closed_set:
                    h = self.heuristic_estimate_cost(neighbor, goal)
                    self.nodes[neighbor] = {'g': g, 'h': h, 'f': g+h, 'parent': current}
                    self.open_set_add(neighbor)
                    # Draw the open set
                    if self.enable_visualization:
                        draw_node(neighbor, pygame.Color("cyan"))
                # If we find a different goal we like, return the path to it.
                if self.retarget_alternate_goals and neighbor != goal and self.is_alternate_goal(neighbor):
                    path = self.retrace_path(neighbor)
                    break

        # Draw the final path
        if self.enable_visualization:
            for p in path:
                draw_node(p, pygame.Color("red"))
            pygame.display.flip()

        return path

class JasonAI(AStar):
    def __init__(self, player):
        super(JasonAI, self).__init__()
        self.player = player
        self.current_goal = None  # Coordinates of where the snake is currently headed - (x, y)
        self.current_path = None  # List of points which lead to the goal - [(x1, y1), (x2, y2), ...]
        self.check_for_closer_apples = False

    def get_closest_apple(self):
        return min((self.heuristic_estimate_cost((self.player.x, self.player.y), (apple.x, apple.y)), apple) for apple in game.apples)[1]

    def next_safe_move(self):
        directions = [game.LEFT, game.RIGHT, game.UP, game.DOWN]
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        objects = []
        safe = True

        # Get objects surrounding the player
        for direction in directions:
            c = normalize_coordinate((self.player.x + offsets[direction][0], self.player.y + offsets[direction][1]))
            objects.append(game.board[c[0]][c[1]])

        # Check 2 steps ahead for another player's head
        c = normalize_coordinate((self.player.x + 2*offsets[self.player.direction][0], self.player.y + 2*offsets[self.player.direction][1]))
        obj = game.board[c[0]][c[1]]
        if isinstance(obj, game_objects.SnakePart) and obj is obj.player.parts[-1]:
            print "Snake head ahead!"
            safe = False

        # Keep going in the same direction if its safe. Otherwise find the first safe move
        if safe and (not objects[self.player.direction] or isinstance(objects[self.player.direction], game_objects.Apple)):
            return normalize_coordinate((self.player.x + offsets[self.player.direction][0], self.player.y + offsets[self.player.direction][1]))
        else:
            for i, obj in enumerate(objects):
                if i != self.player.direction and (not obj or isinstance(obj, game_objects.Apple)):
                    return normalize_coordinate((self.player.x + offsets[i][0], self.player.y + offsets[i][1]))
            print "No safe move!"
            return (self.player.x, self.player.y)

    def reassign_path(self):
        # Target the closest apple
        closest_apple = self.get_closest_apple()
        self.current_goal = (closest_apple.x, closest_apple.y)

        # Find a path to the target
        astar = AStar()
        path = astar.get_path((self.player.x, self.player.y), self.current_goal)
        if path:
            self.current_path = deque(path)
            self.current_path.popleft()  # Discard current position
        else:
            print "No path found, getting safe move"
            self.current_goal = self.next_safe_move()
            self.current_path = deque([self.current_goal])
            print self.current_path

    def next_move(self):
        if not self.current_path or not self.current_goal:
            self.reassign_path()

        # Target a new apple if the current one disappears, or if a closer one appears
        apple = game.board[self.current_goal[0]][self.current_goal[1]]
        if not apple or not isinstance(apple, game_objects.Apple):
            print "Apple disappeared"
            self.reassign_path()
        
        # If a closer apple appears, go for it
        if self.check_for_closer_apples:
            if apple is not self.get_closest_apple():
                print "Found closer apple"
                self.reassign_path()

        # If something is in our way, refresh path
        object_ahead = game.board[self.current_path[0][0]][self.current_path[0][1]]
        if object_ahead and not isinstance(object_ahead, game_objects.Apple):
            print "Something's in our way"
            self.reassign_path()

        # Get the next position
        next_pos = self.current_path.popleft()

        # Set player direction
        if next_pos[0] == self.player.x-1 or (self.player.x == 0 and next_pos[0] == game.BOARD_WIDTH-1):
            self.player.direction = game.LEFT
        elif next_pos[0] == self.player.x+1 or (self.player.x == game.BOARD_WIDTH-1 and next_pos[0] == 0):
            self.player.direction = game.RIGHT
        elif next_pos[1] == self.player.y-1 or (self.player.y == 0 and next_pos[1] == game.BOARD_HEIGHT-1):
            self.player.direction = game.UP
        elif next_pos[1] == self.player.y+1 or (self.player.y == game.BOARD_HEIGHT-1 and next_pos[1] == 0):
            self.player.direction = game.DOWN



