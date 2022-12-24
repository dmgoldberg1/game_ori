from mainhero import MainHero
from platform import Platform
from utilities import Background
import pygame


# настройки окна
BackGround = Background('forest.jpg', [0,0])

size = WIGHT, HEIGHT = 1000, 600
FPS = 20
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

pygame.init()

# спрайты
all_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()

# добавление героя в спрайты
MainHero(all_sprites, (200, 100))
Platform(all_sprites, platform_sprites, (200, 400))

mainhero_status = [True]
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

        # пересоздание персонажа
        if not mainhero_status[0]:
            MainHero(all_sprites, (500, 250))
            mainhero_status[0] = True

        # зарисовка и загрузочный апдейт
        screen.fill((255, 255, 255))
        screen.blit(BackGround.image, BackGround.rect)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
