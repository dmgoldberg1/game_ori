import os
import sys
import time
import pygame
from utilities import load_image, sprite_distance
from pygame.locals import *
# import pygame_ai as pai
import math

all_sprites = pygame.sprite.Group()


class NPC(pygame.sprite.Sprite):
    image = load_image("temp.png", colorkey=(255, 255, 255))
    print(image.get_rect())
    image = pygame.transform.scale(image, (151 // 2, 186 // 2))

    def __init__(self, group, coords):
        super().__init__(group)
        self.group = group
        self.rect = self.image.get_rect(topleft=coords)


# class Enemy(pai.gameobject.GameObject):
#
#     def __init__(self, pos=(0, 0)):
#
#         img = pygame.Surface((10, 10)).convert_alpha()
#         img.fill((255, 255, 255, 0))
#
#         pygame.draw.circle(img, (255, 0, 0), (5, 5), 5)
#
#         super(Enemy, self).__init__(
#             img_surf=img,
#             pos=pos,
#             max_speed=10,
#             max_accel=40,
#             max_rotation=40,
#             max_angular_accel=30
#         )
#
#         self.ai = pai.steering.kinematic.NullSteering()
#
#     def update(self, tick):
#         gravity = pai.steering.kinematic.SteeringOutput()
#         gravity.linear[1] = 300
#
#
#         steering = self.ai.get_steering()
#         self.steer_x(steering, tick)
#
#         velocity = self.velocity + gravity.linear * tick
#
#         self.rect.move_ip(velocity)
#
#
# class Enemy_test(pai.gameobject.GameObject):
#
#     def __init__(self, pos=(0, 0)):
#         img = pygame.Surface((10, 10)).convert_alpha()
#         img.fill((255, 255, 255, 0))
#         pygame.draw.circle(img, (255, 0, 0), (5, 5), 5)
#         super(Enemy_test, self).__init__(
#             img_surf=img,
#             pos=pos,
#             max_speed=25,
#             max_accel=40,
#             max_rotation=40,
#             max_angular_accel=30
#         )
#         self.ai = pai.steering.kinematic.NullSteering()
#
#     def update(self, tick):
#         steering = self.ai.get_steering()
#         self.steer(steering, tick)
#         self.rect.move_ip(self.velocity)
#
#
# class PathCosine(pai.steering.path.Path):
#
#     def __init__(self, start, height, length):
#         self.start = start
#         self.height = height
#         self.length = length
#
#         def cosine_path(self, x):
#             y = self.start[1] + math.cos(x) * self.height
#             return x, y
#
#         super(PathCosine, self).__init__(
#             path_func=cosine_path,
#             domain_start=int(self.start[0]),
#             domain_end=int(self.start[0] + length),
#             increment=30
#         )
