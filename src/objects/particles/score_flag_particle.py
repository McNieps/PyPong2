import pygame
import random

from src.objects.particles.particle import Particle


class ScoreFlagParticle(Particle):
    def __init__(self, flag_rect):
        speed = pygame.math.Vector2(0, 200)
        speed.rotate_ip(random.randint(-15, 15))
        size = random.randint(3, 8)
        lifetime = size*0.25

        position = (random.randint(flag_rect.left, flag_rect.right),
                    random.randint(flag_rect.bottom-5, flag_rect.bottom))

        friction = random.randint(50, 150)/1000

        super().__init__(position, speed, size, friction, lifetime)

    @classmethod
    def spawn_bunch(cls, flag_rect, quantity):
        for i in range(quantity):
            ScoreFlagParticle(flag_rect)

    def draw(self, surface):
        size = int(self.base_size*((self.current_ratio-1)*-1))
        if size < 1:
            size = 1
        self.friction = size/1000

        ellipse_rect = pygame.Rect(0, 0, size, size)
        ellipse_rect.center = self.x, self.y
        pygame.draw.ellipse(surface, (255, 255, 255), ellipse_rect)

    def update_pos(self, delta):
        self.vy += 75*delta
        self.vx = self.vx * self.friction ** delta
        self.vy = self.vy * self.friction ** delta

        self.x += self.vx * delta
        self.y += self.vy * delta
