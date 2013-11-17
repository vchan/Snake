import pygame
import game
import random

class Explosion(object):
    def __init__(self, x, y, color):
        self.particles = []
        self.num_particles = 30
        self.particle_radius = 3
        self.max_speed = 10
        self.x = x
        self.y = y
        self.color = color

        for i in range(self.num_particles):
            self.particles.append([float(self.x), float(self.y), random.uniform(-self.max_speed, self.max_speed), random.uniform(-self.max_speed, self.max_speed)])

    def draw(self):
        for p in self.particles:
            pygame.draw.circle(game.screen, self.color, (int(p[0]), int(p[1])), self.particle_radius)

    def update(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]

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
