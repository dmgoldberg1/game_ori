import pygame
import os
import sys


# загрузка изображений (пока не анимашки)
def load_image(name, colorkey=None):
    # сменить на texture\{папка с анимацией} и потом загружать кадры из папки
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# настройки окна
size = width, height = 500, 500
FPS = 20
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

pygame.init()

# спрайты
all_sprites = pygame.sprite.Group()


# класс героя
class MainHero(pygame.sprite.Sprite):
    # картинка
    image = load_image("temp.png")

    def __init__(self, group):
        super().__init__(group)
        self.state = {'на земле': True,
                      'карабкается': False}
        self.image = MainHero.image
        self.rect = self.image.get_rect()
        self.rect.x = 250
        self.rect.y = 250

        self.x_vel = 0
        self.y_vel = 0

    def update(self, *args):
        # up, down кнопки
        ud_buttons = [119]
        # left, right кнопки
        lr_buttons = {97: -7,
                      100: 7}

        # тестовое движение
        if args:
            if args[0].type == pygame.KEYDOWN:
                if self.state['на земле']:
                    if args[0].key in lr_buttons:
                        self.x_vel = lr_buttons[args[0].key]

                    if args[0].key in ud_buttons:
                        self.y_vel = -33
                        self.state['на земле'] = False

            if args[0].type == pygame.KEYUP:
                if self.state['на земле']:
                    self.x_vel = 0

        # симуляция гравитации
        # стопить при поверхности
        if not self.state['на земле']:
            self.y_vel += 2

        # надо это фиксить, делать всё через if-else будет ппц запарно
        self.rect = self.rect.move(self.x_vel, self.y_vel)


# добавление героя в спрайты
MainHero(all_sprites)
if __name__ == '__main__':
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # отрисовка спрайта
            all_sprites.update(event)

        # зарисовка и загрузочный апдейт
        screen.fill((255, 255, 255))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
