import pygame

from utilities import load_image

# нулевой объект, благодаря которому можно определять глобальное положение объектов
class Null_Object(pygame.sprite.Sprite):
    # картинка
    image = load_image("cat_hero.png", colorkey=(255, 255, 255))
    # print(image.get_rect())
    image = pygame.transform.scale(image, (151 // 2, 186 // 2))

    def __init__(self, group):
        super().__init__(group)
        # расположение на экране
        self.image = Null_Object.image
        # прозрачный объект
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.pos = self.rect
