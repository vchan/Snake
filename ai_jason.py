from collections import deque

import pygame
from pygame.locals import *

import game
import game_objects
from process import AIProcess

enable_visualization = False
wrap_coordinates = False
check_for_closer_apples = False

def normalize_coordinates(x, y):
    """Wraps coordinates if they are out of bounds"""
    if x < 0:
        x += game.BOARD_WIDTH
    if y < 0:
        y += game.BOARD_HEIGHT
    if x >= game.BOARD_WIDTH:
        x -= game.BOARD_WIDTH
    if y >= game.BOARD_HEIGHT:
        y -= game.BOARD_HEIGHT
    return (x, y)

def heuristic_cost_estimate(start, goal):
    """Calculates the Manhattan distance between two coordinates"""
    x_distance = abs(start[0]-goal[0])
    y_distance = abs(start[1]-goal[1])

    if wrap_coordinates:
        x_distance = min(x_distance, game.BOARD_WIDTH - x_distance)
        y_distance = min(y_distance, game.BOARD_HEIGHT - y_distance)

    return x_distance + y_distance

def extract_path(parent_nodes, current_node):
    """Helper for a_start_path(). Traces parent_nodes backwards, returning the path to the start node."""
    if current_node not in parent_nodes:
        return [current_node]
    else:
        return extract_path(parent_nodes, parent_nodes[current_node]) + [current_node]


class JasonAI(AIProcess):
    def __init__(self, *args, **kwargs):
        super(JasonAI, self).__init__(*args, **kwargs)
        self.current_goal = None  # Coordinates of where the snake is currently headed - (x, y)
        self.current_path = None  # List of points which lead to the goal - [(x1, y1), (x2, y2), ...]

    def a_star_path(self, goal):
        start = (self.player.x, self.player.y)

        """
        Uses the A* algorithm to find a path (list of (x,y) coordinates) from start to goal
        http://www.policyalmanac.org/games/aStarTutorial.htm

        """
        open_list = [start]
        closed_list = []
        parent_nodes = {}

        g_scores = {start: 0}
        h_scores = {start: heuristic_cost_estimate(start, goal)}
        f_scores = {start: g_scores[start] + h_scores[start]}
        
        while open_list:
            # Choose the lowest f score in the open list
            current = min((f_scores[node], node) for node in open_list)[1]
            if current == goal:
                path = extract_path(parent_nodes, current)
                # Draw the final path
                if enable_visualization:
                    for p in path:
                        pygame.draw.rect(game.screen, pygame.Color(255, 0, 0), pygame.Rect(p[0]*game.CELL_WIDTH, p[1]*game.CELL_HEIGHT, game.CELL_WIDTH, game.CELL_HEIGHT))
                    pygame.display.flip()
                return path

            open_list.remove(current)
            closed_list.append(current)

            # Draw the closed list
            if enable_visualization:
                pygame.draw.rect(game.screen, pygame.Color(0, 255, 0), pygame.Rect(current[0]*game.CELL_WIDTH, current[1]*game.CELL_HEIGHT, game.CELL_WIDTH, game.CELL_HEIGHT))

            # Get neighbors
            neighbors = []

            if wrap_coordinates:
                up = normalize_coordinates(current[0], current[1]-1)
                down = normalize_coordinates(current[0], current[1]+1)
                left = normalize_coordinates(current[0]-1, current[1])
                right = normalize_coordinates(current[0]+1, current[1])
            else:
                up = (current[0], current[1]-1)
                down = (current[0], current[1]+1)
                left = (current[0]-1, current[1])
                right = (current[0]+1, current[1])


            if (wrap_coordinates or (not wrap_coordinates and up[1] >= 0)) and \
                (self.board[up[0]][up[1]] == None or isinstance(self.board[up[0]][up[1]], game_objects.Apple)):
                neighbors.append(up)
            if (wrap_coordinates or (not wrap_coordinates and down[1] < game.BOARD_HEIGHT)) and \
                (self.board[down[0]][down[1]] == None or isinstance(self.board[down[0]][down[1]], game_objects.Apple)):
                neighbors.append(down)
            if (wrap_coordinates or (not wrap_coordinates and left[0] >= 0)) and \
                (self.board[left[0]][left[1]] == None or isinstance(self.board[left[0]][left[1]], game_objects.Apple)):
                neighbors.append(left)
            if (wrap_coordinates or (not wrap_coordinates and right[0] < game.BOARD_WIDTH)) and \
                (self.board[right[0]][right[1]] == None or isinstance(self.board[right[0]][right[1]], game_objects.Apple)):
                neighbors.append(right)

            # Calculate path scores
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue

                g = g_scores[current] + 1
                h = heuristic_cost_estimate(neighbor, goal)
                f = g + h

                if neighbor not in open_list or f < f_scores[neighbor]:
                    parent_nodes[neighbor] = current
                    g_scores[neighbor] = g
                    h_scores[neighbor] = h
                    f_scores[neighbor] = f
                    if neighbor not in open_list:
                        open_list.append(neighbor)
                        # Draw the open list
                        if enable_visualization:
                            pygame.draw.rect(game.screen, pygame.Color(0, 255, 255), pygame.Rect(neighbor[0]*game.CELL_WIDTH, neighbor[1]*game.CELL_HEIGHT, game.CELL_WIDTH, game.CELL_HEIGHT))

            if enable_visualization:
                pygame.display.flip()

        # Return false if no path was found
        return False

    def get_closest_apple(self):
        return min((heuristic_cost_estimate((self.player.x, self.player.y), (apple.x, apple.y)), apple) for apple in self.apples)[1]

    def next_safe_move(self):
        directions = [game.LEFT, game.RIGHT, game.UP, game.DOWN]
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        objects = []
        safe = True

        # Get objects surrounding the player
        for direction in directions:
            c = normalize_coordinates(self.player.x + offsets[direction][0], self.player.y + offsets[direction][1])
            objects.append(self.board[c[0]][c[1]])

        # Check 2 steps ahead for another player's head
        c = normalize_coordinates(self.player.x + 2*offsets[self.player.direction][0], self.player.y + 2*offsets[self.player.direction][1])
        obj = self.board[c[0]][c[1]]
        if isinstance(obj, game_objects.SnakePart) and obj is obj.player.parts[-1]:
            print "Snake head ahead!"
            safe = False

        # Keep going in the same direction if its safe. Otherwise find the first safe move
        if safe and (not objects[self.player.direction] or isinstance(objects[self.player.direction], game_objects.Apple)):
            return normalize_coordinates(self.player.x + offsets[self.player.direction][0], self.player.y + offsets[self.player.direction][1])
        else:
            for i, obj in enumerate(objects):
                if i != self.player.direction and (not obj or isinstance(obj, game_objects.Apple)):
                    return normalize_coordinates(self.player.x + offsets[i][0], self.player.y + offsets[i][1])
            print "No safe move!"
            return (self.player.x, self.player.y)

    def reassign_path(self):
        # Target the closest apple
        closest_apple = self.get_closest_apple()
        self.current_goal = (closest_apple.x, closest_apple.y)

        # Find a path to the target
        path = self.a_star_path(self.current_goal)
        if path:
            self.current_path = deque(path)
            self.current_path.popleft()  # Discard current position
        else:
            print "No path found, getting safe move"
            self.current_goal = self.next_safe_move()
            self.current_path = deque([self.current_goal])
            print self.current_path

    def execute(self):
        if not self.current_path or not self.current_goal:
            self.reassign_path()

        # Target a new apple if the current one disappears, or if a closer one appears
        apple = self.board[self.current_goal[0]][self.current_goal[1]]
        if not apple or not isinstance(apple, game_objects.Apple):
            print "Apple disappeared"
            self.reassign_path()
        
        # If a closer apple appears, go for it
        if check_for_closer_apples:
            if apple is not self.get_closest_apple():
                print "Found closer apple"
                self.reassign_path()

        # If something is in our way, refresh path
        object_ahead = self.board[self.current_path[0][0]][self.current_path[0][1]]
        if object_ahead and not isinstance(object_ahead, game_objects.Apple):
            print "Something's in our way"
            self.reassign_path()

        # Get the next position
        next_pos = self.current_path.popleft()

        print "current: ", (self.player.x, self.player.y), ", goal: ", self.current_goal, ", next: ", next_pos

        # Set player direction
        if next_pos[0] == self.player.x-1 or (self.player.x == 0 and next_pos[0] == game.BOARD_WIDTH-1):
            self.press_left()
        elif next_pos[0] == self.player.x+1 or (self.player.x == game.BOARD_WIDTH-1 and next_pos[0] == 0):
            self.press_right()
        elif next_pos[1] == self.player.y-1 or (self.player.y == 0 and next_pos[1] == game.BOARD_HEIGHT-1):
            self.press_up()
        elif next_pos[1] == self.player.y+1 or (self.player.y == game.BOARD_HEIGHT-1 and next_pos[1] == 0):
            self.press_down()


