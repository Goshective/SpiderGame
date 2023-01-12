import pygame
import random as rnd
from PIL import Image, ImageDraw, ImageFilter
from our_player import Player
from constants import *
from groups import *
from stand_sprite import Standart_Sprite
from loading_files import load_image

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


def generate_level(width=64, height=128):
    new_player = None
    img = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img)
    area = {}

    while True:
        for x in range(width):
            for y in range(height):
                draw.point((x, y), rnd.randint(0, 255))

        pix = img.filter(ImageFilter.GaussianBlur(radius=3)).load()
        areas = []

        for x in range(1, width - 1):
            for y in range(1, height - 1):
                point = (x, y)
                if pix[point] >= 127:
                    continue
                area = {}
                for area in areas:
                    if (x - 1, y) in area or (x, y - 1) in area:
                        area.add(point)
                        break
                if point not in area:
                    areas.append({point})

        if len(areas) == 1:
            while True:
                start = (rnd.randint(1, width), rnd.randint(1, height))
                if start in area:
                    break
            while True:
                finish = (rnd.randint(1, width), rnd.randint(1, height))
                if finish in area and finish != start:
                    break
            break

    for x in range(width):
        for y in range(height):
            point = (x, y)
            if point == start:
                new_player = Player(x, y, images['player'])
            elif point == finish:
                Tile('finish', x, y)
            elif point not in area:
                Tile('wall', x, y)

    return new_player
