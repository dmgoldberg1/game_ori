from platform import Platform

import pygame
from mainhero import MainHero
from utilities import Background

# настройки окна
pygame.init()
size = WIGHT, HEIGHT = 1000, 600
FPS = 20
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

BackGround = Background('forest.jpg', [0, 0])

# спрайты
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()

# добавление героя в спрайты
MainHero(all_sprites, (200, 100))
Platform(all_sprites, platform_sprites, (200, 400))

# запуск симуляции
if __name__ == '__main__':
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if event.type == pygame.KEYDOWN:
            #     print(event.key)

            # отрисовка спрайта
            all_sprites.update(event)

        # зарисовка и загрузочный апдейт
        screen.fill((255, 255, 255))
        screen.blit(BackGround.image, BackGround.rect)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
