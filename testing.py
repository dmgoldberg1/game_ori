import pygame, os.path
from pygame.locals import *


class Translucent(pygame.sprite.Sprite):
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.image.load(os.path.join('data', 'cat_hero.png'))
        self.image = self.image.convert()
        # self.image.set_colorkey(-1, RLEACCEL)
        self.image.set_alpha(3)
        self.rect = self.image.get_rect()
        self.rect.center = (320, 240)


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    clock = pygame.time.Clock()
    transgroups = pygame.sprite.Group()

    """Here's the Translucency Code"""
    transsurface = pygame.display.set_mode(screen.get_size())
    transsurface = transsurface.convert(screen)
    transsurface.fill((255, 0, 255))
    # transsurface.set_colorkey((255, 0, 255))
    transsurface.set_alpha(50)

    a = Translucent(transgroups)
    while 1:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
        # pygame.draw(a)
        transgroups.draw(screen)
        # screen.blit(transsurface, (0, 0))

        pygame.display.flip()


main()