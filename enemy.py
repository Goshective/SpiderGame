import pygame
from random import randint as rnd
from stand_sprite import Standart_Sprite
from geometry import Vector
from groups import *
from constants import *


class Enemy(Standart_Sprite):
    def __init__(self, x, y) -> None:
        super().__init__(enemies_group, all_sprites)
        self.cords = Vector((x + 0.5) * tile_width, (y + 0.5) * tile_height)
        self.rect = pygame.Rect(self.cords.x - ENEMY_RADIUS, self.cords.y - ENEMY_RADIUS, ENEMY_RADIUS * 2, ENEMY_RADIUS * 2)
        self.v = Vector(rnd(-3, 3), rnd(-3, 3))

    def update(self):
        # time = pygame.time.get_ticks()
        plats = pygame.sprite.spritecollide(self, col_tiles, False)
        for plat in plats:
            pr, pl, pb, pt = plat.rect.right, plat.rect.left, plat.rect.bottom, plat.rect.top
            if pt <= self.rect.top <= pb:
                self.v.y *= -1
                self.rect.top = pb + 1
            elif pt <= self.rect.bottom <= pb:
                self.v.y *= -1
                self.rect.bottom = pt - 1
            if pl <= self.rect.left <= pr:
                self.v.x *= -1
                self.rect.left = pr + 1
            elif pl <= self.rect.right <= pr:
                self.v.x *= -1
                self.rect.right = pl - 1
            

    def move(self, dx, dy):
        self.cords += self.v
        self.cords += Vector(dx, dy)
        self.rect.x = self.cords.x - ENEMY_RADIUS
        self.rect.y = self.cords.y - ENEMY_RADIUS

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.cords.x), int(self.cords.y)), ENEMY_RADIUS)