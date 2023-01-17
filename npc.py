import random

import pygame

from utilities import load_image

import math

all_sprites = pygame.sprite.Group()

WIDTH, HEIGHT = 1000, 600


class NPC(pygame.sprite.Sprite):
    image = load_image("animation/npc.jpg", colorkey=(255, 255, 255))
    # print(image.get_rect())
    image = pygame.transform.scale(image, (90, 90))

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
        self.image = load_image('animation/enemy_melee.jpg', colorkey=(255, 255, 255))
        self.image = pygame.transform.scale(self.image, (50, 50))

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
                    # print(self.vel.y)
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
                    # print('aaaaaaa')
                    self.main_hero.hp -= 1

                # self.rect.center = self.pos  # Updates


class EnemyRangeFly(pygame.sprite.Sprite):
    def __init__(self, group, platform_sprite_group, coords):
        super().__init__(group)
        self.pause = False
        self.image = load_image('animation/enemy_range.jpg', colorkey=(255, 255, 255))
        self.image = pygame.transform.scale(self.image, (50, 50))
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



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x_enemy, y_enemy, x_hero, y_hero, group, platform_sprite_group):
        super().__init__(group)
        self.platform_sprite_group = platform_sprite_group
        self.image = load_image('temp.png', colorkey=(255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x_enemy
        self.rect.y = y_enemy

        self.last_position = pygame.Rect(self.rect)
        self.position = pygame.Rect(self.rect)

        self.state = {'на земле': True,
                      'карабкается': False}

        self.pos = (x_enemy, y_enemy)
        mx, my = x_hero, y_hero
        self.dir = (mx - x_enemy, my - y_enemy)
        length = math.hypot(*self.dir)
        self.fire = False
        self.fire_timer = 0
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0] / length, self.dir[1] / length)
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

        # self.bullet = pygame.Surface((7, 2)).convert_alpha()
        # self.bullet.fill((255, 255, 255))
        self.image = pygame.transform.rotate(self.image, angle)
        self.speed = 5

    def update(self, *args):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)
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
                    pass
                    # self.kill()
                if not platform_rect.collidepoint(self.last_position.right, self.last_position.bottom):
                    # print(collide_down_right)
                    # self.kill()
                    self.state['на земле'] = True
                    x = max(collide_down_right[0][0], collide_down_right[-1][0])
                    y = min(collide_down_right[0][1], collide_down_right[-1][1])
                    self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                               (y - self.rect.height - self.rect.y))

            # обработка пересечения с низом - левом персонажа
            if collide_down_left:
                # print('d_l')
                if self.state['на земле']:
                    pass
                    # self.kill()
                if not platform_rect.collidepoint(self.last_position.left, self.last_position.bottom):
                    # print(collide_down_left)
                    # self.kill()
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
                    # self.kill()
                    x = min(collide_top_right[0][0], collide_top_right[-1][0])
                    y = max(collide_top_right[0][1], collide_top_right[-1][1])
                    self.rect = self.rect.move(x - self.rect.x - self.rect.width - 1,
                                               (y - self.rect.y))
                # врезается в потолок, в воздухе
                elif not platform_rect.collidepoint(self.last_position.right, self.last_position.top):
                    # print(collide_top_right)
                    self.state['на земле'] = False
                    # self.kill()
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
                    # self.kill()
                    x = max(collide_top_left[0][0], collide_top_left[-1][0])
                    y = max(collide_top_left[0][1], collide_top_left[-1][1])
                    self.rect = self.rect.move(x - self.rect.x + 1,
                                               (y - self.rect.y))
                # врезается в потолок, в воздухе
                elif not platform_rect.collidepoint(self.last_position.left, self.last_position.top):
                    # print(collide_top_left)
                    self.state['на земле'] = False
                    # dddself.kill()
                    x = max(collide_top_left[0][0], collide_top_left[-1][0])
                    y = max(collide_top_left[0][1], collide_top_left[-1][1])
                    self.rect = self.rect.move(x - self.rect.x,
                                               (y - self.rect.y + 1))

            # обновление позиции
            self.position = pygame.Rect(self.rect)

    def draw(self, surf):
        bullet_rect = self.image.get_rect(center=self.pos)
        surf.blit(self.image, bullet_rect)


class Boss(pygame.sprite.Sprite):
    def __init__(self, group, special_group, platform_sprite_group, platform, main_hero):
        super().__init__(group)
        self.image = load_image('animation/boss.jpg', colorkey=(255, 255, 255))
        self.image = pygame.transform.scale(self.image, (70, 70))

        # создаем прямоугольник - объект
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = platform.rect.x, platform.rect.y - self.rect.h
        self.mask = pygame.mask.from_surface(self.image)
        # print('ПЛАТФОРМА', platform.rect.topleft)

        # константы
        self.pause = False

        # константы для движения
        self.vel = pygame.math.Vector2(0, 0)
        self.direction = random.randint(0, 1)  # 0 for Right, 1 for Left
        self.vel.x = random.randint(2, 6) / 2  # Randomized velocity of the generated enemy
        #self.vel.x = 0
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
                # print('BOSS pos', self.position.x)

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
                            pass
                            # print('qqqqqqqqqqqqqqqqqqqq')
                    else:
                        self.vel.y += self.gravity
                    # print(self.vel.y)
                    if self.position.x < 650:
                        self.rect.x = 670
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
                    # print('aaaaaaa')
                    self.main_hero.hp -= 1

                # self.rect.center = self.pos  # Updates

                
