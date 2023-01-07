import pygame
from stand_sprite import Standart_Sprite
from constants import *
from groups import *
from animation import Animation


class Player(Standart_Sprite):
    def __init__(self, pos_x, pos_y, player_image):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 50)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.rope = None
        self.anim = Animation("player")

    def set_rope(self, rope):
        self.rope = rope

    def update(self, left, right, up, down, camera, ropes):
        if self.rope is not None:
            idle = self.__handle_flying(left, right, up, down)
        else:
            idle = self.__handle_running(left, right, up, down)

        self.image = self.anim.update(idle)
        camera.contact(self, ropes)

    def __handle_flying(self, left, right, up, down):
        idle = True
        seg = self.rope.segments[0]
        c = seg.cords
        v = seg.v
        self.rect.x = c.x - 25
        self.rect.y = c.y
        self.vx = v.x
        self.vy = v.y
        if left:
            v.x -= MOVE_SPEED / 20
        elif right:
            v.x += MOVE_SPEED / 20
        if up:
            self.rope.changelen(-0.1)
        elif down:
            self.rope.changelen(0.1)
        return idle
        
    def __handle_running(self, left, right, up, down):
        idle = False
        if up:
            if self.on_ground:
                self.vy = -JMP_POWER
        if left:
            self.vx = -MOVE_SPEED
        
        if right:
            self.vx = MOVE_SPEED
         
        if left == right:
            self.vx = 0
            idle = True
        if not self.on_ground:
            self.vy +=  GRAVITY
            
        self.on_ground = False
        self.rect.y += self.vy
        self.__collide(0, self.vy)
        
        self.rect.x += self.vx
        self.__collide(self.vx, 0)
        return idle

    def __collide(self, vx, vy):
        lst = pygame.sprite.spritecollide(self, tiles_group, False)
        for plat in lst:
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
        """if len(lst) == 0 and vx == 0:
            self.on_ground = False"""