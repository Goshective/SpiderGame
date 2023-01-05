import os
import pygame
import sys
from constants import *

def normal_path(filename, folder=None):
    if folder is not None:
        return os.path.join(ROOT_PATH, folder, filename)
    return os.path.join(ROOT_PATH, folder, filename)


def load_level(filename):
    filename = normal_path(filename, folder='data')
    if not os.path.isfile(filename):
        print(f"Файл с картой '{filename}' не найден")
        sys.exit()
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину    
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')    
    level = [[x for x in line] for line in list(map(lambda x: x.ljust(max_width, '.'), level_map))]
    return level


def load_image(name, colorkey=None):
    player_image = False
    if name[:4] == "pauk" and name[4:-4].isnumeric():
        player_image = True
    fullname = normal_path(name, folder='data')
    # если файл не существует, то выходим
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

    if player_image:
        image = pygame.transform.smoothscale(image, (50, 50))

    return image