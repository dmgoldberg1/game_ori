# pygame
import pygame

# классы-работники
from Platform import Platform
from mainhero import MainHero
from utilities import Background


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


class InputBox(pygame.sprite.Sprite):
    def __init__(self, group, x, y, w, h, text=''):
        super().__init__(group)
        self.f = pygame.font.SysFont('arial', 36)
        self.image = pygame.Surface([w, h])
        self.image.fill((0, 0, 0))
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = self.f.render(text, True, (255, 0, 0))
        self.active = False

    def update(self, *evento):
        if evento:
            event = evento[0]
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        print(self.text)
                        self.text = ''
                    else:
                        self.text = event.unicode

                    self.txt_surface = self.f.render(self.text, True, (255, 0, 0))


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
Button(settings, [0, 0], [40, 40], '->', menu)
InputBox(settings, 100, 100, 40, 40)
# меню
Button(menu, [WIGHT // 2 - 200, 150], [350, 70], 'Играть', all_sprites)
Button(menu, [WIGHT // 2 - 200, 250], [350, 70], 'Настройки', settings)
Button(menu, [0, 0], [40, 40], '->')
# игру
Button(all_sprites, [0, 0], [40, 40], '->', menu)

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
