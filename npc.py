import random

import pygame

from utilities import load_image

all_sprites = pygame.sprite.Group()

WIDTH, HEIGHT = 1000, 600


class NPC(pygame.sprite.Sprite):
    image = load_image("temp.png", colorkey=(255, 255, 255))
    # print(image.get_rect())
    image = pygame.transform.scale(image, (151 // 2, 186 // 2))

    def __init__(self, group, coords, text):
        super().__init__(group)
        self.group = group
        self.rect = self.image.get_rect(topleft=coords)

        # константы
        self.npc_visited = False
        self.npc_visit = False
        self.npc_time_visit = 0

        self.npc_font = pygame.font.SysFont('Comic Sans MS', 30)
        self.text_surface = self.npc_font.render(text, True, (0, 0, 0))


# npc jgk
class EnemyMelee(pygame.sprite.Sprite):
    def __init__(self, group, special_group, platform_sprite_group, platform, main_hero):
        super().__init__(group)
        self.image = load_image('temp.png')

        # создаем прямоугольник - объект
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = platform.rect.x, platform.rect.y - self.rect.h
        self.mask = pygame.mask.from_surface(self.image)

        # константы
        self.pause = False

        # константы для движения
        self.vel = pygame.math.Vector2(0, 0)
        self.direction = random.randint(0, 1)  # 0 for Right, 1 for Left
        self.vel.x = random.randint(2, 6) / 2  # Randomized velocity of the generated enemy
        self.vel.y = -20
        self.gravity = 2

        # константы для платформ
        self.platform = platform
        self.platform_sprite_group = platform_sprite_group
        self.last_position = pygame.Rect(self.rect)
        self.state = {'на земле': False,
                      'карабкается': False}

        # константы для связи с главным героем
        self.main_hero = main_hero

        # добавление в группу врагов
        self.add(special_group)


    def update(self, *args):
        # pass
        # Causes the enemy to change directions upon reaching the end of screen
        # self.rect = self.rect.move(self.vel.x, self.vel.y)
        if not self.pause:
            if not args:
                self.main_hero_pos = self.main_hero.rect
                s = ((self.rect.x - self.main_hero_pos.x) ** 2 + (self.rect.y - self.main_hero_pos.y) ** 2) ** 0.5
                # print(s)

                self.position = pygame.Rect(self.rect)
                # if self.platform.rect.x <= self.position.x <= self.platform.rect.x + 10:
                #     self.direction = 0
                # elif self.platform.rect.x + self.platform.rect.w - 10 <= self.position.x <= self.platform.rect.x + self.platform.rect.w:
                #     self.direction = 1
                #     self.rect.x += self.vel.x

                if s < 500:
                    if round(self.main_hero_pos.x + self.main_hero_pos.w // 2) == round(self.position.x):
                        self.vel.x = 0
                    elif self.main_hero_pos.x + self.main_hero_pos.w // 2 < self.position.x:
                        self.vel.x = -random.randint(4, 8) / 2
                    else:
                        self.vel.x = random.randint(4, 8) / 2


                    if self.state['на земле']:
                        self.vel.y = 0
                        if self.main_hero_pos.y + self.main_hero_pos.h < self.position.y:
                            self.vel.y += -20
                            # print('qqqqqqqqqqqqqqqqqqqq')
                    else:
                        self.vel.y += self.gravity
                    print(self.vel.y)
                    self.rect.y += self.vel.y
                    self.rect.x += self.vel.x
                # print(self.state['на земле'], self.rect.y)

                platforms = []
                for i in self.platform_sprite_group:
                    # print(i.mask.get_bounding_rects()[0])
                    a, b, c, d = i.mask.get_bounding_rects()[0][:4]
                    platform_rect = pygame.Rect(i.rect[0] + a, i.rect[1] + b + 5, c, d)

                    # линия пересечения персонажа по 4 направлениям
                    down_hero_line_left = ((self.position.left, self.position.bottom),
                                           (self.last_position.left, self.last_position.bottom))
                    down_hero_line_right = ((self.position.right, self.position.bottom),
                                            (self.last_position.right, self.last_position.bottom))

                    collide_down_left = platform_rect.clipline(down_hero_line_left)
                    collide_down_right = platform_rect.clipline(down_hero_line_right)

                    if collide_down_right:
                        # print('d_r')
                        if not platform_rect.collidepoint(self.last_position.right, self.last_position.bottom):
                            # print(collide_down_right)
                            self.state['на земле'] = True
                            x = max(collide_down_right[0][0], collide_down_right[-1][0])
                            y = min(collide_down_right[0][1], collide_down_right[-1][1])
                            self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                       (y - self.rect.height - self.rect.y))

                    # обработка пересечения с низом - левом персонажа
                    if collide_down_left:
                        # print('d_l')
                        if not platform_rect.collidepoint(self.last_position.left, self.last_position.bottom):
                            # print(collide_down_left)
                            self.state['на земле'] = True
                            x = min(collide_down_left[0][0], collide_down_left[-1][0])
                            y = min(collide_down_left[0][1], collide_down_left[-1][1])
                            self.rect = self.rect.move(x - self.rect.x,
                                                       (y - self.rect.height - self.rect.y))
                    platforms.append([i, platform_rect.collidepoint(self.position.left, self.position.bottom),
                                      platform_rect.collidepoint(self.position.right, self.position.bottom)])
                    if any(filter(lambda x: x[1] or x[2], platforms)):
                        self.state['на земле'] = True
                        # self.platform_type = platform.platform_type
                        # self.platform = platform
                    else:
                        self.state['на земле'] = False

                    self.position = pygame.Rect(self.rect)
                self.last_position = self.position

                if pygame.sprite.collide_mask(self, self.main_hero):
                    print('aaaaaaa')
                    self.main_hero.hp -= 1

                # self.rect.center = self.pos  # Updates


class EnemyRangeFly(pygame.sprite.Sprite):
    def __init__(self, group, platform_sprite_group, coords):
        super().__init__(group)
        self.pause = False
        self.image = load_image('temp.png')
        self.rect = self.image.get_rect(topleft=coords)
        self.pos = pygame.math.Vector2(0, 0)
        self.pos.x = coords[0]
        self.pos.y = coords[1]
        self.vel = pygame.math.Vector2(0, 0)
        self.direction = random.randint(0, 1)  # 0 for Right, 1 for Left
        self.vel.x = random.randint(2, 6) / 2  # Randomized velocity of the generated enemy
        self.vel.y = random.randint(2, 6) / 2
        self.platform_sprite_group = platform_sprite_group
        self.last_position = pygame.Rect(self.rect)
        self.state = {'на земле': True,
                      'карабкается': False}

    def update(self, *args):
        if not self.pause:
            if not args:
                # Causes the enemy to change directions upon reaching the end of screen
                self.rect = self.rect.move(self.vel.x, self.vel.y)
                self.position = pygame.Rect(self.rect)
                if self.position.x >= 300:
                    self.direction = 1
                elif self.position.x <= 100:
                    self.direction = 0
                # self.pos.x += self.vel.x

                if self.direction == 0:
                    self.rect.x += self.vel.x

                    updown = random.randint(0, 2)

                    if updown == 0:
                        self.rect.y += self.vel.y

                    if updown == 1:
                        self.rect.y -= self.vel.y
                if self.direction == 1:
                    self.rect.x -= self.vel.x

                    updown = random.randint(0, 2)

                    if updown == 0:
                        self.rect.y += self.vel.y
                    if updown == 1:
                        self.rect.y -= self.vel.y
                for i in self.platform_sprite_group:
                    # print(i.mask.get_bounding_rects()[0])
                    a, b, c, d = i.mask.get_bounding_rects()[0][:4]
                    platform_rect = pygame.Rect(i.rect[0] + a, i.rect[1] + b + 5, c, d)

                    # линия пересечения персонажа по 4 направлениям
                    down_hero_line_left = ((self.position.left, self.position.bottom),
                                           (self.last_position.left, self.last_position.bottom))
                    down_hero_line_right = ((self.position.right, self.position.bottom),
                                            (self.last_position.right, self.last_position.bottom))
                    top_hero_line_left = ((self.position.left, self.position.top),
                                          (self.last_position.left, self.last_position.top))
                    top_hero_line_right = ((self.position.right, self.position.top),
                                           (self.last_position.right, self.last_position.top))

                    # поиск пересечения персонажем по 4 углам
                    collide_down_left = platform_rect.clipline(down_hero_line_left)
                    collide_down_right = platform_rect.clipline(down_hero_line_right)
                    collide_top_left = platform_rect.clipline(top_hero_line_left)
                    collide_top_right = platform_rect.clipline(top_hero_line_right)

                    if collide_down_right:
                        # print('d_r')
                        if self.state['на земле']:
                            self.vel.y = -1 * self.vel.y
                        if not platform_rect.collidepoint(self.last_position.right, self.last_position.bottom):
                            # print(collide_down_right)
                            self.vel.y = -1 * self.vel.y
                            self.state['на земле'] = True
                            x = max(collide_down_right[0][0], collide_down_right[-1][0])
                            y = min(collide_down_right[0][1], collide_down_right[-1][1])
                            self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                       (y - self.rect.height - self.rect.y))

                    # обработка пересечения с низом - левом персонажа
                    if collide_down_left:
                        # print('d_l')
                        if self.state['на земле']:
                            self.vel.y = -1 * self.vel.y
                        if not platform_rect.collidepoint(self.last_position.left, self.last_position.bottom):
                            # print(collide_down_left)
                            self.y_vel = -1 * self.vel.y
                            self.state['на земле'] = True
                            x = min(collide_down_left[0][0], collide_down_left[-1][0])
                            y = min(collide_down_left[0][1], collide_down_left[-1][1])
                            self.rect = self.rect.move(x - self.rect.x,
                                                       (y - self.rect.height - self.rect.y))

                    # обработка пересечения с верхом - правом персонажа
                    if collide_top_right:
                        # print('t_r')
                        # врезается в потолок, стоя на земле
                        if self.state['на земле']:
                            # print(collide_top_right)
                            self.vel.y = -1 * self.vel.y
                            x = min(collide_top_right[0][0], collide_top_right[-1][0])
                            y = max(collide_top_right[0][1], collide_top_right[-1][1])
                            self.rect = self.rect.move(x - self.rect.x - self.rect.width - 1,
                                                       (y - self.rect.y))
                        # врезается в потолок, в воздухе
                        elif not platform_rect.collidepoint(self.last_position.right, self.last_position.top):
                            # print(collide_top_right)
                            self.state['на земле'] = False
                            self.vel.y = -1 * self.vel.y
                            x = min(collide_top_right[0][0], collide_top_right[-1][0])
                            y = max(collide_top_right[0][1], collide_top_right[-1][1])
                            self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                       (y - self.rect.y + 1))

                    # обработка пересечения с верхом - левом персонажа
                    if collide_top_left:
                        # print('t_l')
                        # врезается в потолок, стоя на земле
                        if self.state['на земле']:
                            # print(collide_top_left)
                            self.vel.y = -1 * self.vel.y
                            x = max(collide_top_left[0][0], collide_top_left[-1][0])
                            y = max(collide_top_left[0][1], collide_top_left[-1][1])
                            self.rect = self.rect.move(x - self.rect.x + 1,
                                                       (y - self.rect.y))
                        # врезается в потолок, в воздухе
                        elif not platform_rect.collidepoint(self.last_position.left, self.last_position.top):
                            # print(collide_top_left)
                            self.state['на земле'] = False
                            self.vel.y = -1 * self.vel.y
                            x = max(collide_top_left[0][0], collide_top_left[-1][0])
                            y = max(collide_top_left[0][1], collide_top_left[-1][1])
                            self.rect = self.rect.move(x - self.rect.x,
                                                       (y - self.rect.y + 1))

                    # обновление позиции
                    self.position = pygame.Rect(self.rect)

                    # обновление статуса
                    if (platform_rect.collidepoint(self.position.left, self.position.bottom)) or \
                            (platform_rect.collidepoint(self.position.right, self.position.bottom)):
                        self.state['на земле'] = True
                    else:
                        self.state['на земле'] = False


# НЕ Сделано
class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, platform_sprite_group, coords):
        super().__init__(group)
        self.image = load_image('temp.png')
        self.rect = self.image.get_rect(topleft=coords)
        self.platform_sprite_group = platform_sprite_group
        self.pause = False
        self.x = coords[0]
        self.y = coords[1]
        self.speed_x = 8
        self.speed_y = 0
        self.dest_x = 0
        self.dest_y = 0

    def update(self, *args):
        if not self.pause:
            self.x += self.speed_x
