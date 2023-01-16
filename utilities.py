import os
import sys
import pygame
import sqlite3


# создание фона
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = load_image(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


# загрузка изображений
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


def sprite_distance(rect1, rect2, dist):
    x1, y1 = rect1.topleft
    x2, y2 = rect2.topleft
    if abs(x1 - x2) <= dist and abs(y1 - y2) <= dist:
        return True
    else:
        return False

def move_to_the_point(obj, db_tag):
    con = sqlite3.connect(os.path.join('data', 'storage.db'))
    cur = con.cursor()
    result = cur.execute("""SELECT x, y FROM saved_coordinates WHERE tag = ?""", (db_tag,)).fetchall()
    con.close()

    obj.rect = obj.rect.move(*result[0])
    print(obj.rect)

    
