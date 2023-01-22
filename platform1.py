# импорты:
# структура игры
import pygame
# вспомогательные функции
from utilities import load_image

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
platform_size = (110, 15)


# платформа
class Platform(pygame.sprite.Sprite):
    # картинка
    image = load_image("animation/platform.png")
    image = pygame.transform.scale(image, platform_size)

    def __init__(self, group, special_group, coords, image=image, image_scale=None):
        super().__init__(group)
        self.image = image
        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)
        self.rect = self.image.get_rect()
        self.rect.x = coords[0] * 100
        self.rect.y = coords[1] * 100
        self.platform_type = None

        # создаем маску платформы для пересечения
        self.mask = pygame.mask.from_surface(self.image)

        # добавляем в группу спрайтов-платформ
        self.add(special_group)

    def update(self, *args):
        pass


# огненная платформа
class PlatformFire(Platform):
    # картинка
    image = load_image("animation\\platform_fire1.png", colorkey=(255, 255, 255))
    image = pygame.transform.scale(image, platform_size)

    def __init__(self, group, special_group, coords, image=image, image_scale=None):
        super().__init__(group, special_group, coords)
        self.image = image
        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)
        self.rect.y -= 3
        self.platform_type = 'fire'

    def update(self, *args):
        pass


# скользкая платформа
class PlatformSlippery(Platform):
    # картинка
    image = load_image("animation/platform_slippery.png")
    image = pygame.transform.scale(image, platform_size)

    def __init__(self, group, special_group, coords, image=image, image_scale=None):
        super().__init__(group, special_group, (coords[0], coords[1]))
        self.image = image
        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)

        self.platform_type = 'slippery'

    def update(self, *args):
        pass


# стена
class PlatformVertical(Platform):
    # картинка
    image = load_image('vertical_platform_1.jpg')
    image = pygame.transform.scale(image, (50, 150))

    def __init__(self, group, special_group, coords, image=image, image_scale=None):
        super().__init__(group, special_group, (coords[0], coords[1]))
        self.image = image
        self.rect.width, self.rect.height = self.image.get_rect().width, self.image.get_rect().height
        self.mask = pygame.mask.from_surface(self.image)

        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)

        self.platform_type = 'vertical'

    def update(self, *args):
        pass
