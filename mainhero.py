# импорты:
# работа с БД
import os
import sqlite3
# структура игры
import pygame
# неиграбельные персонажи
from data import timer_npc
# вспомогательные функции
from utilities import load_image, skill_check

# музыка
pygame.mixer.pre_init(44100, -16, 1, 512)
sound_down = pygame.mixer.Sound("data\\music\\gluhoy-zvuk-padeniya-myagkogo-predmeta.wav")
sound_down.set_volume(0.8)



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
    image = pygame.transform.scale(image, (151 // 2, 186 // 2))

    def __init__(self, group, platform_sprite_group, null_object):
        super().__init__(group)
        self.group = group
        self.platform_sprite_group = platform_sprite_group
        self.state = {'на земле': True,
                      'карабкается': False}

        # работа с анимацией
        self.moving_statuses = {'straight': [True, 'animation\\mainhero2\\mainhero\\straight\\', 12],
                                'left': [True, 'animation\\mainhero2\\mainhero\\left\\', 8],
                                'right': [True, 'animation\\mainhero2\\mainhero\\right\\', 8]}
        self.image = load_image("animation\\mainhero2\\mainhero\\straight\\1.png")
        self.image = pygame.transform.scale(self.image, (50, 75))
        self.animation_counter = 1
        self.status_direct = 'straight'

        # константы
        self.continue_moving_x = False
        self.hit = False
        self.hit_timer = 0
        self.in_air = True
        self.button_lr_pressed = False
        self.pause = False
        self.allow = False
        self.null_object = null_object
        self.jump_count = 1 + skill_check('двойной прыжок')
        self.death = False

        # игровые моменты
        self.allow = False
        self.platform_type = None
        self.platform = None
        self.hp = 10

        # расположение на экране
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.y = 200

        # характеритики
        self.hero_widht = self.image.get_rect()[2]
        self.hero_height = self.image.get_rect()[3]

        self.last_position = pygame.Rect(self.rect)
        self.position = pygame.Rect(self.rect)

        self.x_vel = 0
        self.y_vel = 0

        self.mask = pygame.mask.from_surface(self.image)

        # up, down кнопки
        self.ud_buttons = [self.get_from_db('Прыжок'), 1073741906]
        # left, right кнопки
        self.lr_buttons = {self.get_from_db('Влево'): -8,
                           self.get_from_db('Вправо'): 8,
                           1073741904: -8,
                           1073741903: 8}

    def animation_image(self, type_of_moving):
        for key in self.moving_statuses.keys():
            if key != type_of_moving:
                self.moving_statuses[key][0] = False
            else:
                if not self.moving_statuses[key][0]:
                    self.moving_statuses[key][0] = True
                    self.animation_counter = 0
        stat, name, count = self.moving_statuses[type_of_moving]
        self.animation_counter = (self.animation_counter + 1) % count
        self.image = load_image(f"{name}{self.animation_counter + 1}.png")
        self.image = pygame.transform.scale(self.image, (50, 75))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.width, self.rect.height = self.image.get_rect()[2:]

    def get_from_db(self, db_link):
        con = sqlite3.connect(os.path.join('data', 'storage.db'))
        cur = con.cursor()
        result = cur.execute("""SELECT nums FROM binds WHERE name = ?""", (db_link,)).fetchall()
        con.close()
        return result[0][0]

    def update(self, *args):
        # обновление биндов во время работы игры
        if not self.lr_buttons != {self.get_from_db('Влево'): -8,
                                   self.get_from_db('Вправо'): 8,
                                   1073741904: -8,
                                   1073741903: 8}:
            self.lr_buttons = {self.get_from_db('Влево'): -8,
                               self.get_from_db('Вправо'): 8,
                               1073741904: -8,
                               1073741903: 8}

        if self.ud_buttons != [self.get_from_db('Прыжок'), 1073741906]:
            self.ud_buttons = [self.get_from_db('Прыжок'), 1073741906]

        # прогрузка позиции
        if not self.allow:
            # убираем скорости
            if self.x_vel or self.y_vel:
                self.x_vel = 0
                self.y_vel = 0

            # достаём абсолютные координаты из БД
            con = sqlite3.connect(os.path.join('data', 'storage.db'))
            cur = con.cursor()
            result = cur.execute("""SELECT x, y FROM saved_coordinates WHERE tag = ?""",
                                 ('герой',)).fetchall()[0]
            con.close()

            # расчёт нужного движения
            # для x'а
            if self.rect.x - self.null_object.rect.x < result[0]:
                move_x = 1
            elif self.rect.x - self.null_object.rect.x > result[0]:
                move_x = -1
            else:
                move_x = 0
            move_x *= 10 if (result[0] - (self.rect.x - self.null_object.rect.x)) % 10 == 0 else 1
            move_x *= 10 if (result[0] - (self.rect.x - self.null_object.rect.x)) % 100 == 0 else 1
            move_x *= 10 if (result[0] - (self.rect.x - self.null_object.rect.x)) % 1000 == 0 else 1

            # для y'а
            if self.rect.y - self.null_object.rect.y < result[1]:
                move_y = 1
            elif self.rect.y - self.null_object.rect.y > result[1]:
                move_y = -1
            else:
                move_y = 0
            move_y *= 10 if (result[1] - (self.rect.y - self.null_object.rect.y)) % 10 == 0 else 1
            move_y *= 10 if (result[1] - (self.rect.y - self.null_object.rect.y)) % 100 == 0 else 1
            move_y *= 10 if (result[1] - (self.rect.y - self.null_object.rect.y)) % 1000 == 0 else 1

            # if для остановки на месте назаначения
            if not move_x and not move_y:
                self.allow = True

            # само движение
            self.rect = self.rect.move(move_x, move_y)

        # обработка событий
        elif self.allow and args:
            if args[0].type == pygame.KEYDOWN and timer_npc[0]:
                self.continue_moving_x = True

                if self.jump_count:
                    if args[0].key in self.ud_buttons:
                        self.y_vel = -33
                        self.state['на земле'] = False
                        self.jump_count -= 1

                if args[0].key in self.lr_buttons:
                    self.x_vel = self.lr_buttons[args[0].key]
                    self.button_lr_pressed = True

            if args[0].type == pygame.KEYUP and args[0].key in self.lr_buttons:
                self.continue_moving_x = False
                self.button_lr_pressed = False

        # движение исходящее из события
        elif self.allow:
            # обработка платформы
            if self.platform_type == 'slippery':
                self.continue_moving_x = True
            elif self.platform_type == 'fire':
                self.hp -= 1
            else:
                if not self.button_lr_pressed:
                    self.continue_moving_x = False

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

            # подготовка к обработке пересечений
            self.rect = self.rect.move(self.x_vel, self.y_vel)
            self.position = pygame.Rect(self.rect)
            self.in_air = True

            # обработка пересечений - цикл по пересечению с платформами
            platforms = []
            for p in self.platform_sprite_group:
                for i in p:
                    a, b, c, d = i.mask.get_bounding_rects()[0][:4]
                    platform = i
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
                    center_hero_line_left = ((self.position.left, self.position.centery),
                                             (self.last_position.left, self.last_position.centery))
                    center_hero_line_right = ((self.position.right, self.position.centery),
                                              (self.last_position.right, self.last_position.centery))

                    # поиск пересечения персонажем по 4 углам
                    collide_down_left = platform_rect.clipline(down_hero_line_left)
                    collide_down_right = platform_rect.clipline(down_hero_line_right)
                    collide_top_left = platform_rect.clipline(top_hero_line_left)
                    collide_top_right = platform_rect.clipline(top_hero_line_right)
                    collide_center_left = platform_rect.clipline(center_hero_line_left)
                    collide_center_right = platform_rect.clipline(center_hero_line_right)

                    if any([collide_down_right, collide_down_left, collide_top_right, collide_top_left,
                            collide_center_left, collide_center_right]):
                        self.in_air = False
                        if collide_center_left:
                            x = max(collide_center_left[0][0], collide_center_left[-1][0])
                            if x == collide_center_left[0][0]:
                                y = collide_center_left[0][1]
                            else:
                                y = collide_center_left[-1][1]
                            if not platform_rect.collidepoint(self.last_position.left, self.last_position.centery):
                                self.rect = self.rect.move(x - self.rect.x, (y - self.rect.y - self.rect.height // 2))

                        # обработка пересечения с центром - правом персонажа
                        if collide_center_right:
                            x = min(collide_center_right[0][0], collide_center_right[-1][0])
                            if x == collide_center_right[0][0]:
                                y = collide_center_right[0][1]
                            else:
                                y = collide_center_right[-1][1]
                            if not platform_rect.collidepoint(self.last_position.right, self.last_position.centery):
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                           (y - self.rect.y - self.rect.height // 2))
                        # обработка пересечения с низом - правом персонажа
                        if collide_down_right:
                            if self.state['на земле']:
                                self.y_vel = 0
                            if not platform_rect.collidepoint(self.last_position.right, self.last_position.bottom):
                                sound_down.play()
                                self.platform_type = platform.platform_type
                                self.y_vel = 0
                                self.state['на земле'] = True
                                x = max(collide_down_right[0][0], collide_down_right[-1][0])
                                y = min(collide_down_right[0][1], collide_down_right[-1][1])
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                           (y - self.rect.height - self.rect.y))

                        # обработка пересечения с низом - левом персонажа
                        if collide_down_left:
                            if self.state['на земле']:
                                self.y_vel = 0
                            if not platform_rect.collidepoint(self.last_position.left, self.last_position.bottom):
                                sound_down.play()
                                self.platform_type = platform.platform_type
                                self.y_vel = 0
                                self.state['на земле'] = True
                                x = min(collide_down_left[0][0], collide_down_left[-1][0])
                                y = min(collide_down_left[0][1], collide_down_left[-1][1])
                                self.rect = self.rect.move(x - self.rect.x,
                                                           (y - self.rect.height - self.rect.y))

                        # обработка пересечения с верхом - правом персонажа
                        if collide_top_right:
                            # врезается в потолок, стоя на земле
                            if self.state['на земле']:
                                self.y_vel = 0
                                x = min(collide_top_right[0][0], collide_top_right[-1][0])
                                y = max(collide_top_right[0][1], collide_top_right[-1][1])
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width - 1,
                                                           (y - self.rect.y))
                            # врезается в потолок, в воздухе
                            elif not platform_rect.collidepoint(self.last_position.right, self.last_position.top):
                                self.state['на земле'] = False
                                self.y_vel = 0
                                x = min(collide_top_right[0][0], collide_top_right[-1][0])
                                y = max(collide_top_right[0][1], collide_top_right[-1][1])
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                           (y - self.rect.y + 1))

                        # обработка пересечения с верхом - левом персонажа
                        if collide_top_left:
                            # врезается в потолок, стоя на земле
                            if self.state['на земле']:
                                self.y_vel = 0
                                x = max(collide_top_left[0][0], collide_top_left[-1][0])
                                y = max(collide_top_left[0][1], collide_top_left[-1][1])
                                self.rect = self.rect.move(x - self.rect.x + 1,
                                                           (y - self.rect.y))
                            # врезается в потолок, в воздухе
                            elif not platform_rect.collidepoint(self.last_position.left, self.last_position.top):
                                self.state['на земле'] = False
                                self.y_vel = 0
                                x = max(collide_top_left[0][0], collide_top_left[-1][0])
                                y = max(collide_top_left[0][1], collide_top_left[-1][1])
                                self.rect = self.rect.move(x - self.rect.x,
                                                           (y - self.rect.y + 1))

                        # обновление позиции
                        self.position = pygame.Rect(self.rect)

                        platforms.append([i, platform_rect.collidepoint(self.position.left, self.position.bottom),
                                          platform_rect.collidepoint(self.position.right, self.position.bottom)])
            if any(filter(lambda x: x[1] or x[2], platforms)):
                self.state['на земле'] = True
                self.jump_count = 1 + skill_check('двойной прыжок')
            else:
                self.state['на земле'] = False

            # если не было пересечений
            if self.in_air:
                self.state['на земле'] = False

            # обновление изображения
            if self.position.x == self.last_position.x:
                self.animation_image('straight')
                self.status_direct = 'straight'
            elif self.position.x > self.last_position.x:
                self.animation_image('right')
                self.status_direct = 'right'
            elif self.position.x < self.last_position.x:
                self.animation_image('left')
                self.status_direct = 'left'


            # упал - умер - возродился
            # теперь: набрал большую скорость - умер - возродился
            if self.y_vel > 100 or self.hp <= 0:
                self.allow = False
                self.hp = 10
                # сохраняем позицию игрока
                con = sqlite3.connect(os.path.join('data', 'storage.db'))
                cur = con.cursor()

                dx = 150
                dy = 200
                result = cur.execute("""UPDATE saved_coordinates SET x = ? WHERE tag = ?""", (dx, 'герой')).fetchall()
                result = cur.execute("""UPDATE saved_coordinates SET y = ? WHERE tag = ?""", (dy, 'герой')).fetchall()

                con.commit()
                con.close()

                self.death = True


            # запоминаем старую позицию
            self.last_position = self.position
