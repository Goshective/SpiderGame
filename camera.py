from constants import *
from groups import *

class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    def apply(self, obj):
        obj.move(self.dx, self.dy)
    
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH / 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT / 2)

    def contact(self, player, ropes):
        self.update(player)
        for r in ropes:
            if r is not None:
                self.apply(r)
        for sprite in all_sprites:
            self.apply(sprite)