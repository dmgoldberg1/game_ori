# pygame
import pygame
# БД
import sqlite3
import time
# классы-работники
from platform import Platform, PlatformSlippery, PlatformFire, PlatformMove
from mainhero import MainHero
from utilities import Background, sprite_distance
from npc import NPC, Enemy
from data import timer_npc
# import pygame_ai as pai
from camera import Camera


# рабочие классы/функции
########################################################################################################################
# кнопка
class Button(pygame.sprite.Sprite):
    def __init__(self, group, coords, size, description, linked_page=False):
        super().__init__(group)

        # цвет всех кнопок (можно менять)
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color("blue"))

        # текст (можно менять настройки)
        f1 = pygame.font.SysFont('arial', 36)
        text1 = f1.render(description, True, (255, 0, 0))
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
                global active_sprites
                active_sprites = self.linked_page
            else:
                global running
                running = False

        elif args and args[0].type == pygame.KEYDOWN:
            if args[0].key == 27:
                if self.linked_page:
                    active_sprites = self.linked_page
                else:
                    running = False


# вставил кноки в main, потому что привязка к running и active_sprites
# неудобна через импорт, простите


# ПОКА НЕ СВЯЗАНО С БД
class KeyRegister(pygame.sprite.Sprite):
    def __init__(self, group, coords, db_link):
        super().__init__(group)
        self.size = [50, 50]
        self.db_link = db_link

        self.image = pygame.Surface(self.size)
        self.active = False
        self.draw((0, 255, 0))

        # координаты
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def update(self, *args):
        # реакция на клик
        clicked = args and self.rect.collidepoint(pygame.mouse.get_pos())
        if clicked and args[0].type == pygame.MOUSEBUTTONDOWN:
            self.active = True
            self.draw((0, 123, 0))
            print(self.rect)

        elif clicked and args[0].type == pygame.KEYDOWN and self.active:
            self.active = False
            self.db_link = args[0].unicode

            self.draw((0, 255, 0))

    # отрисовка линии
    def draw(self, color):
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, color, [0, 0, 50, 50], 5)
        f1 = pygame.font.SysFont('arial', 36)
        text1 = f1.render(self.db_link, True, (255, 0, 0))
        self.image.blit(text1, ((self.size[0] - text1.get_width()) // 2, (self.size[1] - text1.get_height()) // 2))


class Label(pygame.sprite.Sprite):
    def __init__(self, group, coords, font, description, font_size=36):
        super().__init__(group)

        f1 = pygame.font.SysFont(font, font_size)
        text1 = f1.render(description, True, (255, 0, 0))

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


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


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
# меню
menu = pygame.sprite.Group()
settings = pygame.sprite.Group()
about = pygame.sprite.Group()

# загружаем кнопками:
# настройки
Button(settings, [0, 0], [40, 40], '←', menu)

Label(settings, [WIDTH // 2 - 320, 150], 'arial', 'Прыжок')
KeyRegister(settings, [WIDTH // 2 - 200, 150], 'w')

Label(settings, [WIDTH // 2 - 320, 210], 'arial', 'Влево')
KeyRegister(settings, [WIDTH // 2 - 200, 210], 'a')

Label(settings, [WIDTH // 2 - 320, 270], 'arial', 'Crouch')
KeyRegister(settings, [WIDTH // 2 - 200, 270], 's')

Label(settings, [WIDTH // 2 - 320, 330], 'arial', 'Вправо')
KeyRegister(settings, [WIDTH // 2 - 200, 330], 'd')
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
Button(all_sprites, [0, 0], [40, 40], '←', menu)

# активное окно
active_sprites = menu
# gravity_entities = []
# drag = pai.steering.kinematic.Drag(15)
# герой, уровень

main_hero = MainHero(all_sprites, platform_sprites, (200, 100))
enemy = Enemy(all_sprites, (400, 100))

npc = NPC(all_sprites, (500, 100))
# enemy = Enemy(pos = (WIGHT//6, HEIGHT//2))
# gravity_entities.append(enemy)
# enemy.ai = pai.steering.kinematic.Seek(enemy, main_hero)
tick = clock.tick(60)/1000
generate_level(load_level('map.txt'))
npc_visited = False

# камера
camera = Camera()

# симуляция
########################################################################################################################

# запуск симуляции
if __name__ == '__main__':
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # отрисовка спрайтов
            active_sprites.update(event)
        # зарисовка и загрузочный апдейт
        screen.fill((255, 255, 255))

        # фон (на else можно поменять фон меню)
        if active_sprites == all_sprites:
            screen.blit(BackGround.image, BackGround.rect)
        else:
            pass
        if sprite_distance(npc.rect, main_hero.rect) and not npc_visited:
            # print('amogus')
            starttime = pygame.time.get_ticks()
            timer_npc[0] = False
            npc_visited = True
            my_font = pygame.font.SysFont('Comic Sans MS', 30)
            text_surface = my_font.render('Ты встретил деда!', True, (0, 0, 0))
            amogus = 1

        try:
            # print(pygame.time.get_ticks() - starttime)
            if pygame.time.get_ticks() - starttime >= 5000:
                amogus = 0
                timer_npc[0] = True
        except:
            pass
        try:
            if amogus == 1:
                screen.blit(text_surface, (430, 50))
        except:
            pass

        active_sprites.update()
        # camera.update(main_hero)
        # # обновляем положение всех спрайтов
        # for sprite in all_sprites:
        #     camera.apply(sprite)
        # enemy.update(tick)
        # for gentity in gravity_entities:
        #     if gentity.rect.bottom > HEIGHT:
        #         gentity.rect.bottom = HEIGHT
        # enemy.steer(drag.get_steering(enemy), tick)
        active_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
