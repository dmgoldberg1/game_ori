import os
import sys
import time
import pygame
from utilities import load_image, sprite_distance
from pygame.locals import *
import math
import random

all_sprites = pygame.sprite.Group()


class NPC(pygame.sprite.Sprite):
    image = load_image("temp.png", colorkey=(255, 255, 255))
    print(image.get_rect())
    image = pygame.transform.scale(image, (151 // 2, 186 // 2))

    def __init__(self, group, coords):
        super().__init__(group)
        self.group = group
        self.rect = self.image.get_rect(topleft=coords)

#npc
class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, coords):
        super().__init__(group)
        self.image = load_image('temp.png')
        self.rect = self.image.get_rect(topleft=coords)
        self.pos = pygame.math.Vector2(0, 0)
        self.vel = pygame.math.Vector2(0, 0)
        self.direction = random.randint(0, 1)  # 0 for Right, 1 for Left
        self.vel.x = random.randint(2, 6) / 2  # Randomized velocity of the generated enemy
        if self.direction == 0:
            self.pos.x = 0
            self.pos.y = 235
        if self.direction == 1:
            self.pos.x = 700
            self.pos.y = 235

    def update(self, *args):
        # Causes the enemy to change directions upon reaching the end of screen
        if self.pos.x >= 300:
            self.direction = 1
        elif self.pos.x <= 0:
            self.direction = 0
            self.pos.x += self.vel.x

        if self.direction == 0:
            self.pos.x += self.vel.x
        if self.direction == 1:
            self.pos.x -= self.vel.x

        self.rect.center = self.pos  # Updates rect
