# pygame
import os
# БД
import sqlite3

import pygame

# import pygame_ai as pai
from camera import Camera
from data import timer_npc
from mainhero import MainHero
from npc import NPC, EnemyMelee, EnemyRangeFly, Bullet, Boss
from nullobject import Null_Object
# import pygame_ai as pai
# классы-работники
from platform import Platform, PlatformSlippery, PlatformFire, PlatformVertical
from utilities import Background, sprite_distance, load_image

# музыка
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.music.load('data\\music\\Мощная Эпическая Музыка _ The BEST Epic Music (256  kbps).mp3')

music_play = False
pygame.mixer.music.play(-1)
# pygame.mixer.music.stop()



# рабочие классы/функции
########################################################################################################################

class Hp_status(pygame.sprite.Sprite):
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = load_image("animation\\hp_status.png", colorkey=(255, 255, 255))
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.image = self.image.convert()
        # self.image.set_colorkey(-1, RLEACCEL)
        self.image.set_alpha(50)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)


# кнопка
class Button(pygame.sprite.Sprite):
    def __init__(self, group, coords, size, description, linked_page=False):
        super().__init__(group)

        # цвет всех кнопок (можно менять)
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color("orange"))

        pygame.draw.rect(self.image, pygame.Color("brown"),
                         [0, 0] + size, 5)

        # текст (можно менять настройки)
        f1 = pygame.font.SysFont('arial', 36)
        text1 = f1.render(description, True, pygame.Color("brown"))
        self.image.blit(text1, ((size[0] - text1.get_width()) // 2, (size[1] - text1.get_height()) // 2))

        # координаты
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

        # переход на другую страницу
        self.linked_page = linked_page

    def update(self, *args):
        global active_sprites
        global running
        # реакция на клик
        if len(args) == 1 and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):

            # сделал такую проверку на выход из игры
            if self.linked_page:
                active_sprites = self.linked_page
            else:
                running = False

        elif len(args) == 1 and args[0].type == pygame.KEYDOWN:
            if args[0].key == 27:
                if self.linked_page:
                    active_sprites = self.linked_page
                else:
                    running = False


# ввод биндов
class KeyRegister(pygame.sprite.Sprite):
    def __init__(self, group, coords, db_link):
        super().__init__(group)
        self.size = [50, 50]
        self.db_link = db_link

        self.nums = 0
        self.key = 0
        self.pick_from_db()

        self.image = pygame.Surface(self.size)
        self.active = False
        self.draw(pygame.Color("orange"))

        # координаты
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def update(self, *args):
        # реакция на клик
        clicked = args and self.rect.collidepoint(pygame.mouse.get_pos())
        if clicked and args[0].type == pygame.MOUSEBUTTONDOWN:
            self.active = True
            self.draw(pygame.Color("lime"))

        elif clicked and args[0].type == pygame.KEYDOWN and self.active:
            self.nums = args[0].key
            self.key = args[0].unicode

            con = sqlite3.connect(os.path.join('data', 'storage.db'))
            cur = con.cursor()

            result = cur.execute("""UPDATE binds SET key = ? WHERE name = ?""",
                                 (self.key, self.db_link)).fetchall()
            result = cur.execute("""UPDATE binds SET nums = ? WHERE name = ?""",
                                 (self.nums, self.db_link)).fetchall()

            con.commit()
            con.close()

            self.active = False
            self.draw(pygame.Color("orange"))

    def pick_from_db(self):
        con = sqlite3.connect(os.path.join('data', 'storage.db'))
        cur = con.cursor()
        # print(self.db_link)
        result = cur.execute("""SELECT nums, key FROM binds WHERE name = ?""", (self.db_link,)).fetchall()
        # print(result)
        self.nums, self.key = result[0]
        con.close()

    # отрисовка линии
    def draw(self, color):
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, color, [0, 0, 50, 50], 5)
        f1 = pygame.font.SysFont('arial', 36)
        text1 = f1.render(self.key, True, (255, 0, 0))
        self.image.blit(text1, ((self.size[0] - text1.get_width()) // 2, (self.size[1] - text1.get_height()) // 2))


# лейблы
class Label(pygame.sprite.Sprite):
    def __init__(self, group, coords, font, description, font_size=36):
        super().__init__(group)

        f1 = pygame.font.SysFont(font, font_size)
        text1 = f1.render(description, True, pygame.Color("brown"))

        self.size = [text1.get_width(), text1.get_height()]
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 255))

        self.image.blit(text1, (0, 0))

        # координаты
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def update(self, *args):
        pass


class LoadCover(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

        self.dots = 0
        f1 = pygame.font.SysFont('arial', 60)
        text1 = f1.render('Загрузка...' + ('.' * self.dots), True, pygame.Color("white"))

        self.size = [1000, 600]
        self.image = pygame.Surface(self.size)
        self.image.fill((0, 0, 0))

        self.image.blit(text1, (600 - text1.get_width(), 300 - text1.get_height()))

        # координаты
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self, *args):
        pass


# загрузка уровней
def load_level(filename, count):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    c = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    return c, len(c[0])


# прорисовка уровней
def generate_level(l, number):
    global npc_ded
    level, count = l
    x, y = None, None
    if number == 0:
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    continue
                elif level[y][x] == '-':
                    Platform(all_sprites, platform_sprites, (x, y))
                elif level[y][x] == '|':
                    PlatformVertical(all_sprites, platform_sprites, (x, y))
                elif level[y][x] == '(':
                    PlatformSlippery(all_sprites, platform_sprites, (x, y))
                elif level[y][x] == '/':
                    PlatformFire(all_sprites, platform_sprites, (x, y))
                elif level[y][x] == '_':
                    a = Platform(all_sprites, platform_sprites, (x, y))
                    print((a.rect.x, a.rect.y))
                    enemy1 = EnemyMelee(all_sprites, enemy_sprites, platform_sprites, a, main_hero)
                elif level[y][x] == '$':
                    a = Platform(all_sprites, platform_sprites, (x, y))
                    print((a.rect.x, a.rect.y))
                    npc_ded = NPC(all_sprites, (a.rect.x + 10, a.rect.y - 40), 'Ты встретил деда!')
                elif level[y][x] == '+':
                    a = Platform(all_sprites, platform_sprites, (x, y))
                    print((a.rect.x, a.rect.y))
                    enemy1 = EnemyRangeFly(all_sprites, enemy_sprites, platform_sprites, a, main_hero)
    elif number == 1:
        for y in range(len(level)):
            for x in range(len(level[y])):
                x_1 = x + count
                if level[y][x] == '.':
                    continue
                elif level[y][x] == '-':
                    Platform(all_sprites, platform_sprites1, (x_1, y))
                elif level[y][x] == '|':
                    PlatformVertical(all_sprites, platform_sprites1, (x_1, y))
                elif level[y][x] == '(':
                    PlatformSlippery(all_sprites, platform_sprites1, (x_1, y))
                elif level[y][x] == '/':
                    PlatformFire(all_sprites, platform_sprites1, (x_1, y))
                elif level[y][x] == '_':
                    a = Platform(all_sprites, platform_sprites1, (x_1, y))
                    print((a.rect.x, a.rect.y))
                    enemy1 = EnemyMelee(all_sprites, enemy_sprites, platform_sprites1, a, main_hero)
    elif number == 2:
        count *= 2
        for y in range(len(level)):
            for x in range(len(level[y])):
                x_1 = x + count
                if level[y][x] == '.':
                    continue
                elif level[y][x] == '-':
                    Platform(all_sprites, platform_sprites2, (x_1, y))
                elif level[y][x] == '|':
                    PlatformVertical(all_sprites, platform_sprites2, (x_1, y))
                elif level[y][x] == '(':
                    PlatformSlippery(all_sprites, platform_sprites2, (x_1, y))
                elif level[y][x] == '/':
                    PlatformFire(all_sprites, platform_sprites2, (x_1, y))
                elif level[y][x] == '_':
                    a = Platform(all_sprites, platform_sprites2, (x_1, y))
                    print((a.rect.x, a.rect.y))
                    enemy1 = EnemyMelee(all_sprites, enemy_sprites, platform_sprites2, a, main_hero)

    elif number == 3:
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    continue
                elif level[y][x] == '-':
                    Platform(education_sprites, education_platform_sprites, (x, y))
                elif level[y][x] == '|':
                    PlatformVertical(education_sprites, education_platform_sprites, (x, y))
                elif level[y][x] == '(':
                    PlatformSlippery(education_sprites, education_platform_sprites, (x, y))
                elif level[y][x] == '/':
                    PlatformFire(education_sprites, education_platform_sprites, (x, y))
                elif level[y][x] == '_':
                    a = Platform(education_sprites, education_platform_sprites, (x, y))
                    print((a.rect.x, a.rect.y))
                    enemy1 = EnemyMelee(education_sprites, education_enemy_sprites,
                                        education_platform_sprites, a, education_main_hero)

    return count * 100


# расстановка спрайтов
########################################################################################################################

# настройки окна
pygame.init()
size = WIDTH, HEIGHT = 1000, 600
FPS = 30
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

allow = True
BackGround = Background('forest.jpg', [0, 0])

# заготовки групп спрайтов

# игра
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()
platform_sprites1 = pygame.sprite.Group()
platform_sprites2 = pygame.sprite.Group()
main_hero_sprite = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
hp_status_group = pygame.sprite.Group()

education_sprites = pygame.sprite.Group()
education_platform_sprites = pygame.sprite.Group()
education_enemy_sprites = pygame.sprite.Group()

# меню
about = pygame.sprite.Group()
menu = pygame.sprite.Group()
settings = pygame.sprite.Group()

# загружаем кнопками:
# настройки
Button(settings, [0, 0], [40, 40], '←', menu)

Label(settings, [WIDTH // 2 - 320, 150], 'arial', 'Прыжок')
KeyRegister(settings, [WIDTH // 2 - 200, 150], 'Прыжок')

Label(settings, [WIDTH // 2 - 320, 210], 'arial', 'Влево')
KeyRegister(settings, [WIDTH // 2 - 200, 210], 'Влево')

Label(settings, [WIDTH // 2 - 320, 270], 'arial', 'Карта')
KeyRegister(settings, [WIDTH // 2 - 200, 270], 'Карта')

Label(settings, [WIDTH // 2 - 320, 330], 'arial', 'Вправо')
KeyRegister(settings, [WIDTH // 2 - 200, 330], 'Вправо')
# меню
Label(menu, [WIDTH // 2 - 380, 50], 'Comic Sans MS', 'ЗАБАВНЫЕ ПРИКЛЮЧЕНИЯ', font_size=50)

Button(menu, [WIDTH // 2 - 200, 150], [350, 70], 'Играть', all_sprites)
Button(menu, [WIDTH // 2 - 200, 250], [350, 70], 'Обучение', education_sprites)
Button(menu, [WIDTH // 2 - 200, 350], [350, 70], 'Настройки', settings)
Button(menu, [WIDTH // 2 - 200, 450], [350, 70], 'Об игре', about)
Button(menu, [0, 0], [40, 40], '←')
# описание игры
# НЕ СДЕЛАНО!!!
Button(about, [0, 0], [40, 40], '←', menu)
Label(about, [60, 10], 'arial', 'ВСТАВИТЬ ОПИСАНИЕ (ctrl+c, ctrl+v из презентации) :)', font_size=30)
# игру
button_in_game = Button(all_sprites, [0, 0], [40, 40], '←', menu)
ed_button = Button(education_sprites, [0, 0], [40, 40], '←', menu)

# активное окно
active_sprites = menu
# gravity_entities = []
# drag = pai.steering.kinematic.Drag(15)

# герой, уровень
hp_status = Hp_status(hp_status_group)
null_object = Null_Object(all_sprites)
education_null_object = Null_Object(education_sprites)

load_cover = LoadCover(all_sprites)
main_hero = MainHero(all_sprites, [platform_sprites], null_object)
education_main_hero = MainHero(education_sprites, [education_platform_sprites], education_null_object)
all_sprites.remove(load_cover)

# npc = NPC(all_sprites, (2300, 100), 'Ты встретил деда!')
tick = clock.tick(60) / 1000

board1 = generate_level(load_level('map.txt', 0), 0)
board2 = generate_level(load_level('map2.txt', 1), 1) * 2
board3 = generate_level(load_level('map3.txt', 2), 2) * 2
education_board = generate_level(load_level('map_education.txt', 0), 3)
print(board1, board2, board3)

npc_visited = False
fire = True

bullets = []
pause = True
test = True
check = 1
# камера
camera = Camera(WIDTH, HEIGHT, main_hero)
education_camera = Camera(WIDTH, HEIGHT, education_main_hero)

# симуляция
########################################################################################################################
# запуск симуляции
if __name__ == '__main__':
    while running:
        # запускаем время
        clock.tick(FPS)

        # обработка событий - отклик
        for event in pygame.event.get():
            # закрытие окна
            if event.type == pygame.QUIT and load_cover not in all_sprites:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print('MOUSE', pos)
                if 306 <= pos[0] <= 643:
                    pause = False
                if 5 <= pos[0] <= 35:
                    pause = True

            # карта (игра замерзает)
            if event.type == pygame.KEYDOWN and event.key == main_hero.get_from_db('Карта'):
                size = ((2000, 1000) if size != (2000, 1000) else (1000, 600))
                main_hero.pause = True if not main_hero.pause else False
                for i in enemy_sprites:
                    i.pause = True if not i.pause else False

                pygame.display.set_mode(size)
                os.environ['Sp_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)

            # обновление спрайтов
            active_sprites.update(event)

        # начало отрисовки нового экрана
        screen.fill((255, 255, 255))

        # обрабатываем границы
        if board1 - 200 <= main_hero.rect.x - null_object.rect.x <= board1 + 200 and len(
                main_hero.platform_sprite_group) == 1:
            main_hero.platform_sprite_group.append(platform_sprites1)
            print('aaaaaaaaa')
        elif board2 - 200 <= main_hero.rect.x - null_object.rect.x <= board2 + 200 and len(
                main_hero.platform_sprite_group) == 2:
            main_hero.platform_sprite_group.append(platform_sprites2)  # .append(platform_sprites2)
            print('aaaaaaaaa')
        elif board1 + 200 <= main_hero.rect.x - null_object.rect.x <= board2 - 200 and len(
                main_hero.platform_sprite_group) == 2:
            main_hero.platform_sprite_group = [platform_sprites1]
            print('bbbbbbbbbbbb')
        elif board2 + 200 <= main_hero.rect.x - null_object.rect.x <= board3 - 200 and len(
                main_hero.platform_sprite_group) == 2:
            main_hero.platform_sprite_group = main_hero.platform_sprite_group[1:]
            print('bbbbbbbbbbbb')

        # фон (на else можно поменять фон меню)
        if active_sprites == all_sprites:
            screen.blit(BackGround.image, BackGround.rect)
        else:
            pass

        if sprite_distance(npc_ded.rect, main_hero.rect, 130) and not npc_ded.npc_visited and main_hero.allow:
            # print('amogus')
            starttime = pygame.time.get_ticks()
            timer_npc[0] = False

            npc_ded.npc_visited = True
            npc_ded.npc_visit = True
            npc_ded.npc_time_visit = pygame.time.get_ticks()
            amogus = 1

        # если время встречи пошло
        if npc_ded.npc_time_visit:

            # если время посещения превосходит 5 сек
            if pygame.time.get_ticks() - npc_ded.npc_time_visit >= 5000:
                npc_ded.npc_visit = False
                npc_ded.npc_time_visit = 0
                timer_npc[0] = True

            # если персонаж сейчас посещает нпс
            if npc_ded.npc_visit:
                screen.blit(npc_ded.text_surface, (430, 50))

        # работа с координатами
        if not main_hero.allow and active_sprites == all_sprites:
            all_sprites.update(null_object.rect.x, null_object.rect.y)

            # натянуть 'загрузку'
            if load_cover not in all_sprites:
                load_cover = LoadCover(all_sprites)
        else:
            active_sprites.update()

            # снять 'загрузку'
            if load_cover in all_sprites:
                all_sprites.remove(load_cover)

        for enemy in enemy_sprites:
            if not pause:
                if type(enemy) == Boss or type(enemy) == EnemyRangeFly:
                    if fire and sprite_distance(main_hero.rect, enemy.rect, 500):
                        bullet = Bullet(enemy.rect.x, enemy.rect.y, main_hero.position.x,
                                        main_hero.position.y,
                                        all_sprites, platform_sprites)
                        bullets.append(bullet)

                        bullet.kill()
                        fire = False
                        bullet.fire_timer = pygame.time.get_ticks()

                    for bullet in bullets[:]:
                        bullet.update()
                        if main_hero.rect.collidepoint(bullet.pos):
                            main_hero.hp -= 1
                            bullets.remove(bullet)
                        if not screen.get_rect().collidepoint(bullet.pos):
                            bullets.remove(bullet)
                        # print(f'''Герой: {main_hero.rect.x}, Пуля: {int(bullet.pos[0] // 1)}''')

                    for bullet in bullets:
                        bullet.draw(screen)

                        # print(bullets)
                        # print(sprite_distance(main_hero.rect, bullet.rect, 150))

                    if not fire and pygame.time.get_ticks() - bullet.fire_timer >= 5000:
                        fire = True
                        bullet.fire_timer = 0
            # print(sprite_distance(main_hero.rect, enemy.rect, 80))
            # print(main_hero.hp)

            # Стрельба летающих нпс

        active_sprites.update()

        # если экран игры
        if active_sprites == all_sprites:

            # изменяем ракурс камеры
            camera.update(main_hero)

            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                # print(type(sprite) if type(sprite) != Platform else 0)
                if sprite != button_in_game and sprite != load_cover:
                    camera.apply(sprite)
            main_hero.last_position = main_hero.rect
            main_hero.position = main_hero.rect
            # print('dddddddddddddddddd')



        elif active_sprites == education_sprites:
            education_camera.update(education_main_hero)
            # обновляем положение всех спрайтов
            for sprite in education_sprites:
                if sprite != ed_button:
                    education_camera.apply(sprite)
            education_main_hero.last_position = education_main_hero.rect
            education_main_hero.position = education_main_hero.rect

        active_sprites.draw(screen)
        if active_sprites == all_sprites:
            hp_status.image.set_alpha((10 - main_hero.hp) * 10)
            hp_status_group.draw(screen)
        pygame.display.flip()

    # сохраняем позицию игрока
    con = sqlite3.connect(os.path.join('data', 'storage.db'))
    cur = con.cursor()

    result = cur.execute("""UPDATE saved_coordinates SET x = ? WHERE tag = ?""",
                         (main_hero.rect.x - null_object.rect.x, 'герой')).fetchall()
    result = cur.execute("""UPDATE saved_coordinates SET y = ? WHERE tag = ?""",
                         (main_hero.rect.y - null_object.rect.y, 'герой')).fetchall()

    print(main_hero.rect.x - null_object.rect.x, main_hero.rect.y - null_object.rect.y)

    con.commit()
    con.close()

    # закрываем окно
    pygame.quit()
