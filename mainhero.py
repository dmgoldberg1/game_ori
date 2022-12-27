import os
import sys
import time

import pygame
from utilities import load_image

# настройки окна
size = WIDHT, HEIGHT = 1000, 600
FPS = 20
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

pygame.init()

# спрайты
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()


# класс героя
class MainHero(pygame.sprite.Sprite):
    # картинка
    image = load_image("cat_hero.png", colorkey=(255, 255, 255))
    # print(image.get_rect())
    image = pygame.transform.scale(image, (151 // 2, 186 // 2))

    def __init__(self, group, platform_sprite_group, coords):
        super().__init__(group)
        self.group = group
        self.platform_sprite_group = platform_sprite_group
        self.state = {'на земле': True,
                      'карабкается': False}
        self.image = MainHero.image

        # константы
        self.collision = False
        self.continue_moving_x = False
        self.continue_moving_y = True

        # расположение на экране
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

        # характеритики
        self.hero_widht = self.image.get_rect()[2]
        self.hero_height = self.image.get_rect()[3]

        self.last_position = (self.rect.x, self.rect.y, self.rect.x + self.rect.w, self.rect.y + self.rect.h)

        self.x_vel = 0
        self.y_vel = 0

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):

        self.position = (self.rect.x, self.rect.y, self.rect.x + self.rect.w, self.rect.y + self.rect.h)

        # up, down кнопки
        ud_buttons = [119, 1073741906]
        # left, right кнопки
        lr_buttons = {97: -8,
                      100: 8,
                      1073741904: -8,
                      1073741903: 8}

        # обработка пересечений
        self.collision = False

        for i in self.platform_sprite_group:
            platform_position = (i.rect.x, i.rect.y, i.rect.x + i.rect.w, i.rect.y + i.rect.h)
            # print(platform_position)

            if self.last_position[1] < platform_position[2] <= self.position[3] and (
                    platform_position[0] <= self.position[0] <= platform_position[2] and
                    platform_position[0] <= self.position[2] <= platform_position[2]):
                self.state['на земле'] = True
                self.rect = self.rect.move(0, platform_position[2] - self.position[3])
                self.y_vel = 0
            # if pygame.sprite.collide_mask(self, i):
            #     place_collide = pygame.sprite.collide_mask(self, i)
            #     place_collide_for_height, place_collide_for_widht = place_collide[0], place_collide[1]
            #     # print(place_collide)
            #     if (self.hero_height - 30 < place_collide_for_height <= self.hero_height) and self.continue_moving_y:
            #         self.rect = self.rect.move(0, place_collide[1] - self.image.get_rect()[3])
            #         self.state['на земле'] = True
            #         self.collision = True
            #         self.continue_moving_y = True
            #     elif (place_collide[1] < self.image.get_rect()[3] - 60) and self.continue_moving_y:
            #         self.y_vel = - (self.y_vel) * 0.8
            #         self.continue_moving_y = False
            # if place_collide[0] < 10 and place_collide[1] <
        if not self.collision:
            self.state['на земле'] = False

        # обработка событий
        if args:
            if args[0].type == pygame.KEYDOWN:
                self.continue_moving_x = True

                if self.state['на земле']:
                    if args[0].key in ud_buttons:
                        self.y_vel = -33
                        self.state['на земле'] = False

                if args[0].key in lr_buttons:
                    self.x_vel = lr_buttons[args[0].key]

            if args[0].type == pygame.KEYUP:
                self.continue_moving_x = False
                if self.state['на земле']:
                    self.x_vel = 0

        # обработка статуса положения
        if not self.state['на земле']:
            self.y_vel += 2
            self.continue_moving_y = True
        else:
            self.y_vel = 0
            if not self.continue_moving_x:
                if 1 > abs(self.x_vel) > 0:
                    self.x_vel -= 2 * (self.x_vel / abs(self.x_vel))
                else:
                    self.x_vel = 0

        # надо это фиксить, делать всё через if-else будет ппц запарно
        self.rect = self.rect.move(self.x_vel, self.y_vel)

        # упал - умер - возродился
        if self.rect.y > HEIGHT:  # HEIGHT - берется из файла mainhero.py
            self.kill()
            MainHero(self.group, self.platform_sprite_group, (600, 250))

        # запоминаем старую позицию
        self.last_position = self.position


# добавление героя в спрайты
MainHero(all_sprites, platform_sprites, (200, 100))

# запуск симуляции
if __name__ == '__main__':
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if event.type == pygame.KEYDOWN:
            #     print(event.key)

            # отрисовка спрайта
            all_sprites.update(event)

        # зарисовка и загрузочный апдейт
        screen.fill((255, 255, 255))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
