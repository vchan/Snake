import pygame
import game
import random

def draw_circle(screen, color, (center_x, center_y), radius, width):
    """Handles alpha transparency"""
    image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA, 32)
    pygame.draw.circle(image, color, (radius, radius), radius, width)
    screen.blit(image, (center_x-radius, center_y-radius))

class Explosion(object):
    def __init__(self, x, y, color, num_particles=20, particle_radius=3, fade_speed=4):
        self.particles = []  # Each particle holds [x, y, x_speed, y_speed]
        self.num_particles = num_particles        
        self.particle_radius = particle_radius
        self.max_speed = 10
        self.x = x
        self.y = y
        self.color = (color[0], color[1], color[2], 255)
        self.fade_speed = fade_speed

        for i in range(self.num_particles):
            self.particles.append([float(self.x), float(self.y), random.uniform(-self.max_speed, self.max_speed), random.uniform(-self.max_speed, self.max_speed)])

    def draw(self):
        for p in self.particles:
            draw_circle(game.screen, self.color, (int(p[0]), int(p[1])), self.particle_radius, 0)

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

class ParticleTrail(object):
    def __init__(self, object_followed):
        self.object_followed = object_followed
        self.particles = []
        self.color = (255, 0, 0, 255)

    def draw(self):
        for particle in self.particles:
            draw_circle(game.screen, self.color, (partice[0], particle[1]), radius, 1)

    def update(self):
        self.particles.append([self.object_followed.x, self.object_followed.y])

class Portal(object):
    def __init__(self):
        self.x = 200
        self.y = 200
        self.color = (255, 0, 0, 255)
        self.fade_speed = 2
        self.circles = [[1, self.color]]
        self.spacing = 10

    def draw(self):
        for radius, color in self.circles:
            draw_circle(game.screen, color, (self.x, self.y), radius, 1)

    def update(self):
        # Increase radius of all circles
        for circle in self.circles:
            circle[0] += 1

        # Create new circles emerging from the center
        if self.circles[-1][0] > self.spacing:
            self.circles.append([1, self.color])

        # Start fading the bigger circles
        for circle in filter(lambda c: c[0] > 0, self.circles):
            color = list(circle[1])
            color[3] -= self.fade_speed
            if color[3] < 0:
                self.circles.remove(circle)
            else:
                circle[1] = tuple(color)


