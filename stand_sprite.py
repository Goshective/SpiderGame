from pygame import sprite as s

class Standart_Sprite(s.Sprite):
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy