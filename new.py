import pygame
import os
import sqlite3
from data import timer_npc
from utilities import load_image, move_to_the_point

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

    def __init__(self, group, platform_sprite_group):
        super().__init__(group)
        self.group = group
        self.platform_sprite_group = platform_sprite_group
        self.state = {'на земле': True,
                      'карабкается': False}
        self.image = MainHero.image

        # константы
        self.continue_moving_x = False
        self.hit = False
        self.hit_timer = 0
        self.in_air = True
        self.button_lr_pressed = False
        self.pause = False

        # игровые моменты
        self.platform_type = None
        self.platform = None
        self.hp = 10

        # расположение на экране
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        move_to_the_point(self, 'герой')

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

    def get_from_db(self, db_link):
        con = sqlite3.connect(os.path.join('data', 'storage.db'))
        cur = con.cursor()
        result = cur.execute("""SELECT nums FROM binds WHERE name = ?""", (db_link,)).fetchall()
        con.close()
        return result[0][0]

    def update(self, *args):
        if not self.allow and len(args) == 2:
            con = sqlite3.connect(os.path.join('data', 'storage.db'))
            cur = con.cursor()
            result = cur.execute("""SELECT x, y FROM saved_coordinates WHERE tag = ?""", ('герой',)).fetchall()[0]
            con.close()
            print(self.rect.x)
            print(result[0])
            print(-(self.rect.x - result[0]))
            print()
            print(self.rect.y)
            print(result[1])
            print(-(self.rect.y - result[1] + 20))
            self.rect = self.rect.move(-(self.rect.x - result[0]),
                                       -(self.rect.y - result[1] + 20))
            self.allow = True

        elif self.allow:
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

        # обработка событий
        if args:
            if args[0].type == pygame.KEYDOWN and timer_npc[0]:
                self.continue_moving_x = True

                if self.state['на земле']:
                    if args[0].key in self.ud_buttons:
                        self.y_vel = -33
                        self.state['на земле'] = False

                if args[0].key in self.lr_buttons:
                    self.x_vel = self.lr_buttons[args[0].key]
                    self.button_lr_pressed = True

            if args[0].type == pygame.KEYUP and args[0].key in self.lr_buttons:
                self.continue_moving_x = False
                self.button_lr_pressed = False
        else:
            # обработка платформы
            if self.platform_type == 'slippery':
                self.continue_moving_x = True
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
            # print(self.platform_sprite_group)
            platforms = []
            for p in self.platform_sprite_group:
                for i in p:
                    # print(i.mask.get_bounding_rects()[0])
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

                    # print(collide, line11, platform_rect)
                    if any([collide_down_right, collide_down_left, collide_top_right, collide_top_left,
                            collide_center_left, collide_center_right]):
                        self.in_air = False
                        if collide_center_left:
                            print('c_l')
                            print(collide_center_left)
                            x = max(collide_center_left[0][0], collide_center_left[-1][0])
                            if x == collide_center_left[0][0]:
                                y = collide_center_left[0][1]
                            else:
                                y = collide_center_left[-1][1]
                            if not platform_rect.collidepoint(self.last_position.left, self.last_position.centery):
                                self.rect = self.rect.move(x - self.rect.x, (y - self.rect.y - self.rect.height // 2))

                        # обработка пересечения с центром - правом персонажа
                        if collide_center_right:
                            print('c_r')
                            print(collide_center_right)
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
                            print('d_r')
                            if self.state['на земле']:
                                self.y_vel = 0
                            if not platform_rect.collidepoint(self.last_position.right, self.last_position.bottom):
                                print(collide_down_right)
                                self.y_vel = 0
                                self.state['на земле'] = True
                                x = max(collide_down_right[0][0], collide_down_right[-1][0])
                                y = min(collide_down_right[0][1], collide_down_right[-1][1])
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                           (y - self.rect.height - self.rect.y))

                        # обработка пересечения с низом - левом персонажа
                        if collide_down_left:
                            print('d_l')
                            if self.state['на земле']:
                                self.y_vel = 0
                            if not platform_rect.collidepoint(self.last_position.left, self.last_position.bottom):
                                print(collide_down_left)
                                self.y_vel = 0
                                self.state['на земле'] = True
                                x = min(collide_down_left[0][0], collide_down_left[-1][0])
                                y = min(collide_down_left[0][1], collide_down_left[-1][1])
                                self.rect = self.rect.move(x - self.rect.x,
                                                           (y - self.rect.height - self.rect.y))

                        # обработка пересечения с верхом - правом персонажа
                        if collide_top_right:
                            print('t_r')
                            # врезается в потолок, стоя на земле
                            if self.state['на земле']:
                                print(collide_top_right)
                                self.y_vel = 0
                                x = min(collide_top_right[0][0], collide_top_right[-1][0])
                                y = max(collide_top_right[0][1], collide_top_right[-1][1])
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width - 1,
                                                           (y - self.rect.y))
                            # врезается в потолок, в воздухе
                            elif not platform_rect.collidepoint(self.last_position.right, self.last_position.top):
                                print(collide_top_right)
                                self.state['на земле'] = False
                                self.y_vel = 0
                                x = min(collide_top_right[0][0], collide_top_right[-1][0])
                                y = max(collide_top_right[0][1], collide_top_right[-1][1])
                                self.rect = self.rect.move(x - self.rect.x - self.rect.width,
                                                           (y - self.rect.y + 1))

                        # обработка пересечения с верхом - левом персонажа
                        if collide_top_left:
                            print('t_l')
                            # врезается в потолок, стоя на земле
                            if self.state['на земле']:
                                print(collide_top_left)
                                self.y_vel = 0
                                x = max(collide_top_left[0][0], collide_top_left[-1][0])
                                y = max(collide_top_left[0][1], collide_top_left[-1][1])
                                self.rect = self.rect.move(x - self.rect.x + 1,
                                                           (y - self.rect.y))
                            # врезается в потолок, в воздухе
                            elif not platform_rect.collidepoint(self.last_position.left, self.last_position.top):
                                print(collide_top_left)
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
            else:
                self.state['на земле'] = False

            # если не было пересечений
            if self.in_air:
                self.state['на земле'] = False

            # упал - умер - возродился
            if self.rect.y > HEIGHT:  # HEIGHT - берется из файла mainhero.py or self.hp == 0
                self.kill()
                MainHero(self.group, self.platform_sprite_group)
                self.hp = 10


            # запоминаем старую позицию
            self.last_position = self.position

            #############################################



# добавление героя в спрайты
MainHero(all_sprites, platform_sprites)

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
