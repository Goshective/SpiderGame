import pygame
import sys
from our_player import Player
from constants import * # type: ignore
from groups import * # type: ignore
from camera import Camera
from stand_sprite import Standart_Sprite
from loading_files import load_image, load_level


pygame.init()

screen = pygame.display.set_mode(size)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y, player_image)
            """elif level[y][x] == "*":
                base_rope = Rope(__something__)"""
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vect):
        return Vector(self.x + vect.x, self.y + vect.y)

    def __sub__(self, vect):
        return Vector(self.x - vect.x, self.y - vect.y)

    def __mul__(self, n):
        return Vector(self.x * n, self.y * n)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def set_null(self, x=None, y=None):
        self.x = self.x if x is None else x
        self.y = self.y if y is None else y

    def vector_to(self, vect):  # from self to vect
        return vect - self

    def l_vector_to(self, vect, lenght=1):
        v = self.vector_to(vect)
        if v.dist == 0:
            return Vector(0, 0)
        return v * (lenght / v.dist)

    @property
    def dist(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


class PinnedSegment:
    def __init__(self, x, y, src=None):
        self.cords = Vector(x, y)
        self.src = src

    def changelen(self, dl):
        pass

    def link(self, prev, next):
        self.prev = prev
        self.next = next
        
    def update(self):
        if self.src is not None:
            self.cords = Vector(self.src.rect.left + player.rect.width // 2, self.src.rect.top)
        
    def move(self, dx, dy):
        self.cords += Vector(dx, dy)

    def draw(self):
        pygame.draw.circle(screen, (0, 255, 0), (int(self.cords.x), int(self.cords.y)), 2)
         
class Segment:
    def __init__(self, x, y, l):
        self.cords = Vector(x, y)
        self.v = Vector(0, 0)
        self.len = l
        self.min_len = l / 5
        self.max_len = l * 10
        
    def changelen(self, dl):
        if self.len < 1 and dl < 0:
            return
        if self.len > 10 and dl > 0:
            return
        self.len += dl

    def link(self, prev, next):
        self.prev = prev
        self.next = next
        
    def update(self):
        self.v.y += GRAVITY / 5
        for link_p in (self.prev, self.next):
            if link_p is None:
                continue
            vec = self.cords.vector_to(link_p.cords) # from end to start to balance
            tail = (vec.dist - self.len) / 10
            direction = self.cords.l_vector_to(link_p.cords)
            dv = direction * tail
            
            self.v += dv

        self.v *= 0.99

    def get_cords(self):
        return Vector(self.cords.x, self.cords.y)

    def __collide(self):
        next_pos = self.cords + self.v
        for tile in tiles_group:
            r = tile.rect
            p1 = r.collidepoint(self.cords.x, self.cords.y)
            p2 = r.collidepoint(next_pos.x, next_pos.y)
            if not p1 and not p2:
                continue

            if p1 and p2: # both points inside rect, move to closest side
                self.v = Vector(0,0)
                p1 = self.cords
                dl = abs(r.left - p1.x)
                dr = abs(r.right - p1.x)
                dt = abs(r.top - p1.y)
                db = abs(r.bottom - p1.y)
                m = min(dl,dr,dt,db)
                if   m == dl:
                    p1.x = r.left - 1
                elif m == dr:
                    p1.x = r.right
                elif m == dt:
                    p1.y = r.top - 1
                else:
                    p1.y = r.bottom
                break

            if not p1 and p2:
                p1 = self.cords
                p2 = next_pos
                if p1.x < r.left and p2.x >= r.left:
                    self.v.x = 0
                    p1.x = r.left - 1
                elif p1.x >= r.right and p2.x < r.right:
                    self.v.x = 0
                    p1.x = r.right
                elif p1.y < r.top and p2.y >= r.top:
                    self.v.y = 0
                    p1.y = r.top - 1
                elif p1.y >= r.bottom and p2.y < r.bottom:
                    self.v.y = 0
                    p1.y = r.bottom
                break
            break

    def move(self, dx, dy):
        self.cords += Vector(dx, dy)
        self.__collide()
        self.cords += self.v * 0.9

    def draw(self):
        if self.prev is None:
            return
        p1 = self.prev.cords
        p2 = self.cords
        pygame.draw.line(screen, (255, 255, 255), (p1.x, p1.y), (p2.x, p2.y), 1)
        pygame.draw.circle(screen, (255, 0, 0), (int(p2.x), int(p2.y)), 2)

        
class Rope:
    def __init__(self, *segments):
        self.segments = [] 
        for i in range(len(segments)):
            s = segments[i]
            prev = segments[i - 1] if i > 0 else None
            next = segments[i + 1] if i < len(segments) - 1 else None
            s.link(prev, next)
            self.segments.append(s)

    def changelen(self, dl):
        for s in self.segments:
            s.changelen(dl)
 
    def update(self):
        for s in self.segments:
            s.update()

    def move(self, dx, dy):
        for s in self.segments:
            s.move(dx, dy)

    def draw(self):
        for s in self.segments:
            s.draw()
 
    @staticmethod
    def create(p, player):
        points = []
        x, y = player.rect.left + player.rect.width // 2, player.rect.top
        pts = 10
        dx = (p[0] - x) / pts
        dy = (p[1] - y) / pts
        segments = []
        for i in range(pts):
            if i == pts - 1:
                seg = PinnedSegment(x, y)
            else: 
                seg = Segment(x, y, 1)
            segments.append(seg)
            x += dx
            y += dy
        return Rope(*segments)


class Tile(Standart_Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        # return self


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('pauk1.png')

level_map = load_level("lim.txt")

player, level_x, level_y = generate_level(level_map)
sizes = level_x + 1, level_y + 1

camera = Camera()

clock = pygame.time.Clock()

ropes = []
start_screen()

running = True
up, down, left, right = False, False, False, False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            if event.key == pygame.K_w:
                up = event.type == pygame.KEYDOWN
            elif event.key == pygame.K_s:
                down = event.type == pygame.KEYDOWN
            elif event.key == pygame.K_a:
                left = event.type == pygame.KEYDOWN
            elif event.key == pygame.K_d:
                right = event.type == pygame.KEYDOWN
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if len(ropes) > 0:
                ropes = []
                player.set_rope(None)
            else:
                p = pygame.mouse.get_pos()
                rope = Rope.create(p, player)
                ropes.append(rope)
                player.set_rope(rope)

    screen.fill((192, 192, 192))
    player_group.update(left, right, up, down, camera, ropes)

    for r in ropes:
        r.update()
    
    tiles_group.draw(screen)
    player_group.draw(screen)

    for r in ropes:
        r.draw()

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()