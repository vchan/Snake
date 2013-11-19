from collections import deque
import pygame
import game
import game_effects

class GameObject(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = game.CELL_WIDTH
        self.height = game.CELL_HEIGHT
        self.rect = pygame.Rect(x*self.width, y*self.height, self.width, self.height)
        self.color = color

    def draw(self):
        pygame.draw.rect(game.screen, self.color, self.rect)

    def update(self):
        raise NotImplemented('Not implemented')

    def collides_with(self, collidable):
        """Returns the object it collides with, otherwise false."""
        if isinstance(collidable, list):
            index = self.rect.collidelist([c.rect for c in collidable])
            return False if index == -1 else collidable[index]
        else:
            return self.rect.colliderect(collidable.rect)

class SnakePart(GameObject):
    def __init__(self, player, x, y, color):
        super(SnakePart, self).__init__(x, y, color)
        self.player = player

    def become_missile(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = game_effects.adjust_brightness(self.color, 0.5)
        self.particle_trail = game_effects.ParticleTrail(self, self.color)
        game.effects.append(self.particle_trail)

    def update(self):
        if self.direction == game.LEFT:
            self.x -= 1
        elif self.direction == game.RIGHT:
            self.x += 1
        elif self.direction == game.UP:
            self.y -= 1
        elif self.direction == game.DOWN:
            self.y += 1

        # Check if SnakePart is out of bounds
        if self.x < 0:
            self.x = game.BOARD_WIDTH-1
        if self.x >= game.BOARD_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = game.BOARD_HEIGHT-1
        if self.y >= game.BOARD_HEIGHT:
            self.y = 0

        # Keep rect object up to date
        self.rect = pygame.Rect(self.x*self.width, self.y*self.height, self.width, self.height)

        # Check if missle collided with anything
        collidable = self.collides_with(game.get_collidables(self))
        if collidable:
            if isinstance(collidable, Wall):
                game.walls.remove(collidable)
                game.effects.append(game_effects.Explosion(collidable.rect.centerx, collidable.rect.centery, collidable.color, max_speed=6, num_particles=5, particle_size=5, fade_speed=12))
            if self in game.missiles:
                self.destroy_missile()
            if collidable in game.missiles:
                collidable.destroy_missile()

    def destroy_missile(self):
        game.missiles.remove(self)
        game.effects.remove(self.particle_trail)
        game.effects.append(game_effects.Explosion(self.rect.centerx, self.rect.centery, self.color, max_speed=15, num_particles=5, particle_size=4, fade_speed=10))

class Apple(GameObject):
    def __init__(self, x, y):
        super(Apple, self).__init__(x, y, pygame.Color(255, 0, 0))
        self.color_change = 4

    def update(self):
        self.color.g += self.color_change
        if self.color.g > 200 or self.color.g == 0:
            self.color_change *= -1
        
    def draw(self):
        radius = int(self.rect.width/2*1.414)  # Expand the diameter to the length of the diagonal
        pygame.draw.circle(game.screen, self.color, self.rect.center, radius)

class Wall(GameObject):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y, pygame.Color(139, 69, 0))

class IndestructableWall(GameObject):
    def __init__(self, x, y):
        super(IndestructableWall, self).__init__(x, y, pygame.Color(99, 39, 20))

class Player(object):
    def __init__(self, name, x, y, direction, color):
        self.name = name
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
        self.parts = deque()
        self.parts.append(SnakePart(self, self.x, self.y, color))
        self.grow = False
        self.is_dead = False
        self.frames_until_update_position = 3
        self.frame_count = 1

    def update(self):
        if self.frame_count < self.frames_until_update_position:
            self.frame_count += 1
        else:
            self.update_position()
            self.frame_count = 1

    def update_position(self):
        if self.direction == game.LEFT:
            self.x -= 1
        elif self.direction == game.RIGHT:
            self.x += 1
        elif self.direction == game.UP:
            self.y -= 1
        elif self.direction == game.DOWN:
            self.y += 1

        # Check if player is out of bounds
        if self.x < 0:
            self.x = game.BOARD_WIDTH-1
        if self.x >= game.BOARD_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = game.BOARD_HEIGHT-1
        if self.y >= game.BOARD_HEIGHT:
            self.y = 0

        # Check if player collided with something
        head = SnakePart(self, self.x, self.y, self.color)
        collided_object = head.collides_with(game.get_collidables())

        if collided_object:
            if collided_object in game.missiles:
                collided_object.destroy_missile()
            self.kill(collided_object)

        # Append new head after collision checks
        self.parts.append(head)

        # Check if player ate an apple
        for apple in game.apples:
            if apple.collides_with(head):
                game.apples.remove(apple)
                game.add_apple()
                self.grow = True
                # game.effects.append(game_effects.FadingText(str(len(self.parts)), head.rect.centerx, head.rect.centery, pygame.Color(255, 0, 0)))
                game.log_screen.add("%s grew to %s blocks." % (self.name, len(self.parts)))

        # Pop the tail
        if self.grow:
            self.grow = False
        else:
            self.parts.popleft()

        # Reset any locks
        self._lock_set_direction = False

    def kill(self, collided_object=None):
        self.is_dead = True

        # Show explosion
        game.effects.append(game_effects.Explosion(self.parts[-1].rect.left, self.parts[-1].rect.top, self.color, max_speed=22, num_particles=20, particle_size=5, fade_speed=6))

        # Log it!
        log_text = self.name + " died!"
        if isinstance(collided_object, Wall):
            log_text = self.name + " ran into a wall."
        elif isinstance(collided_object, SnakePart):
            if collided_object.player is self:
                log_text = self.name + " killed themselves."
            else:
                log_text = self.name + " got killed by " + collided_object.player.name + "!"
        game.log_screen.add(log_text)

    def draw(self):
        for part in self.parts:
            part.draw()

    def fire(self):
        """ Fires a snakepart """
        if len(self.parts) > 1:
            part = self.parts.popleft()  # Remove from the tail
            part.become_missile(self.x, self.y, self.direction)  # Move missile to the head
            part.update()  # Move missile in front of the head
            game.missiles.append(part)

    def set_direction(self, direction):
        if self.is_dead or self._lock_set_direction:
            return

        if direction == self.direction:
            self.fire()
        elif (direction == game.LEFT and self.direction != game.RIGHT) or \
            (direction == game.RIGHT and self.direction != game.LEFT) or \
            (direction == game.UP and self.direction != game.DOWN) or \
            (direction == game.DOWN and self.direction != game.UP):
            self.direction = direction
            self._lock_set_direction = True

class LogScreen(object):
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("verdana", 12)
        self.log = deque()
        self.log_size = 5

    def draw(self):
        for i, text in enumerate(self.log):
            text = self.font.render(text, 1, (255, 255, 255))
            textpos = text.get_rect(top = 30 + i*20, right = game.WINDOW_WIDTH-30)
            game.screen.blit(text, textpos)

    def add(self, text):
        self.log.append(text)
        if len(self.log) > self.log_size:
            self.log.popleft()
