import pygame
from random import uniform as rnd
from stand_sprite import Standart_Sprite
from geometry import Vector
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
        objects = list(pygame.sprite.spritecollide(self, all_sprites, False))
        def area_intersection(r1, r2):
            r = r1.clip(r2)
            return -(r.width * r.height)
        objects = sorted(objects, key=lambda r: area_intersection(r.rect, self.rect))

        inverted_x = False
        inverted_y = False

        for obj in objects:
            if obj == self:
                continue
            elif obj.type == "player":
                self.murder = True
                break
                """elif obj.type == "enemy":
                    dx, dy = self.cords.x - obj.cords.x, self.cords.y - obj.cords.y
                    s = (dx ** 2 + dy ** 2) ** 0.5
                    if 2 * ENEMY_RADIUS - s >= 0:
                        obj.v.y, self.v.y = self.v.y, obj.v.y
                        self.v.x, obj.v.x = obj.v.x, self.v.x
                        
                        movx, movy =  dx / 4, dy / 4
                        self.cords.x, self.cords.y = self.cords.x + movx, self.cords.y + movy
                        obj.cords.x, obj.cords.y = obj.cords.x - movy, obj.cords.y - movy
                        self.cords += Vector(movx, movy)
                        obj.cords += Vector(-movx, -movy)"""

            elif obj.type == "wall":
                r = self.rect.clip(obj.rect)
                if r.width == r.height and (inverted_x or inverted_y):
                    continue
                if r.height < r.width:
                    inverted_y = True
                else:
                    inverted_x = True

        if inverted_x:
            self.v.x *= -1
        if inverted_y:
            self.v.y *= -1
        self.cords += self.v

    def move(self, dx, dy):
        self.cords += Vector(dx, dy)
        self.rect.x = self.cords.x - ENEMY_RADIUS
        self.rect.y = self.cords.y - ENEMY_RADIUS

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.cords.x), int(self.cords.y)), ENEMY_RADIUS)
        #pygame.draw.rect(screen, (255, 0, 0), self.rect)