import pygame
import os
import sys
from platform import Platform
from utilities import load_image


# класс героя
class MainHero(pygame.sprite.Sprite):
    # картинка
    image = load_image("temp.png", colorkey=(255, 255, 255))
    image = pygame.transform.scale(image, (100, 100))

    def __init__(self, group, coords):
        super().__init__(group)
        self.group = group
        self.state = {'на земле': True,
                      'карабкается': False}
        self.image = MainHero.image
        self.collision = False
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

        self.x_vel = 0
        self.y_vel = 0

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        # up, down кнопки
        ud_buttons = [119, 1073741906]
        # left, right кнопки
        lr_buttons = {97: -7,
                      100: 7,
                      1073741904: -7,
                      1073741903: 7}

        self.collision = False

        for i in platform_sprites:
            if pygame.sprite.collide_mask(self, i):
                self.state['на земле'] = True
                self.collision = True
        if not self.collision:
            self.state['на земле'] = False

        # тестовое движение
        if args:
            if args[0].type == pygame.KEYDOWN:
                if self.state['на земле']:
                    if args[0].key in ud_buttons:
                        self.y_vel = -33
                        self.state['на земле'] = False

                if args[0].key in lr_buttons:
                    self.x_vel = lr_buttons[args[0].key]

            if args[0].type == pygame.KEYUP:
                if self.state['на земле']:
                    self.x_vel = 0

        # симуляция гравитации
        # стопить при поверхности
        if not self.state['на земле']:
            self.y_vel += 2

        else:
            self.y_vel = 0

        # надо это фиксить, делать всё через if-else будет ппц запарно
        self.rect = self.rect.move(self.x_vel, self.y_vel)

        if self.rect.y > HEIGHT:
            self.kill()
            MainHero(self.group, (500, 250))
