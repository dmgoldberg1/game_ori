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
size = WIDTH, HEIGHT = 500, 500
FPS = 20
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

pygame.init()

# группы спрайтов
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()


# класс платформы
class Platform(pygame.sprite.Sprite):
    # картинка
    image = load_image("platform.png", colorkey=(255, 255, 255))
    image = pygame.transform.scale(image, (200, 200))

    def __init__(self, group, special_group, coords, image=image):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]

        # self.x_vel = 0
        # self.y_vel = 0

        # создаем маску платформы для пересечения
        self.mask = pygame.mask.from_surface(self.image)

        # добавляем в группу спрайтов-платформ
        self.add(special_group)

    def update(self, *args):
        pass


# добавление платформы в спрайты
Platform(all_sprites, platform_sprites, (250, 250))

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
