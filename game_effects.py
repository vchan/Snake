import pygame
import game
import random

def draw_circle(screen, color, (center_x, center_y), radius):
    """Handles alpha transparency"""
    image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA, 32)
    pygame.draw.circle(image, color, (radius, radius), radius)
    screen.blit(image, (center_x-radius, center_y-radius))

class Explosion(object):
    def __init__(self, x, y, color):
        self.particles = []  # Each particle holds [x, y, x_speed, y_speed]
        self.num_particles = 20
        self.particle_radius = 3
        self.max_speed = 10
        self.x = x
        self.y = y
        self.color = (color[0], color[1], color[2], 255)
        self.fade_speed = 4

        for i in range(self.num_particles):
            self.particles.append([float(self.x), float(self.y), random.uniform(-self.max_speed, self.max_speed), random.uniform(-self.max_speed, self.max_speed)])

    def draw(self):
        for p in self.particles:
            draw_circle(game.screen, self.color, (int(p[0]), int(p[1])), self.particle_radius)

    def update(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]

        # Decrease alpha of particle
        color = list(self.color)
        color[3] -= self.fade_speed
        self.color = tuple(color)

        if color[3] < 0:
            game.effects.remove(self)

class Portal(object):
    def __init__(self):
        self.radiuses = [1]
        self.x = 200
        self.y = 200
        self.color = pygame.Color(255, 0, 0, 10)

    def draw(self):
        for radius in self.radiuses:
            pygame.draw.circle(game.screen, pygame.Color(255, 128, 0, 255), (self.x, self.y), radius, 1)

    def update(self):
        for i in range(len(self.radiuses)):
            self.radiuses[i] += 1

        if self.radiuses[-1] > 20:
            self.radiuses.append(1)

        if self.radiuses[0] > 100:
            self.radiuses.pop(0)
