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
        seg1, seg2, seg3 = self.rope.segments[0], self.rope.segments[1], self.rope.segments[2]
        c = seg1.cords
        v = seg1.v
        self.rect.x = c.x - self.rect.width // 2
        self.rect.y = c.y
        self.vx = v.x
        self.vy = v.y
        if left:
            v.x -= 0.1
            # v.y -= 0.1
        elif right:
            v.x += 0.1
            # v.y -= 0.1
        if up:
            self.rope.changelen(-0.1)
        elif down:
            self.rope.changelen(0.1)
        
        self.__collide_flying()

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
        self.rect.x += self.vx

        self.__collide()
        return idle

    def __collide_flying(self):
        lst = pygame.sprite.spritecollide(self, col_tiles, False)
        for plat in lst:
            sl, sr, st, sb = self.rect.left, self.rect.right, self.rect.top, self.rect.bottom
            pl, pr, pt, pb = plat.rect.left, plat.rect.right, plat.rect.top, plat.rect.bottom
            point_player = self.rope.segments[0]
            cords_p0 = point_player.get_cords()
            x_const = self.rect.width // 2
            y_const = self.rect.height

            if pl <= sr <= pr and pt <= sb <= pb:  # 1
                if sr - pl < sb - pt:
                    sr = pl
                    point_player.cords.x = pl - x_const
                else:
                    sb = pt
                    point_player.cords.y = pt - y_const

            elif pl <= sl <= pr and pt <= sb <= pb:  # 2
                if pr - sl < sb - pt:
                    sl = pr
                    point_player.cords.x = pr + x_const
                else:
                    sb = pt
                    point_player.cords.y = pt - y_const

            elif pl <= sl <= pr and pt <= st <= pb:  # 3
                if pr - sl < pb - st:
                    sl = pr
                    point_player.cords.x = pr + x_const
                else:
                    st = pb
                    point_player.cords.y = pb

            elif pl <= sr <= pr and pt <= st <= pb:  # 4
                if sr - pl < pb - st:
                    sr = pl
                    point_player.cords.x = pl - x_const
                else:
                    st = pb
                    point_player.cords.y = pb

            elif pt <= st and sb <= pb:
                if pl <= sl <= pr:
                    sl = pr  # *5
                    point_player.cords.x = pr + x_const
                else:
                    sr = pl  # *6
                    point_player.cords.x = pl - x_const

            dx = point_player.cords.x - cords_p0.x
            dy = point_player.cords.y - cords_p0.y
            if dx >= 25:
                point_player.cords.x -= dx // 2
                self.rect.x -= dx // 2
                point_player.v.set_null(x=0)
            if dy >= 25:
                point_player.cords.y -= dy // 2
                self.rect.y -= dy // 2
                point_player.v.set_null(y=0)

    def __collide(self):
        lst = list(pygame.sprite.spritecollide(self, col_tiles, False))
       
        def area_intersection(r1, r2):
            r = r1.clip(r2)
            return -(r.width * r.height)


        # сортируем по площади пересечения. бОльшая площадь более важная и обрабатывается первой
        lst = sorted(lst, key=lambda r: area_intersection(r.rect, self.rect))

        for plat in lst:
            sl, sr, st, sb = self.rect.left, self.rect.right, self.rect.top, self.rect.bottom
            pl, pr, pt, pb = plat.rect.left, plat.rect.right, plat.rect.top, plat.rect.bottom
 
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
                self.vx = 0
        """if len(lst) == 0 and vx == 0:
            self.on_ground = False"""

    def check_exit(self):
        for plat in finish_tiles:
            if self.rect.colliderect(plat.rect):
                for spr in all_sprites:
                    spr.kill()
                self.rope = None
                return True
        return False