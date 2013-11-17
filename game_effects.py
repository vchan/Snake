from collections import deque
import pygame
import game
import random

def draw_circle(screen, color, (center_x, center_y), radius, width):
    """Handles alpha transparency"""
    image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA, 32)
    pygame.draw.circle(image, color, (radius, radius), radius, width)
    screen.blit(image, (center_x-radius, center_y-radius))

def draw_rect(screen, color, rect, width=0):
    """Handles alpha transparency"""
    image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA, 32)
    pygame.draw.rect(image, color, pygame.Rect(0, 0, rect.width, rect.height), width)
    screen.blit(image, (rect.left, rect.top))

class Explosion(object):
    def __init__(self, x, y, color, num_particles=20, particle_size=3, fade_speed=4, particle_type="circle"):
        self.particles = []  # Each particle holds [x, y, x_speed, y_speed]
        self.num_particles = num_particles        
        self.particle_size = particle_size
        self.particle_type = particle_type
        self.max_speed = 10
        self.x = x
        self.y = y
        self.color = (color[0], color[1], color[2], 255)
        self.fade_speed = fade_speed

        for i in range(self.num_particles):
            self.particles.append([float(self.x), float(self.y), random.uniform(-self.max_speed, self.max_speed), random.uniform(-self.max_speed, self.max_speed)])

    def draw(self):
        for p in self.particles:
            if self.particle_type == "rect":
                draw_rect(game.screen, self.color, pygame.Rect(p[0], p[1], self.particle_size, self.particle_size))
            else:
                draw_circle(game.screen, self.color, (int(p[0]), int(p[1])), self.particle_size, 0)

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
    def __init__(self, followed_object, color):
        self.followed_object = followed_object
        self.particles = deque()
        self.num_particles = 20
        self.color = color
        self.radius = 2
        self.particle_speed = 1


    def draw(self):
        for particle in self.particles:
            draw_circle(game.screen, self.color, (particle[0], particle[1]), self.radius, 0)

    def update(self):
        self.particles.append([self.followed_object.rect.centerx, self.followed_object.rect.centery, random.uniform(-self.particle_speed, self.particle_speed), random.uniform(-self.particle_speed, self.particle_speed)])
        if len(self.particles) > self.num_particles:
            self.particles.popleft()

        for particle in self.particles:
            particle[0] += particle[2]
            particle[1] += particle[3]

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


