import pygame
from new import MainHero
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

# класс платформы
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
        # print(self.image.get_rect())
        self.rect.x = coords[0] * 100
        self.rect.y = coords[1] * 100

        self.platform_type = None

        # self.x_vel = 0
        # self.y_vel = 0

        # создаем маску платформы для пересечения
        self.mask = pygame.mask.from_surface(self.image)

        # добавляем в группу спрайтов-платформ
        self.add(special_group)

    def update(self, *args):
        pass


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


class PlatformVertical(Platform):
    # картинка
    image = load_image('vertical_platform_1.jpg')
    image = pygame.transform.scale(image, (50, 150))

    def __init__(self, group, special_group, coords, image=image, image_scale=None):
        super().__init__(group, special_group, (coords[0], coords[1]))
        self.image = image
        # print('a', self.image.get_rect(), self.rect)
        self.rect.width, self.rect.height = self.image.get_rect().width, self.image.get_rect().height
        # print('a', self.image.get_rect(), self.rect)
        self.mask = pygame.mask.from_surface(self.image)

        if image_scale:
            self.image = pygame.transform.scale(self.image, image_scale)

        self.platform_type = 'vertical'

    def update(self, *args):
        pass


# добавление платформы в спрайты
a = PlatformVertical(all_sprites, platform_sprites, (3, 1))
c = PlatformVertical(all_sprites, platform_sprites, (3, 0))
b = Platform(all_sprites, platform_sprites, (1, 2))
m = MainHero(all_sprites, [platform_sprites])

print(a.rect)
# print(a.rect)
if __name__ == '__main__':
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                print(m.rect)

            # отрисовка спрайта
            all_sprites.update(event)
        # зарисовка и загрузочный апдейт
        screen.fill((0, 0, 0))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

    
