import pygame
from stand_sprite import Standart_Sprite
from groups import *
from constants import *


class Enemy(Standart_Sprite):
    def __init__(self, x, y) -> None:
        super().__init__(enemies_group, all_sprites)
        self.x = (x + 0.5) * tile_width
        self.y = (y + 0.5) * tile_height

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 20)