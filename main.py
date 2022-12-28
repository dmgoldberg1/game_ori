# pygame
import pygame

# классы-работники
from platform import Platform
from mainhero import MainHero
from utilities import Background


# кнопка
class Button(pygame.sprite.Sprite):
    def __init__(self, group, coords, size, description, offset, linked_page=False):
        super().__init__(group)

        # цвет всех кнопок (можно менять)
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color("blue"))

        # текст (можно менять настройки)
        f1 = pygame.font.SysFont('arial', 36)
        text1 = f1.render(description, True, (255, 0, 0))
        self.image.blit(text1, (size[0] // 2 - offset[0], size[1] // 2 - offset[1]))

        # координаты
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

        # переход на другую страницу
        self.linked_page = linked_page

    def update(self, *args):
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


# вставил кноки в main, потому что привязка к running и active_sprites
# неудобна через импорт, простите


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


########################################################################################################################
# настройки окна
pygame.init()
size = WIGHT, HEIGHT = 1000, 600
FPS = 30
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

BackGround = Background('forest.jpg', [0, 0])

# заготовки групп спрайтов
# игра
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()
# меню
menu = pygame.sprite.Group()
settings = pygame.sprite.Group()

# загружаем кнопками:
# настройки
Button(settings, [0, 0], [40, 40], '->', [15, 20], menu)
# меню
Button(menu, [WIGHT // 2 - 200, 150], [350, 70], 'Играть', [45, 15], all_sprites)
Button(menu, [WIGHT // 2 - 200, 250], [350, 70], 'Настройки', [70, 15], settings)
Button(menu, [0, 0], [40, 40], '->', [15, 20])
# игру
Button(all_sprites, [0, 0], [40, 40], '->', [15, 20], menu)

# активное окно
active_sprites = menu

# герой, уровень
MainHero(all_sprites, platform_sprites, (200, 100))
generate_level(load_level('map.txt'))

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

        active_sprites.update()
        active_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
