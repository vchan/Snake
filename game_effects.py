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

def clone_color(color):
    return pygame.Color(color.r, color.g, color.b, color.a)

def adjust_brightness(color, multiplier):
    rgb = [color.r, color.g, color.b]
    for i in range(len(rgb)):
        rgb[i] = int(rgb[i] * multiplier)
        if rgb[i] > 255:
            rgb[i] = 255
        if rgb[i] < 0:
            rgb[i] = 0
    return pygame.Color(rgb[0], rgb[1], rgb[2], color.a)

class Explosion(object):
    def __init__(self, x, y, color, max_speed=15, num_particles=20, particle_size=3, fade_speed=6, particle_type="circle"):
        self.particles = []  # Each particle holds [x, y, x_speed, y_speed]
        self.num_particles = num_particles        
        self.particle_size = particle_size
        self.particle_type = particle_type
        self.max_speed = max_speed
        self.x = x
        self.y = y
        self.color = clone_color(color)
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
        if self.color.a < self.fade_speed:
            game.effects.remove(self)
        else:
            self.color.a -= self.fade_speed

class ParticleTrail(object):
    def __init__(self, followed_object, color):
        self.followed_object = followed_object
        self.color = clone_color(color)
        self.trail_density = 1
        self.particles = []
        self.particle_radius = 2
        self.particle_speed = 2
        self.fade_speed = 10

    def draw(self):
        for particle in self.particles:
            draw_circle(game.screen, particle['color'], (particle['x'], particle['y']), self.particle_radius, 0)

    def update(self):
        for i in range(self.trail_density):
            self.particles.append({
                "x": self.followed_object.rect.centerx, 
                "y": self.followed_object.rect.centery, 
                "vx": random.uniform(-self.particle_speed, self.particle_speed), 
                "vy": random.uniform(-self.particle_speed, self.particle_speed), 
                "color": clone_color(self.color)
                })

        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            if particle['color'].a < self.fade_speed:
                self.particles.remove(particle)
            else:
                particle['color'].a -= self.fade_speed

# class FadingText(object):
#     def __init__(self, text, x, y, color):
#         self.text = text
#         self.x = x
#         self.y = y
#         self.color = clone_color(color)
#         self.font = pygame.font.SysFont("georgia", 15, bold=True)
#         self.fade_speed = 2

#     def draw(self):
#         text = self.font.render(self.text, 1, self.color)
#         # text.convert_alpha()
#         # text.set_alpha(50)
#         text_pos = text.get_rect(centerx = self.x, centery = self.y)
#         game.screen.blit(text, text_pos)

#     def update(self):
#         if self.color.a < self.fade_speed:
#             game.effects.remove(self)
#         else:
#             self.color.a -= self.fade_speed

# class Portal(object):
#     def __init__(self, x, y, color):
#         self.x = x
#         self.y = y
#         self.color = clone_color(color)
#         self.fade_speed = 10
#         self.fade_threshold = 40
#         self.ring_spacing = 30
#         self.ring_start_width = 10
#         self.rings = []
#         self.add_ring()        

#     def add_ring(self):
#         self.rings.append({'radius': self.ring_start_width, 'color': pygame.Color(self.color.r, self.color.g, self.color.b, 255)})

#     def draw(self):
#         for ring in self.rings:
#             draw_circle(game.screen, ring['color'], (self.x, self.y), ring['radius'], 1)

#     def update(self):
#         # Increase radius of all rings
#         for ring in self.rings:
#             ring['radius'] += 1

#         # Create new rings emerging from the center
#         if self.rings[-1]['radius'] > self.ring_spacing:
#             self.add_ring()

#         for ring in filter(lambda r: r['radius'] > self.fade_threshold, self.rings):
#             if ring['color'].a < self.fade_speed:
#                 self.rings.remove(ring)
#             else:
#                 ring['color'].a -= self.fade_speed


