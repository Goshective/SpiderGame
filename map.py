import pygame
import random as rnd
from our_player import Player
from constants import *
from groups import *
from stand_sprite import Standart_Sprite
from loading_files import load_image
from opensimplex import OpenSimplex

pygame.init()
screen = pygame.display.set_mode(size)
images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'finish': load_image('exit.png'),
    'player': load_image('pauk1.png')
}


class Tile(Standart_Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


def generate_level(width=64, height=64):
    new_player = None
    areas = []
    area_main = set()
    gen = OpenSimplex(seed=rnd.randint(0, 10000))

    for x in range(width-2):
        for y in range(height-2):
            noise = gen.noise2(x/5, y/5)
            if noise >= 0:
                point = (x, y)
                area = set()
                for area in areas:
                    if (x - 1, y) in area or (x, y - 1) in area:
                        area.add(point)
                if point not in area:
                    areas.append({point})

    while True:
        doubles = False
        for area in areas:
            for area_ in areas:
                if area != area_ and len(area & area_):
                    area.update(area_)
                    doubles = True
            if len(area) > len(area_main):
                area_main = area
        if not doubles:
            break

    while True:
        start = (rnd.randint(0, width-2), rnd.randint(0, height-2))
        if start in area_main:
            break
    while True:
        finish = (rnd.randint(0, width-2), rnd.randint(0, height-2))
        if finish in area_main and finish != start:
            break

    for x in range(width):
        for y in range(height):
            point = (x-1, y-1)
            if point == start:
                new_player = Player(x, y, images['player'])
            elif point == finish:
                Tile('finish', x, y)
            elif point not in area_main:
                Tile('wall', x, y)

    return new_player