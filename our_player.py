import pygame
from stand_sprite import Standart_Sprite
from constants import *
from groups import *


class Player(Standart_Sprite):
    def __init__(self, pos_x, pos_y, player_image):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 30, tile_height * pos_y + 5)
        self.x = pos_x
        self.y = pos_y
        self.vx = 0
        self.vy = 0
        self.on_ground = False

    def update(self, left, right, up, camera, ropes):
        if up:
            if self.on_ground:
                self.vy = -JMP_POWER
        if left:
            self.vx = -MOVE_SPEED
 
        if right:
            self.vx = MOVE_SPEED
         
        if not(left or right):
            self.vx = 0
        if not self.on_ground:
            self.vy +=  GRAVITY

        self.on_ground = False
        self.rect.y += self.vy
        self.collide(0, self.vy)

        self.rect.x += self.vx
        self.collide(self.vx, 0)

        camera.contact(self, ropes)

    def collide(self, vx, vy):
        for plat in pygame.sprite.spritecollide(self, tiles_group, False):
            if vx > 0:
                self.rect.right = plat.rect.left 

            elif vx < 0:
                self.rect.left = plat.rect.right

            if vy > 0:
                self.rect.bottom = plat.rect.top
                self.on_ground = True
                self.vy = 0

            elif vy < 0:
                self.rect.top = plat.rect.bottom
                self.vy = 0