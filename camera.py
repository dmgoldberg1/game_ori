from platform import Platform, PlatformSlippery, PlatformMove, PlatformFire

WIDTH, HEIGHT = 1000, 600


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, width, height, main_hero):
        self.dx = 0
        self.dy = 0
        self.width = width
        self.height = height
        self.main_hero_last_position = main_hero.rect
        self.main_hero_position = main_hero.rect

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        # print(type(obj))
        if type(obj) == Platform or type(obj) == PlatformSlippery or \
                type(obj) == PlatformFire or type(obj) == PlatformMove:
            obj.rect.x += self.dx
            obj.rect.y += self.dy
        else:
            obj.rect.x += self.dx
            obj.rect.y += self.dy
        # print(obj.rect.x, obj.rect.y)

    # позиционировать камеру на объекте target
    def update(self, target):
        self.main_hero_position = target.rect
        # print(self.main_hero_last_position)
        # print(self.main_hero_position)
        if not (100 <= self.main_hero_position.x <= self.width - 100 and
                100 <= self.main_hero_position.y <= self.height - 100):
            self.dx = -(self.main_hero_position.x - self.main_hero_last_position.x)
            self.dy = -(self.main_hero_position.y - self.main_hero_last_position.y)
        else:
            self.dx = 0
            self.dy = 0

        if not (0 <= self.main_hero_position.x <= self.width and
                0 <= self.main_hero_position.y <= self.height):
            pass
            # print('a')
            # print(self.main_hero_position)
            # print('a')
        # print(self.dx, self.dy)
        self.main_hero_last_position = target.rect
