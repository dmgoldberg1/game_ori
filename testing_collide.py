from platform_game import Platform

import pygame
from mainhero import MainHero

# настройки окна
pygame.init()
size = WIDHT, HEIGHT = 1000, 600
FPS = 30
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

# спрайты
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()

# добавление героя в спрайты
# MainHero(all_sprites, platform_sprites, (200, 100))
c = pygame.Rect(100, 150, 200, 200)
a = ((200, 200), (200, 200))
collide = c.clipline(a)
print(collide)
# запуск симуляции
if __name__ == '__main__':
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # отрисовка спрайта
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, 'blue', c)
        pygame.draw.line(screen, (0, 255, 0), a[0], a[1], 2)
        # зарисовка и загрузочный апдейт

        pygame.display.flip()

    pygame.quit()
