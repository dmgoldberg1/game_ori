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

        # расположение на экране
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

        # характеритики
        self.hero_widht = self.image.get_rect()[2]
        self.hero_height = self.image.get_rect()[3]

        self.last_position = pygame.Rect(self.rect)

        self.x_vel = 0
        self.y_vel = 0

        self.mask = pygame.mask.from_surface(self.image)

        # up, down кнопки
        self.ud_buttons = [119, 1073741906]
        # left, right кнопки
        self.lr_buttons = {97: -8,
                           100: 8,
                           1073741904: -8,
                           1073741903: 8}

    def update(self, *args):
        # обработка событий
        if args:
            if args[0].type == pygame.KEYDOWN and timer_nps[0]:
                self.continue_moving_x = True

                if self.state['на земле']:
                    if args[0].key in self.ud_buttons:
                        self.y_vel = -33
                        self.state['на земле'] = False

                if args[0].key in self.lr_buttons:
                    self.x_vel = self.lr_buttons[args[0].key]

            if args[0].type == pygame.KEYUP:
                self.continue_moving_x = False
                if self.state['на земле']:
                    self.x_vel = 0

        # обработка статуса положения
        if not self.state['на земле']:
            self.y_vel += 2
        else:
            self.y_vel = 0
            if not self.continue_moving_x:
                if 1 > abs(self.x_vel) > 0:
                    self.x_vel -= 2 * (self.x_vel / abs(self.x_vel))
                else:
                    self.x_vel = 0

        # обработка пересечений
        print(self.state['на земле'])
        self.rect = self.rect.move(self.x_vel, self.y_vel)
        self.position = pygame.Rect(self.rect)

        # print(self.position, '     ',self.last_position)

        for i in self.platform_sprite_group:
            # print(i.mask.get_bounding_rects()[0])
            a, b, c, d = i.mask.get_bounding_rects()[0][:4]
            platform_rect = pygame.Rect(i.rect[0] + a, i.rect[1] + b + 5, c, d)

            # линия пересечения персонажа по 4 направлениям
            down_hero_line = ((self.position.centerx, self.position.bottom),
                              (self.last_position.centerx, self.last_position.bottom))
            up_hero_line = ((self.position.centerx, self.position.top),
                            (self.last_position.centerx, self.last_position.top))
            left_hero_line = ((self.position.left, self.position.centery),
                              (self.last_position.left, self.last_position.centery))
            right_hero_line = ((self.position.right, self.position.centery),
                               (self.last_position.right, self.last_position.centery))

            # поиск пересечения персонажем по 4 направлениям
            collide_down = platform_rect.clipline(down_hero_line)
            collide_up = platform_rect.clipline(up_hero_line)
            collide_left = platform_rect.clipline(left_hero_line)
            collide_right = platform_rect.clipline(right_hero_line)

            # print(collide, line, platform_rect)
            if any([collide_down, collide_up, collide_left, collide_right]):
                # обработка пересечения с низом персонажа
                if collide_down:
                    print('d')
                    if self.state['на земле']:
                        self.y_vel = 0
                    if not platform_rect.collidepoint(self.last_position.centerx, self.last_position.bottom):
                        self.state['на земле'] = True
                        self.rect = self.rect.move((collide_down[-1][0] - self.rect.width // 2) - self.rect.x,
                                                   (collide_down[-1][1] - self.rect.height) - self.rect.y)
                    # self.rect = pygame.Rect(collide_down[-1][0] - self.rect.width // 2,
                    #                         collide_down[-1][1] - self.rect.height,
                    #                         self.rect.width, self.rect.height)
                # обработка пересечения с верхом персонажа
                elif collide_up:
                    print('u')
                    self.y_vel = - self.y_vel * 0.9
                    self.state['на земле'] = False
                    print(collide_up)
                    self.rect.move(collide_up[0][0] - self.rect.width // 2,
                                   collide_up[0][1])
                    self.rect = pygame.Rect(collide_up[0][0] - self.rect.width // 2,
                                            collide_up[0][1] - self.rect.height,
                                            self.rect.width, self.rect.height)
                # обработка пересечения с левом персонажа
                elif collide_left:
                    print('l')
                    # self.rect = pygame.Rect(collide[-1][0] - self.rect[2] // 2, self.rect.y,
                    #                         self.rect[2], self.rect[3])
                # обработка пересечения с правом персонажа
                elif collide_right:
                    print('r')
                    # self.rect = pygame.Rect(collide[-1][0] - self.rect[2] // 2, self.rect.y,
                    #                         self.rect[2], self.rect[3])
                self.position = pygame.Rect(self.rect)

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

# if collide_top_left:
#     print('t_l')
#     if not platform_rect.collidepoint(self.last_position.right, self.last_position.top):
#         print(collide_top_left)
#         self.y_vel = 0
#         x = min(collide_top_left[0][0], collide_top_left[-1][0])
#         y = max(collide_top_left[0][1], collide_top_left[-1][1])
#         self.rect = self.rect.move(x - self.rect.x,
#                                    (y - self.rect.y + 1))

# # обработка пересечения с левом персонажа
# if collide_left_down:
#     print('l_d')
#     if not platform_rect.collidepoint(self.last_position.left, self.last_position.bottom):
#         print(collide_left_down)
#         self.x_vel = 0
#         # self.rect = self.rect.move((collide_left_down[0][0] - self.rect.width) - self.rect.x,
#         #                            (collide_left_down[0][1] - self.rect.y + 1))
#
# elif collide_left_top:
#     print('l_t')
#     if not platform_rect.collidepoint(self.last_position.left, self.last_position.top):
#         print(collide_left_top)
#         self.x_vel = 0
#         # self.rect = self.rect.move((collide_left_top[0][0]) - self.rect.x,
#         #                            (collide_left_top[0][1] - self.rect.y + 1))

# elif collide_left:
#     print('l')
#     # self.rect = pygame.Rect(collide[-1][0] - self.rect[2] // 2, self.rect.y,
#     #                         self.rect[2], self.rect[3])
# # обработка пересечения с правом персонажа
# elif collide_right:
#     print('r')
#     # self.rect = pygame.Rect(collide[-1][0] - self.rect[2] // 2, self.rect.y,
#     #                         self.rect[2], self.rect[3])