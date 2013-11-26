from collections import deque
from heapq import heappush, heappop
from operator import itemgetter

import pygame
from pygame.locals import *

import game
import game_objects

class AStar(object):
    def __init__(self):
        self.closed_set = set()
        self.open_set = set()  # We use set for fast membership tests
        self.open_heap = []  # We use heap for fast min checks
        self.nodes = {}

        self.enable_path_visualization = False
        self.wrap_coordinates = False
        self.retarget_alternate_goals = False

    def is_neighbor(self, node):
        raise Exception("Not implemented")

    def is_alternate_goal(self, node):
        raise Exception("Not implemented")

    def wrap_node(self, node):
        raise Exception("Not implemented")

    def draw_node(self, node, color):
        raise Exception("Not implemented")

    def movement_cost(self, node1, node2):
        raise Exception("Not implemented")

    def heuristic_estimate_cost(self, start, goal):
        raise Exception("Not implemented")

    def _retrace_path(self, node):
        if self.nodes[node]['parent'] is None:
            return [node]
        else:
            return self._retrace_path(self.nodes[node]['parent']) + [node]

    def retrace_path(self, node):
        path = self._retrace_path(node)
        if self.enable_path_visualization:
            for p in path:
                self.draw_node(p, pygame.Color("red"))
        return path

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

    def clear_data(self):
        self.open_set = set()
        self.open_heap = []
        self.closed_set = set()
        self.nodes = {}

    def get_path(self, start, goal):
        self.clear_data()

        # Add start node to the open set
        h = self.heuristic_estimate_cost(start, goal)
        self.nodes[start] = {'g': 0, 'h': h, 'f': h, 'parent': None}
        self.open_set_add(start)        
 
        while self.open_set:
            # Choose lowest f-score in the open list. Use h-score as a tie-breaker
            current = self.open_set_pop_lowest_f_score()
            self.closed_set.add(current)
            if current == goal:
                return self.retrace_path(current)

            # Draw the closed set
            if self.enable_path_visualization:
                self.draw_node(current, pygame.Color("green"))

            # Get neighbors
            neighbors = []
            direction_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, right, up, down
            for ox, oy in direction_offsets:
                neighbor = (current[0]+ox, current[1]+oy) 
                if self.wrap_coordinates:
                    neighbor = self.wrap_node(neighbor)
                if self.is_neighbor(neighbor):
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
                    if self.enable_path_visualization:
                        self.draw_node(neighbor, pygame.Color("cyan"))
                # If we find a different goal we like, return the path to it.
                if self.retarget_alternate_goals and neighbor != goal and self.is_alternate_goal(neighbor):
                    return self.retrace_path(neighbor)

        # If no path was found
        return False

class JasonAI(AStar):
    MAX_SAFETY_SCORE = 100

    def __init__(self, player, *args, **kwargs):
        super(JasonAI, self).__init__()
        self.player = player
        self.player.onkill = self.onkill
        # self.last_known_position = None

        self.enable_path_visualization = False
        self.enable_line_of_fire_visualization = False
        self.enable_safety_score_visualization = False
        self.wrap_coordinates = True
        self.retarget_alternate_goals = True
        self.check_for_closer_apples = True
        
        self.destination = None
        self.path = None

        self.survival_cycles = 0

    def is_neighbor(self, node):
        node_behind_player = self.node_at_direction(self.get_opposite_direction(self.player.direction))
        return not self.is_out_of_bounds(node) and self.is_traversable(node) and node != node_behind_player

    def is_alternate_goal(self, node):
        if self.is_apple(node):
            # print "Found a different apple!"
            return True
        else:
            return False

    def wrap_node(self, node):
        x, y = node
        if x < 0:
            x += game.BOARD_WIDTH
        if y < 0:
            y += game.BOARD_HEIGHT
        if x >= game.BOARD_WIDTH:
            x -= game.BOARD_WIDTH
        if y >= game.BOARD_HEIGHT:
            y -= game.BOARD_HEIGHT
        return (x, y)

    def draw_node(self, node, color):
        pygame.draw.rect(game.screen, color, pygame.Rect(node[0]*game.CELL_WIDTH, node[1]*game.CELL_HEIGHT, game.CELL_WIDTH, game.CELL_HEIGHT))

    def movement_cost(self, node1, node2):
        return 1

    def heuristic_estimate_cost(self, start, goal):
        x_distance = abs(start[0]-goal[0])
        y_distance = abs(start[1]-goal[1])
        if self.wrap_coordinates:
            x_distance = min(x_distance, game.BOARD_WIDTH - x_distance)
            y_distance = min(y_distance, game.BOARD_HEIGHT - y_distance)
        return (x_distance + y_distance)

    def is_out_of_bounds(self, node):
        return not (0 <= node[0] < game.BOARD_WIDTH and 0 <= node[1] < game.BOARD_HEIGHT)

    def is_traversable(self, node):
        return self.get_board_object(node) is None or self.is_apple(node)

    def is_apple(self, node):
        return isinstance(self.get_board_object(node), game_objects.Apple)

    def is_snake_head(self, node):
        obj = self.get_board_object(node)
        return isinstance(obj, game_objects.SnakePart) and (obj.x, obj.y) == (obj.player.x, obj.player.y)

    def is_missile(self, node):
        return isinstance(self.get_board_object(node), game_objects.Missile)

    def is_wall(self, node):
        return isinstance(self.get_board_object(node), game_objects.Wall)

    def get_closest_apple(self):
        apple = min((self.heuristic_estimate_cost((self.player.x, self.player.y), (apple.x, apple.y)), apple) for apple in game.apples)[1]
        return (apple.x, apple.y)

    def get_board_object(self, node):
        return game.board[node[0]][node[1]]

    def translate_direction(self, facing_direction, going_direction):
        left = {game.LEFT: game.DOWN, game.RIGHT: game.UP, game.UP: game.LEFT, game.DOWN: game.RIGHT}

        if going_direction == game.LEFT:
            return left[facing_direction]
        if going_direction == game.RIGHT:
            return self.get_opposite_direction(left[facing_direction])
        if going_direction == game.UP:
            return facing_direction
        if going_direction == game.DOWN:
            return self.get_opposite_direction(facing_direction)
        
    def get_opposite_direction(self, direction):
        opposites = [game.RIGHT, game.LEFT, game.DOWN, game.UP]
        return opposites[direction]

    def node_at_direction(self, direction, start_node=None, steps=1):
        """Gets the node to the left / right / up / down from the player or given start node."""
        start_node = start_node or (self.player.x, self.player.y)
        offsets = {game.LEFT: (-1, 0), game.RIGHT: (1, 0), game.UP: (0, -1), game.DOWN: (0, 1)}
        ox, oy = offsets[direction]
        return self.wrap_node((start_node[0] + ox*steps, start_node[1] + oy*steps))

    # def node_at_offset(self, offset, start_node=None):
    #     """
    #     Takes the player's current position and applies the given (x, y) offset. Handles wrapping.
    #     Uses start_node instead of the player's position if specified.

    #     """
    #     x, y = start_node or (self.player.x, self.player.y)
    #     ox, oy = offset
    #     return self.wrap_node((x+ox, y+oy))

    def direction_to_node(self, node):
        """Given a node adjacent to player, tells you which direction you must go to get to it."""
        x, y = node
        if x == self.player.x-1 or (self.player.x == 0 and x == game.BOARD_WIDTH-1):
            return game.LEFT
        elif x == self.player.x+1 or (self.player.x == game.BOARD_WIDTH-1 and x == 0):
            return game.RIGHT
        elif y == self.player.y-1 or (self.player.y == 0 and y == game.BOARD_HEIGHT-1):
            return game.UP
        elif y == self.player.y+1 or (self.player.y == game.BOARD_HEIGHT-1 and y == 0):
            return game.DOWN
        else:
            print "Player:", (self.player.x, self.player.y), " node:", node
            raise Exception("Node not next to player")

    def get_safety_score(self, direction_to_check):
        """
        Returns the score of the best outcome available by moving in the given direction.
        The worst outcome is if by moving in this direction, we are certain to give another player a point.

        """
        directions = [game.LEFT, game.RIGHT, game.UP, game.DOWN]
        if self.player.get_length() > 1:
            directions.remove(self.get_opposite_direction(direction_to_check))  # Don't check behind us if we're > 1 block long
        node_to_check = self.node_at_direction(direction_to_check)

        # Draw current node
        if self.enable_safety_score_visualization:
            self.draw_node(node_to_check, pygame.Color("cyan"))

        # If node is not traversable (Certain death)
        if not self.is_traversable(node_to_check):
            obj = self.get_board_object(node_to_check)
            # Run into another player - this ranks higher than certain missile death because there's a chance the player could be gone by the next turn.
            if isinstance(obj, game_objects.SnakePart) and obj.player is not self.player:
                return 10
            # Run into a wall or yourself - we prefer this over running into another player, since no one gets a kill point.
            else:
                return 30

        # Look ahead in each direction
        look_ahead = 5
        for direction in directions:
            nodes_in_range = [self.node_at_direction(direction, start_node=node_to_check, steps=i) for i in range(1, look_ahead+1)]

            # Draw the nodes being checked
            if self.enable_safety_score_visualization:
                for node in nodes_in_range:
                    self.draw_node(node, pygame.Color("cyan"))

            # Missile in range (Certain death). Look-ahead 1-3, you die next turn. Look-ahead 4, you die at beginning of 2nd turn.
            for i, node in enumerate(nodes_in_range[:4]):
                if self.is_missile(node) and self.get_board_object(node).direction == self.get_opposite_direction(direction):
                    return 0 + i

            # Player in range (Certain death if opponent doesnt turn away). If neither player turns away, you die next turn.
            if self.is_snake_head(nodes_in_range[0]) and self.get_board_object(nodes_in_range[0]).player is not self.player:
                return 20

            # Player in missile range (Certain death if opponent shoots).
            for i, node in enumerate(nodes_in_range[1:5]):
                if self.is_snake_head(node):
                    player = self.get_board_object(node).player
                    if player.get_length() > 1:
                        if player.direction == self.get_opposite_direction(direction): # If opponent is turned towards us
                            return 40 + i
                        else: # Opponent can still kill us next turn, even if it's turned away from us
                            return 50 + i

        return JasonAI.MAX_SAFETY_SCORE

    def next_safe_move(self):
        safety_scores = {direction: self.get_safety_score(direction) for direction in range(4) if direction != self.get_opposite_direction(self.player.direction)}
        safest_direction, safest_score = max(safety_scores.iteritems(), key=itemgetter(1))
        node_ahead = self.node_at_direction(self.player.direction)

        # If we're forced to choose a suboptimal path, shoot a missile.
        if safest_score < JasonAI.MAX_SAFETY_SCORE:
            print "(P", self.player.player_number , ") Safest path not available. Scores:", safety_scores

        # If there are no safe moves
        if not safest_score:
            print "NO MORE SAFE MOVES! Scores:", safety_scores
            return node_ahead

        # Keep going if it's safe
        if safety_scores[self.player.direction] == safest_score:
            return node_ahead

        # Otherwise change directions
        return self.node_at_direction(safest_direction)

    def prepare_closest_apple_path(self):
        self.destination = self.get_closest_apple()
        path = self.get_path((self.player.x, self.player.y), self.destination)
        if path:
            self.path = deque(path)
            self.path.popleft()  # Discard current position
        else:
            raise Exception("No path to closest apple")

    def prepare_path(self):
        if self.survival_cycles > 0:
            self.path = deque([self.next_safe_move()])
            self.survival_cycles -= 1
            return

        # If a path exists, see if there's a better one
        if self.path:
            
            # # Check if the next node in our path is reachable
            # try:
            #     next_direction = self.direction_to_node(self.path[0])
            # except Exception:
            #     print "Path broke. Reassigning a new path..."
            #     self.path = None
            # else:

            # Check if our apple is still there
            if not self.is_apple(self.destination):
                # print "Apple no longer available"
                self.path = None
            # Check if a closer apple appeared
            elif self.check_for_closer_apples and self.destination != self.get_closest_apple():
                # print "Found closer apple"
                self.path = None

        # Create path to the closest apple
        if not self.path:
            try:
                self.prepare_closest_apple_path()
            except Exception:
                self.survival_cycles = 5
                print "No path to closest apple. Surviving 10 cycles"

        # Check if the first node in the path is safe
        if self.path:
            next_direction = self.direction_to_node(self.path[0])
            next_safety_score = self.get_safety_score(next_direction)
            if next_safety_score < JasonAI.MAX_SAFETY_SCORE:
                # print "Danger! Safety score: ", next_safety_score
                self.survival_cycles = 1

        # If no good path is found, try to survive
        if self.survival_cycles > 0:
            self.prepare_path()
            return

    def get_line_of_fire(self):
        """Returns the coordinates of the first object in the line of fire, as well as our distance to it"""
        iterations = game.BOARD_WIDTH if self.player.direction in (game.LEFT, game.RIGHT) else game.BOARD_HEIGHT

        for distance in range(1, iterations):
            node = self.node_at_direction(self.player.direction, steps=distance)
            if self.enable_line_of_fire_visualization:
                self.draw_node(node, pygame.Color("orange"))
            if not self.is_traversable(node):
                return (node, distance)

        # Nothing in the line of fire
        return (False, False)

    def shoot_missile(self):
        # Always keep a length of 2
        if self.player.get_length() <= 2:
            return False

        # Shoot opponents within 6 nodes from us
        start_nodes = [(self.player.x, self.player.y)]

        # Include the left and right lanes if we've got extra ammo
        if self.player.get_length() > 5:
            start_nodes.append(self.node_at_direction(self.translate_direction(self.player.direction, game.LEFT)))
            start_nodes.append(self.node_at_direction(self.translate_direction(self.player.direction, game.RIGHT)))

        # Look for players!
        look_ahead = 6
        for start_node in start_nodes:
            for step in range(1, look_ahead+1):
                node = self.node_at_direction(self.translate_direction(self.player.direction, game.UP), start_node=start_node, steps=step)
                
                # If we see a player, take the shot.
                if self.is_snake_head(node):
                    return True

                # Draw our line of fire
                if self.enable_line_of_fire_visualization:
                    self.draw_node(node, pygame.Color("orange"))

        # See if any opponents are coming towards us
        if self.player.get_length() > 5:
            node, distance = self.get_line_of_fire()
            if not node:
                return False
            if self.is_snake_head(node):
                player = self.get_board_object(node).player
                # Shoot if they're facing us
                if player.direction == self.get_opposite_direction(self.player.direction):
                    return True
                # Shoot if they're 1 block long
                elif player.get_length() == 1 and player.direction == self.player.direction:
                    return True
                # Shoot regardless if we've got extra ammo
                elif self.player.get_length() > 10:
                    return True

        # Shoot walls if we have the ammo
        if self.is_wall(node) and self.player.get_length() > 15:
            return True


    def onkill(self, collidee):
        self.path = None

        print "(P", self.player.player_number, ") ",

        if isinstance(collidee, game_objects.Wall):
            print "Death by wall"
        elif isinstance(collidee, game_objects.SnakePart):
            if collidee.player is self.player:
                print "Death by self-collision"
            else:
                print "Death by player-collision: ", collidee.player.name, ". Delaying 10 seconds..."
                # pygame.time.wait(1000*10)
        elif isinstance(collidee, game_objects.Missile):
            if collidee.player is self.player:
                print "Death by self-missile"
            else:
                print "Death by player-missile: ", collidee.player.name, ". Delaying 10 seconds..."
                # pygame.time.wait(1000*10)

    def press_key(self, direction):
        pygame.event.post(pygame.event.Event(KEYDOWN, {'key': game.player_controls[self.player.player_number][direction]}))

    def execute(self):
        # # Skip if player has not yet moved
        # if self.last_known_position == (self.player.x, self.player.y):
        #     return
        # else:
        #     self.last_known_position = (self.player.x, self.player.y)

        # Reset our path if it's broken
        if self.path:
            try:
                self.direction_to_node(self.path[0])
            except Exception:
                print "Path broke. Reassigning a new path..."
                self.path = None

        # Decide whether to shoot a missile
        if self.shoot_missile():
            self.press_key(self.player.direction)

        # Get the next move
        self.prepare_path()
        next_direction = self.direction_to_node(self.path.popleft())
        if next_direction != self.player.direction:
            self.press_key(next_direction)

        # Display any visualizations
        if any((self.enable_path_visualization, self.enable_safety_score_visualization, self.enable_line_of_fire_visualization)):
            pygame.display.flip()
            






