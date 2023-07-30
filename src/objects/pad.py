import pygame

from src.objects.particles.pad_slam_dust import PadSlamDust
from src.objects.effects.screen_shake import ScreenShake
from src.engine.sound.synth import Synth


class Pad:
    PADS_BINDINGS = [{"UP": pygame.K_z,
                      "DOWN": pygame.K_s},
                     {"UP": pygame.K_KP_8,
                      "DOWN": pygame.K_KP_2}]

    PADS = []
    PARTICLE_THRESHOLD_SPEED = 50

    def __init__(self, side, linked_arena):
        self.side = side  # 0 if left, 1 if right
        self.bindings = self.PADS_BINDINGS[side]
        self.linked_arena = linked_arena

        # Movements and arena collision
        self.x = 15 + 369 * side
        self.y = 150
        self.vy = 0
        self.base_accel = 2000
        self.friction = 0.01
        self.bounce = 0.8

        # Shape
        self.height = 40
        self.width = 5
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.update_rect()

        # Meta
        self.PADS.append(self)

        # Animation
        self.x_animation = False
        self.x_offset = 0
        self.x_speed = 0
        self.x_spring = -100
        self.x_damping = 40

    @classmethod
    def handle_inputs(cls, delta):
        key_pressed = pygame.key.get_pressed()
        for pad in cls.PADS:
            if key_pressed[pad.bindings["UP"]]:
                pad.move(-1, delta)
            if key_pressed[pad.bindings["DOWN"]]:
                pad.move(1, delta)

    def move(self, direction, delta):
        self.vy += direction * self.base_accel * delta

    def update_pos(self, delta):
        self.vy *= self.friction ** delta
        self.y += self.vy * delta

    def update_rect(self):
        self.rect.width = self.width
        self.rect.height = self.height
        self.rect.center = self.x, self.y

    def update_animation(self, delta):
        if self.x_animation:
            force = self.x_spring * self.x_offset - self.x_speed * self.x_damping
            self.x_speed += force * delta
            self.x_offset += self.x_speed * delta

            if abs(self.x_offset) < 0.2 and abs(self.x_speed) < 10:
                self.x_animation = False

    def create_bounce_sound(self):
        frequency = abs(self.vy)
        duration = abs(self.vy) / 500

        square = Synth.square(10000, frequency / 2, duration)
        noise = Synth.noise(10000, duration)
        fo = Synth.fadeout(duration)
        new_sound = (square + noise*fo) * fo ** 2
        sound = Synth.create_pygame_sound(new_sound)
        sound.set_volume(0.4)
        sound.play()

    def check_collision(self):
        if self.rect.top < self.linked_arena.rect.top:
            self.rect.top = self.linked_arena.rect.top
            self.y = self.rect.centery
            self.vy = abs(self.vy) * self.bounce
            if abs(self.vy) > self.PARTICLE_THRESHOLD_SPEED:
                PadSlamDust.spawn_bunch((self.rect.centerx, self.rect.top), self.vy, 20)
                ScreenShake.create(self.vy/50, 0.2, 0.25)
                self.create_bounce_sound()

        if self.rect.bottom > self.linked_arena.rect.bottom:
            self.rect.bottom = self.linked_arena.rect.bottom
            self.y = self.rect.centery +1
            self.vy = abs(self.vy) * -self.bounce

            if abs(self.vy) > self.PARTICLE_THRESHOLD_SPEED:
                print(self.vy)
                PadSlamDust.spawn_bunch((self.rect.centerx, self.rect.bottom), self.vy, 20)
                ScreenShake.create(self.vy/50, 0.2, 0.25)
                self.create_bounce_sound()

    @classmethod
    def update(cls, delta):
        for pad in cls.PADS:
            pad.update_pos(delta)
            pad.update_rect()
            pad.check_collision()
            pad.update_animation(delta)

    def animate(self, speed):
        self.x_animation = True
        self.x_speed = speed

    def draw(self, surface):
        rect = self.rect.move(self.x_offset, 0)

        pygame.draw.rect(surface, (0, 0, 0), rect.inflate(2, 2), 0, 2)
        pygame.draw.rect(surface, (255, 255, 255), rect, 0, 2)

    @classmethod
    def draw_all(cls, surface):
        for pad in cls.PADS:
            pad.draw(surface)
