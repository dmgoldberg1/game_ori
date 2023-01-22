# импорты:
# работа с БД
import os
import sqlite3
# структура игры
import pygame
# камера
from camera import Camera
# неиграбельные персонажи
from data import timer_npc
from npc import NPC, EnemyMelee, EnemyRangeFly, Bullet, Boss
# главный герой
from mainhero import MainHero
from nullobject import Null_Object
# платформы
from platform1 import Platform, PlatformSlippery, PlatformFire, PlatformVertical
# вспомогательные функции
from utilities import Background, sprite_distance, load_image, activate_skill, skill_check

# музыка
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.music.load('data\\music\\music.mp3')

music_play = False
pygame.mixer.music.play(-1)

pygame.mixer.music.set_volume(0.5)


# рабочие классы/функции
########################################################################################################################

# кровавый ободок
class Hp_status(pygame.sprite.Sprite):
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = load_image("animation\\hp_status.png", colorkey=(255, 255, 255))
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.image = self.image.convert()
        self.image.set_alpha(50)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)


# кнопка
class Button(pygame.sprite.Sprite):
    def __init__(self, group, coords, size, description, linked_page=False):
        super().__init__(group)

        # цвет всех кнопок
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color("orange"))

        pygame.draw.rect(self.image, pygame.Color("brown"),
                         [0, 0] + size, 5)

        # текст
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

        # нажатие esc = нажатие кнопки назад
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
            self.draw(pygame.Color("brown"))

        # запись нового значения
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

    # достаёт уже установленную кнопку
    def pick_from_db(self):
        con = sqlite3.connect(os.path.join('data', 'storage.db'))
        cur = con.cursor()
        result = cur.execute("""SELECT nums, key FROM binds WHERE name = ?""", (self.db_link,)).fetchall()
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

# экран "Загрузка"
class LoadCover(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

        self.dots = 0
        f1 = pygame.font.SysFont('arial', 60)
        text1 = f1.render('Загрузка...' + ('.' * self.dots), True, pygame.Color("white"))

        self.size = [WIDTH, HEIGHT]
        self.image = pygame.Surface(self.size)
        self.image.fill((0, 0, 0))

        self.image.blit(text1, ((WIDTH - text1.get_width()) // 2, (HEIGHT - text1.get_height()) // 2))

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
    # 1-ый уровень
    if number == 0:
        for y in range(len(level)):
            for x in range(len(level[y])):
                # устанавливаем на место символов соотвествующие объекты
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
                    enemy1 = EnemyMelee(all_sprites, all_enemy_sprites, enemy_sprites, platform_sprites, a, main_hero)
                elif level[y][x] == '$':
                    a = Platform(all_sprites, platform_sprites, (x, y))
                    npc_ded = NPC(all_sprites, (a.rect.x + 10, a.rect.y - 40),
                                  'Ты встретил деда! Теперь у тебя есть способность Двойной прыжок')
                elif level[y][x] == '+':
                    a = Platform(all_sprites, platform_sprites, (x, y))
                    enemy1 = EnemyRangeFly(all_sprites, all_enemy_sprites, enemy_sprites, platform_sprites, a,
                                           main_hero)
                elif level[y][x] == '^':
                    a = Platform(all_sprites, platform_sprites, (x, y))

    # 2-ой уровень
    elif number == 1:
        for y in range(len(level)):
            for x in range(len(level[y])):
                x_1 = x + count
                # устанавливаем на место символов соотвествующие объекты
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
                    enemy1 = EnemyMelee(all_sprites, all_enemy_sprites, enemy_sprites, platform_sprites1, a, main_hero)
                elif level[y][x] == '$':
                    a = Platform(all_sprites, platform_sprites1, (x_1, y))
                    npc_ded = NPC(all_sprites, (a.rect.x + 10, a.rect.y - 40), 'Ты встретил деда!')
                elif level[y][x] == '+':
                    a = Platform(all_sprites, platform_sprites1, (x_1, y))
                    enemy1 = EnemyRangeFly(all_sprites, all_enemy_sprites, enemy_sprites, platform_sprites1, a,
                                           main_hero)
                elif level[y][x] == '^':
                    a = Platform(all_sprites, platform_sprites1, (x_1, y))

    # 3-ий уровень
    elif number == 2:
        count *= 2
        for y in range(len(level)):
            for x in range(len(level[y])):
                x_1 = x + count
                # устанавливаем на место символов соотвествующие объекты
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
                    enemy1 = EnemyMelee(all_sprites, all_enemy_sprites, enemy_sprites, platform_sprites2, a, main_hero)
                elif level[y][x] == '$':
                    a = Platform(all_sprites, platform_sprites2, (x_1, y))
                    npc_ded = NPC(all_sprites, (a.rect.x + 10, a.rect.y - 40), 'Ты встретил деда!')
                elif level[y][x] == '+':
                    a = Platform(all_sprites, platform_sprites2, (x_1, y))
                    enemy1 = EnemyRangeFly(all_sprites, all_enemy_sprites, enemy_sprites, platform_sprites2, a,
                                           main_hero)
                elif level[y][x] == '^':
                    a = Platform(all_sprites, platform_sprites2, (x_1, y))
                    enemy1 = Boss(all_sprites, all_enemy_sprites, boss_sprites, platform_sprites2, a, main_hero)

    # обучение
    elif number == 3:
        for y in range(len(level)):
            for x in range(len(level[y])):
                # устанавливаем на место символов соотвествующие объекты
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
                    enemy1 = EnemyMelee(education_sprites, education_all_enemy_sprites, education_enemy_sprites,
                                        education_platform_sprites, a,
                                        education_main_hero)
                elif level[y][x] == '$':
                    a = Platform(education_sprites, education_platform_sprites, (x, y))
                    npc_ded = NPC(education_sprites, (a.rect.x + 10, a.rect.y - 40), 'Ты встретил деда!')
                elif level[y][x] == '+':
                    a = Platform(education_sprites, education_platform_sprites, (x, y))
                    enemy1 = EnemyRangeFly(education_sprites, education_all_enemy_sprites, education_enemy_sprites,
                                           education_platform_sprites, a,
                                           education_main_hero)

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

BackGround = Background('forest.jpg', [0, 0])
MenuBackGround = Background('menu.jpg', [-80, 0])
WinBackGround = Background('win.jpg', [30, 0])

# заготовки групп спрайтов
# игра
all_sprites = pygame.sprite.Group()
all_enemy_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()
platform_sprites1 = pygame.sprite.Group()
platform_sprites2 = pygame.sprite.Group()
main_hero_sprite = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
hp_status_group = pygame.sprite.Group()
result = pygame.sprite.Group()
total = pygame.sprite.Group()
boss_sprites = pygame.sprite.Group()

# обучение
education_sprites = pygame.sprite.Group()
education_all_enemy_sprites = pygame.sprite.Group()
education_platform_sprites = pygame.sprite.Group()
education_enemy_sprites = pygame.sprite.Group()

# меню
about = pygame.sprite.Group()
menu = pygame.sprite.Group()
settings = pygame.sprite.Group()

# загружаем кнопками:
# смерть
Button(result, [WIDTH // 2 - 200, 250], [350, 70], 'Выйти в меню', menu)
Button(result, [WIDTH // 2 - 200, 350], [350, 70], 'Попробовать снова', all_sprites)
Label(result, [WIDTH // 2 - 260, 30], 'calibri', 'КОНЕЦ ИГРЫ', font_size=90)

# победу
Button(total, [WIDTH // 2 - 200, 150], [350, 70], 'Выйти')
Label(total, [WIDTH // 2 - 220, 30], 'calibri', 'победа', font_size=120)

# настройки
Button(settings, [0, 0], [40, 40], '←', menu)

Label(settings, [WIDTH // 2 - 320, 150], 'arial', 'Прыжок')
KeyRegister(settings, [WIDTH // 2 - 200, 150], 'Прыжок')

Label(settings, [WIDTH // 2 - 320, 210], 'arial', 'Влево')
KeyRegister(settings, [WIDTH // 2 - 200, 210], 'Влево')

Label(settings, [WIDTH // 2 - 320, 270], 'arial', 'Вправо')
KeyRegister(settings, [WIDTH // 2 - 200, 270], 'Вправо')

Label(settings, [WIDTH // 2 - 480, 330], 'arial', 'Заморозка времени')
KeyRegister(settings, [WIDTH // 2 - 200, 330], 'Карта')

# меню
Label(menu, [WIDTH // 2 - 380, 50], 'Comic Sans MS', 'ЗАБАВНЫЕ ПРИКЛЮЧЕНИЯ', font_size=50)

Button(menu, [WIDTH // 2 - 200, 150], [350, 70], 'Играть', all_sprites)
Button(menu, [WIDTH // 2 - 200, 250], [350, 70], 'Обучение', education_sprites)
Button(menu, [WIDTH // 2 - 200, 350], [350, 70], 'Настройки', settings)
Button(menu, [WIDTH // 2 - 200, 450], [350, 70], 'Об игре', about)
Button(menu, [0, 0], [40, 40], '←')

# описание игры
Button(about, [0, 0], [40, 40], '←', menu)
Label(about, [60, 50], 'arial', '"Забавные приключения" - компьютерная игра платформер:)', font_size=30)
Label(about, [60, 100], 'arial', '"Цель  игрока -  победить всех мобов на большой карте!', font_size=30)

# игру
button_in_game = Button(all_sprites, [0, 0], [40, 40], '←', menu)
ed_button = Button(education_sprites, [0, 0], [40, 40], '←', menu)

# активное окно
active_sprites = menu

# герой, уровень
hp_status = Hp_status(hp_status_group)
null_object = Null_Object(all_sprites)
education_null_object = Null_Object(education_sprites)

load_cover = LoadCover(all_sprites)
main_hero = MainHero(all_sprites, [platform_sprites], null_object)
education_main_hero = MainHero(education_sprites, [education_platform_sprites], education_null_object)
all_sprites.remove(load_cover)

tick = clock.tick(60) / 1000

# заносим уровни
board1 = generate_level(load_level('map.txt', 0), 0)
board2 = generate_level(load_level('map2.txt', 1), 1) * 2
board3 = generate_level(load_level('map3.txt', 2), 2) * 2
education_board = generate_level(load_level('map_education.txt', 0), 3)

# статусы
npc_visited = False
fire = True
allow = True
npc_visited = False
fire = True
fire_hero = True
bullets = []
bullets_hero = []
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
                if active_sprites == all_sprites:
                    pause = False
                else:
                    pause = True

            # стрельба игрока
            if event.type == pygame.MOUSEBUTTONDOWN:
                if fire_hero:
                    bullet = Bullet(0, 0, main_hero.position.x,
                                    main_hero.position.y,
                                    all_sprites, platform_sprites, False)
                    bullets_hero.append(bullet)
                    bullet.kill()
                    fire_hero = False
                    bullet.fire_timer_hero = pygame.time.get_ticks()

            # заморозка времени
            if event.type == pygame.KEYDOWN and event.key == main_hero.get_from_db('Карта') and \
                    active_sprites == all_sprites and skill_check('заморозка времени'):
                for i in enemy_sprites:
                    i.pause = True if not i.pause else False

            # обновление спрайтов
            active_sprites.update(event)

        # начало отрисовки нового экрана
        screen.fill((255, 255, 255))

        # обрабатываем границы
        if 0 <= main_hero.rect.x - null_object.rect.x <= board1 - 300:
            main_hero.platform_sprite_group = [platform_sprites]
        elif board1 - 300 <= main_hero.rect.x - null_object.rect.x <= board1 + 300:
            main_hero.platform_sprite_group = [platform_sprites, platform_sprites1]
        elif board1 + 300 <= main_hero.rect.x - null_object.rect.x <= board2 - 300:
            main_hero.platform_sprite_group = [platform_sprites1]
        elif board2 - 300 <= main_hero.rect.x - null_object.rect.x <= board2 + 300:
            main_hero.platform_sprite_group = [platform_sprites1, platform_sprites2]
        elif board2 + 300 <= main_hero.rect.x - null_object.rect.x:
            main_hero.platform_sprite_group = [platform_sprites2]

        # фон
        if active_sprites == all_sprites:
            screen.blit(BackGround.image, BackGround.rect)
        elif active_sprites != total:
            screen.blit(MenuBackGround.image, MenuBackGround.rect)
        else:
            screen.blit(WinBackGround.image, WinBackGround.rect)

        # встреча с дедом
        if sprite_distance(npc_ded.rect, main_hero.rect, 130) and not npc_ded.npc_visited and main_hero.allow:
            starttime = pygame.time.get_ticks()
            timer_npc[0] = False
            main_hero.x_vel = 0
            main_hero.y_vel = 0
            npc_ded.npc_visited = True
            npc_ded.npc_visit = True
            npc_ded.npc_time_visit = pygame.time.get_ticks()
            amogus = 1

        # если время встречи пошло
        if npc_ded.npc_time_visit:

            # если время посещения превосходит 5 сек
            if pygame.time.get_ticks() - npc_ded.npc_time_visit >= 3000:
                npc_ded.npc_visit = False
                npc_ded.npc_time_visit = 0
                timer_npc[0] = True

            # если персонаж сейчас посещает нпс
            if npc_ded.npc_visit:
                screen.blit(npc_ded.text_surface, (30, 40))
                activate_skill('двойной прыжок')

        if not enemy_sprites:
            activate_skill('заморозка времени')

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

        # стрельба врагов
        for enemy in all_enemy_sprites:
            if not pause:
                if type(enemy) == Boss or type(enemy) == EnemyRangeFly:
                    if fire and sprite_distance(main_hero.rect, enemy.rect, 1000):
                        bullet = Bullet(enemy.rect.x, enemy.rect.y, main_hero.position.x,
                                        main_hero.position.y,
                                        all_sprites, platform_sprites, True)
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
                    for bullet in bullets:
                        bullet.draw(screen)

                    if not fire and pygame.time.get_ticks() - bullet.fire_timer >= 4000:
                        fire = True
                        bullet.fire_timer = 0
                for bullet in bullets_hero[:]:
                    if type(enemy) == EnemyRangeFly:
                        if enemy.rect.collidepoint(bullet.pos):
                            enemy.hp -= 1
                            bullets_hero.remove(bullet)
                    if type(enemy) == EnemyMelee:
                        if enemy.rect.collidepoint(bullet.pos):
                            enemy.hp -= 1
                            bullets_hero.remove(bullet)
                    if type(enemy) == Boss:
                        if enemy.rect.collidepoint(bullet.pos):
                            enemy.hp -= 1
                            bullets_hero.remove(bullet)
                if not fire_hero and pygame.time.get_ticks() - bullet.fire_timer_hero >= 2000:
                    fire_hero = True
                    bullet.fire_timer_hero = 0

        # Стрельба летающих нпс
        if not pause:
            for bullet in bullets_hero[:]:
                bullet.update()

                if not screen.get_rect().collidepoint(bullet.pos):
                    bullets_hero.remove(bullet)

            for bullet in bullets_hero:
                bullet.draw(screen)

        # пустой update, чтобы всё двигалось одновременно
        active_sprites.update()

        # если экран игры
        if active_sprites == all_sprites:

            # изменяем ракурс камеры
            camera.update(main_hero)

            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                if sprite != button_in_game and sprite != load_cover:
                    camera.apply(sprite)
            main_hero.last_position = main_hero.rect
            main_hero.position = main_hero.rect

        # если экран обучения
        elif active_sprites == education_sprites:
            education_camera.update(education_main_hero)
            # обновляем положение всех спрайтов
            for sprite in education_sprites:
                if sprite != ed_button:
                    education_camera.apply(sprite)
            education_main_hero.last_position = education_main_hero.rect
            education_main_hero.position = education_main_hero.rect
        
        # отрисовать активное окно
        active_sprites.draw(screen)
        
        # если игра - отрисовываем кровавый ободок
        if active_sprites == all_sprites:
            hp_status.image.set_alpha((10 - main_hero.hp) * 10)
            hp_status_group.draw(screen)
        # если умираем, то запускается окно смерти
        if main_hero.death:
            main_hero.platform_type = None
            main_hero.platform_sprite_group = [platform_sprites]
            temp = Label(result, [WIDTH // 2 - 400, 130], 'calibri',
                         'Потрачено ' + str(pygame.time.get_ticks() // 1000) + ' секунд(ы)', font_size=80)
            active_sprites = result
            main_hero.death = False
        
        # если побеждаем, то запускается окно победы
        if not boss_sprites:
            active_sprites = total
        pygame.display.flip()

    # сохраняем позицию игрока
    con = sqlite3.connect(os.path.join('data', 'storage.db'))
    cur = con.cursor()

    result = cur.execute("""UPDATE saved_coordinates SET x = ? WHERE tag = ?""",
                         (main_hero.rect.x - null_object.rect.x, 'герой')).fetchall()
    result = cur.execute("""UPDATE saved_coordinates SET y = ? WHERE tag = ?""",
                         (main_hero.rect.y - null_object.rect.y, 'герой')).fetchall()

    con.commit()
    con.close()

    # закрываем окно
    pygame.quit()
