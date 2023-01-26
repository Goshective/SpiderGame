import pygame
import random as rnd
from our_player import Player
from enemy import Enemy
from constants import *
from groups import *
from stand_sprite import Standart_Sprite
from loading_files import load_image
from opensimplex import OpenSimplex

pygame.init()
screen = pygame.display.set_mode(size)
images = {
    'wall': load_image('b_box(50)(1).png'),
    'empty': load_image('grass.png'),
    'finish': load_image('exit.png'),
    'player': load_image('pauk1.png')
}


class Tile(Standart_Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = images[tile_type]
        if tile_type == "finish":
            super().__init__(tiles_group, all_sprites, finish_tiles)
        else:
            super().__init__(tiles_group, all_sprites, col_tiles)
            #self.image = pygame.transform.rotate(images[tile_type], rnd.choice([0, 90, 270, 180]))
        self.type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


def generate_level(game_settings):
    game_settings.level += 1
    width = game_settings.width
    height = game_settings.height
    new_player = None
    areas = []
    area_main = set()
    gen = OpenSimplex(seed=rnd.randint(0, 10000))

    for x in range(width - 2):
        for y in range(height - 2):
            noise = gen.noise2(x / 5, y / 5)
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

    start = rnd.choice(list(area_main))
    finish = rnd.choice(list(area_main))
    enemies = []
    for _ in range(len(area_main) // SPAWN_COEFF + 1):
        enemy = start
        while enemy == start or enemy == finish:
            enemy = rnd.choice(list(area_main))
        enemies.append(enemy)

    for x in range(width):
        for y in range(height):
            point = (x - 1, y - 1)
            if point == start:
                new_player = Player(x, y, images['player'])
            elif point == finish:
                Tile('finish', x, y)
            elif point in enemies:
                Enemy(x, y)
            elif point not in area_main:
                Tile('wall', x, y)

    return new_player
