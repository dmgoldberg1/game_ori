# pygame
import os
# БД
import sqlite3

import pygame

# import pygame_ai as pai
from camera import Camera
from data import timer_npc
from mainhero import MainHero
from npc import NPC, EnemyMelee, EnemyRangeFly
# import pygame_ai as pai
# классы-работники
from platform import Platform, PlatformSlippery, PlatformFire
from utilities import Background, sprite_distance


# рабочие классы/функции
########################################################################################################################

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
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):

            # сделал такую проверку на выход из игры
            if self.linked_page:
                active_sprites = self.linked_page
            else:
                running = False

        elif args and args[0].type == pygame.KEYDOWN:
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
        result = cur.execute("""SELECT nums, key FROM binds WHERE name = ?""", (self.db_link,)).fetchall()
        print(result)
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


# загрузка уровней
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# прорисовка уровней
def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                continue
            elif level[y][x] == '-':
                Platform(all_sprites, platform_sprites, (x, y))
            elif level[y][x] == '(':
                PlatformSlippery(all_sprites, platform_sprites, (x, y))
            elif level[y][x] == '/':
                PlatformFire(all_sprites, platform_sprites, (x, y))
            elif level[y][x] == '_':
                a = Platform(all_sprites, platform_sprites, (x, y))
                print((a.rect.x, a.rect.y))
                enemy1 = EnemyMelee(all_sprites, enemy_sprites, platform_sprites, a)


# расстановка спрайтов
########################################################################################################################

# настройки окна
pygame.init()
size = WIDTH, HEIGHT = 1000, 600
FPS = 30
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

BackGround = Background('forest.jpg', [0, 0])

# заготовки групп спрайтов
# игра
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()
main_hero_sprite = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()

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
Button(menu, [WIDTH // 2 - 200, 250], [350, 70], 'Обучение', all_sprites)
Button(menu, [WIDTH // 2 - 200, 350], [350, 70], 'Настройки', settings)
Button(menu, [WIDTH // 2 - 200, 450], [350, 70], 'Об игре', about)
Button(menu, [0, 0], [40, 40], '←')
# описание игры
# НЕ СДЕЛАНО!!!
Button(about, [0, 0], [40, 40], '←', menu)
Label(about, [60, 10], 'arial', 'ВСТАВИТЬ ОПИСАНИЕ (ctrl+c, ctrl+v из презентации) :)', font_size=30)
# игру
button_in_game = Button(all_sprites, [0, 0], [40, 40], '←', menu)

# активное окно
active_sprites = menu
# gravity_entities = []
# drag = pai.steering.kinematic.Drag(15)
# герой, уровень

main_hero = MainHero(all_sprites, platform_sprites)
enemy_range_fly = EnemyRangeFly(all_sprites, platform_sprites, (200, 100))

npc = NPC(all_sprites, (500, 100), 'Ты встретил деда!')
tick = clock.tick(60) / 1000
generate_level(load_level('map.txt'))
npc_visited = False

# камера
camera = Camera(WIDTH, HEIGHT, main_hero)

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
            if event.type == pygame.QUIT:
                running = False

            # карта (игра замерзает)
            if event.type == pygame.KEYDOWN and event.key == main_hero.get_from_db('Карта'):
                size = ((2000, 1000) if size != (2000, 1000) else (1000, 600))
                main_hero.pause = True if not main_hero.pause else False
                for i in enemy_sprites:
                    i.pause = True if not i.pause else False
                enemy_range_fly.pause = True if not enemy_range_fly.pause else False
                pygame.display.set_mode(size)
                os.environ['Sp_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)

            # обновление спрайтов
            active_sprites.update(event)

        # начало отрисовки нового экрана
        screen.fill((255, 255, 255))

        # фон (на else можно поменять фон меню)
        if active_sprites == all_sprites:
            screen.blit(BackGround.image, BackGround.rect)
        else:
            pass

        if sprite_distance(npc.rect, main_hero.rect, 130) and not npc.npc_visited:
            # print('amogus')
            starttime = pygame.time.get_ticks()
            timer_npc[0] = False

            npc.npc_visited = True
            npc.npc_visit = True
            npc.npc_time_visit = pygame.time.get_ticks()
            amogus = 1

        # если время встречи пошло
        if npc.npc_time_visit:

            # если время посещения превосходит 5 сек
            if pygame.time.get_ticks() - npc.npc_time_visit >= 5000:
                npc.npc_visit = False
                npc.npc_time_visit = 0
                timer_npc[0] = True

            # если персонаж сейчас посещает нпс
            if npc.npc_visit:
                screen.blit(npc.text_surface, (430, 50))

        for enemy in enemy_sprites:
            if sprite_distance(main_hero.rect, enemy.rect, 80) and not main_hero.hit:
                main_hero.hp -= 1
                main_hero.hit = True
                main_hero.hit_timer = pygame.time.get_ticks()
            if main_hero.hit:
                if pygame.time.get_ticks() - main_hero.hit_timer >= 1000:
                    main_hero.hit = False
                    main_hero.hit_timer = 0
            print(sprite_distance(main_hero.rect, enemy.rect, 80))
            print(main_hero.hp)

        active_sprites.update()

        # если экран игры
        if active_sprites == all_sprites:

            # изменяем ракурс камеры
            camera.update(main_hero)

            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                if sprite != button_in_game:
                    camera.apply(sprite)
            main_hero.last_position = main_hero.rect
            main_hero.position = main_hero.rect

        active_sprites.draw(screen)
        pygame.display.flip()

    # сохраняем позицию игрока
    con = sqlite3.connect(os.path.join('data', 'storage.db'))
    cur = con.cursor()

    result = cur.execute("""UPDATE saved_coordinates SET x = ? WHERE tag = ?""",
                         (main_hero.rect.x, 'герой')).fetchall()
    result = cur.execute("""UPDATE saved_coordinates SET y = ? WHERE tag = ?""",
                         (main_hero.rect.y, 'герой')).fetchall()

    con.commit()
    con.close()

    # закрываем окно
    pygame.quit()
