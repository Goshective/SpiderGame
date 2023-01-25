import pygame
from random import uniform as rnd
from stand_sprite import Standart_Sprite
from geometry import Vector, get_side
from groups import *
from constants import *


class Enemy(Standart_Sprite):
    def __init__(self, x, y) -> None:
        super().__init__(enemies_group, all_sprites)
        self.cords = Vector((x + 0.5) * tile_width, (y + 0.5) * tile_height)
        self.rect = pygame.Rect(self.cords.x - ENEMY_RADIUS, self.cords.y - ENEMY_RADIUS, ENEMY_RADIUS * 2, ENEMY_RADIUS * 2)
        self.v = Vector(rnd(-2, 2), rnd(-2, 2))
        self.type = "enemy"
        self.murder = False

    def update(self):
        # time = pygame.time.get_ticks()
        objects = pygame.sprite.spritecollide(self, all_sprites, False)
        already_collided = False
        for obj in objects:
            if obj == self:
                continue
            elif obj.type == "player":
                self.murder = True
                break
            elif obj.type == "enemy":
                dx, dy = self.cords.x - obj.cords.x, self.cords.y - obj.cords.y
                s = (dx ** 2 + dy ** 2) ** 0.5
                if 2 * ENEMY_RADIUS - s >= 0:
                    obj.v.y, self.v.y = self.v.y, obj.v.y
                    self.v.x, obj.v.x = obj.v.x, self.v.x
                    
                    movx, movy =  dx / 4, dy / 4
                    self.cords.x, self.cords.y = self.cords.x + movx, self.cords.y + movy
                    obj.cords.x, obj.cords.y = obj.cords.x - movy, obj.cords.y - movy
                    self.cords += Vector(movx, movy)
                    obj.cords += Vector(-movx, -movy)

            elif obj.type == "wall":
                """if already_collided:
                    continue
                already_collided = True
                pr, pl, pb, pt = obj.rect.right, obj.rect.left, obj.rect.bottom, obj.rect.top
                side = get_side(self.rect, obj.rect) # side of rectangle
                if side == "top":
                    self.v.y *= -1
                    self.cords.y += self.v.y - 1
                elif side == "bottom":
                    self.v.y *= -1
                    self.cords.y += self.v.y + 1
                elif side == "left":
                    self.v.x *= -1
                    self.cords.x += self.v.x - 1
                elif side == "right":
                    self.v.x *= -1
                    self.cords.x += self.v.x + 1  
                print(side)"""
                """sl, sr, st, sb = self.rect.left, self.rect.right, self.rect.top, self.rect.bottom
                pl, pr, pt, pb = obj.rect.left, obj.rect.right, obj.rect.top, obj.rect.bottom
    
                if pl <= sr <= pr and pt <= sb <= pb:  # 1
                    if sr - pl < sb - pt:
                        self.rect.right = pl - 1
                        self.vx = 0
                    else:
                        self.rect.bottom = pt + 1
                        self.vy = 0
                        self.on_ground = True

                elif pl <= sl <= pr and pt <= sb <= pb:  # 2
                    if pr - sl < sb - pt:
                        self.rect.left = pr + 1
                        self.vx = 0
                    else:
                        self.rect.bottom = pt + 1
                        self.vy = 0
                        self.on_ground = True    

                elif pl <= sl <= pr and pt <= st <= pb:  # 3
                    if pr - sl < pb - st:
                        self.vx = 0
                        self.rect.left = pr + 1
                    else:
                        self.vy = 0
                        self.rect.top = pb + 1
    
                elif pl <= sr <= pr and pt <= st <= pb:  # 4
                    if sr - pl < pb - st:
                        self.rect.right = pl - 1
                    else:
                        self.rect.top = pb + 1
                    self.vx = 0"""
                self.v *= -1

    def move(self, dx, dy):
        self.cords += self.v
        self.cords += Vector(dx, dy)
        self.rect.x = self.cords.x - ENEMY_RADIUS
        self.rect.y = self.cords.y - ENEMY_RADIUS

    def draw(self, screen):
        #pygame.draw.circle(screen, (255, 0, 0), (int(self.cords.x), int(self.cords.y)), ENEMY_RADIUS)
        pygame.draw.rect(screen, (255, 0, 0), self.rect)