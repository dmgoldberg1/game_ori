import pygame
import os
import sys
from utilities import load_image

class Platform(pygame.sprite.Sprite):
    # картинка
    image = load_image("platform.jpg", colorkey=(255, 255, 255))
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

