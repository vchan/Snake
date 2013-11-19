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

        game.board[x][y] = self

    def draw(self):
        pygame.draw.rect(game.screen, self.color, self.rect)

    def update(self):
        raise NotImplementedError('Not implemented')

    def destroy(self):
        game.board[self.x][self.y] = None

class SnakePart(GameObject):
    def __init__(self, player, x, y, color):
        super(SnakePart, self).__init__(x, y, color)
        self.player = player

    def become_missile(self, x, y, direction):
        self.destroy()
        if direction == game.LEFT:
            x -= 1
        elif direction == game.RIGHT:
            x += 1
        elif direction == game.UP:
            y -= 1
        elif direction == game.DOWN:
            y += 1

        # Check if SnakePart is out of bounds
        if x < 0:
            x = game.BOARD_WIDTH-1
        if x >= game.BOARD_WIDTH:
            x = 0
        if y < 0:
            y = game.BOARD_HEIGHT-1
        if y >= game.BOARD_HEIGHT:
            y = 0
        return Missile(self.player, x, y, direction, self.color)

class Missile(GameObject):
    def __init__(self, player, x, y, direction, color):
        super(Missile, self).__init__(x, y, game_effects.adjust_brightness(color, 0.5))
        self.player = player
        self.direction = direction
        self.particle_trail = game_effects.ParticleTrail(self, self.color)
        game.effects.append(self.particle_trail)

    def update(self):
        _x, _y = self.x, self.y

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

        # Update game board
        if (self.x, self.y) != (_x, _y):
            if game.board[_x][_y] == self:
                game.board[_x][_y] = None
            try:
                game.board[self.x][self.y] = self
            except game.CollisionError, ce:
                if isinstance(ce.collidee, Missile):
                    ce.collidee.destroy_missile()
                elif isinstance(ce.collidee, Wall):
                    ce.collidee.destroy()
                    game.effects.append(game_effects.Explosion(ce.collidee.rect.centerx, ce.collidee.rect.centery, ce.collidee.color, max_speed=6, num_particles=5, particle_size=5, fade_speed=12))
                elif isinstance(ce.collidee, SnakePart):
                    player = ce.collidee.player
                    if (player.x, player.y) == (ce.collidee.x, ce.collidee.y):
                        player.kill(self)
                elif isinstance(ce.collidee, Apple):
                    return
                self.destroy_missile()

    def destroy_missile(self):
        self.destroy()
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

    def destroy(self):
        super(Wall, self).destroy()
        game.walls.remove(self)

class IndestructableWall(GameObject):
    def __init__(self, x, y):
        super(IndestructableWall, self).__init__(x, y, pygame.Color(99, 39, 20))

    def destroy(self):
        pass

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

        # Update game board
        try:
            head = SnakePart(self, self.x, self.y, self.color)
            self.parts.append(head)
        except game.CollisionError, ce:
            if isinstance(ce.collidee, Apple):
                game.apples.remove(ce.collidee)
                ce.collidee.destroy()
                game.add_apple()
                self.grow = True
                head = SnakePart(self, self.x, self.y, self.color)
                self.parts.append(head)
                game.log_screen.add("%s grew to %s blocks." % (self.name, len(self.parts)))
            else:
                self.kill(ce.collidee)
                if isinstance(ce.collidee, Missile):
                    ce.collidee.destroy_missile()

        # Pop the tail
        if self.grow:
            self.grow = False
        else:
            end = self.parts.popleft()
            end.destroy()

        # Reset any locks
        self._lock_set_direction = False

    def kill(self, collided_object=None):
        self.is_dead = True
        for part in self.parts:
            part.destroy()

        # Show explosion
        game.effects.append(game_effects.Explosion(self.parts[-1].rect.left, self.parts[-1].rect.top, self.color, max_speed=22, num_particles=20, particle_size=5, fade_speed=6))

        # Log it!
        log_text = self.name + " died!"
        if isinstance(collided_object, Wall):
            log_text = self.name + " ran into a wall."
        elif isinstance(collided_object, (SnakePart, Missile)):
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
            try:
                missile = part.become_missile(self.x, self.y, self.direction)  # Move missile to the head
                game.missiles.append(missile)
                game.log_screen.add('%s fired a missile!' % self.name)
            except game.CollisionError, ce:
                if isinstance(ce.collidee, Missile):
                    # Could not create missile because a missile is already there
                    # Reattach part
                    self.parts.appendleft(part)

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
