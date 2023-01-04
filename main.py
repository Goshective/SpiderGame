import pygame
import os
import sys
from our_player import Player
from constants import * # type: ignore
from groups import * # type: ignore
from camera import Camera
from stand_sprite import Standart_Sprite


pygame.init()

screen = pygame.display.set_mode(size)


def normal_path(filename, folder=None):
    if folder is not None:
        return os.path.join(ROOT_PATH, folder, filename)
    return os.path.join(ROOT_PATH, folder, filename)


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


def load_level(filename):
    filename = normal_path(filename, folder='data')
    if not os.path.isfile(filename):
        print(f"Файл с картой '{filename}' не найден")
        sys.exit()
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину    
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')    
    level = [[x for x in line] for line in list(map(lambda x: x.ljust(max_width, '.'), level_map))]
    return level


def load_image(name, colorkey=None):
    player_image = False
    if name[:4] == "pauk" and name[4:-4].isnumeric():
        player_image = True
    fullname = normal_path(name, folder='data')
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    if player_image:
        image = pygame.transform.smoothscale(image, (50, 50))

    return image


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y, player_image)
            """elif level[y][x] == "*":
                base_rope = Rope_Segment(Standart_Point(x*tile_width, y*tile_height, base=Tile('Wall', x, y)), 
                                        Standart_Point(x*tile_width, (y+1)*tile_height))"""
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y

"""Vector start
Vector end
req_dist = 10
v = end.l_vector_to(start)
dist = v.dist

if dist > req_dist:
    tail = (dist - req_dist) / 10
    v = v * tail"""


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

    def vector_to(self, vect):  # from end1 to end2
        return vect - self

    def l_vector_to(self, vect, lenght=1):
        v = self.vector_to(vect)
        if v.dist == 0:
            return Vector(0, 0)
        return v * (lenght / v.dist)

    @property
    def dist(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Segment:
    def __init__(self, x, y):
        self.cords = Vector(x, y)
        # self.base = base
        """if type(base) is Player:
            self.vx = base.vx
            self.vy = base.vy
        else:"""
        self.v = Vector(0, 0)
        self.len = 1

    def link(self, prev, next):
        self.prev = prev
        self.next = next

    def update(self):
        self.v += Vector(0, GRAVITY)
        #cords =  self.cords + self.v
        for link_p in (self.prev, self.next):
            if link_p is None:
                continue
            vec = self.cords.vector_to(link_p.cords) # from end to start to balance
            tail = (vec.dist - self.len) / 10
            direction = self.cords.l_vector_to(link_p.cords)
            dv = direction * tail ** 2
            
            self.v += dv

        self.v *= 0.99
 

    def move(self, dx, dy):
        self.cords += Vector(dx, dy)

        self.cords += self.v * 0.9

    def draw(self):
        p1 = self.prev.cords
        p2 = self.cords
        pygame.draw.line(screen, (255, 255, 255), (p1.x, p1.y), (p2.x, p2.y), 1)


class Rope:
    def __init__(self, *segments):
        # self.dist = 50
        self.segments = [] 
        for i in range(len(segments)):
            s = segments[i]
            if i == 0:
                s.link(None, segments[1])
                self.base = s
            elif i == len(segments) - 1 :
                s.link(segments[-2], None)
                self.end = s
            else:
                s.link(segments[i - 1], segments[i + 1])
            self.segments.append(s)

    def update(self):
        for s in self.segments[1:]:
            s.update()

    def move(self, dx, dy):
        for s in self.segments:
            s.move(dx, dy)

    def draw(self):
        for s in self.segments[1:]:
            s.draw()


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

rope_start = 225, 295
"""point0 = Segment(rope_start[0], rope_start[1])

point1 = Segment(rope_start[0] + 30, rope_start[1] - 20)
point2 = Segment(rope_start[0] + 40, rope_start[1] - 40)
point3 = Segment(rope_start[0] + 70, rope_start[1] - 60)"""
#point4 = Segment(rope_start[0] + 70, rope_start[1] - 60, base=point3)
#point5 = Segment(rope_start[0] + 70, rope_start[1] - 60, base=point4) 

ropes = []
for j in range(5):
    points = []
    for i in range(10):
        points.append(Segment(rope_start[0] - j * 2 * i, rope_start[1] - j * 2 * i))
    ropes.append(Rope(*points))

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
            # elif event.key == pygame.K_s:
            #     down = event.type == pygame.KEYDOWN
            elif event.key == pygame.K_a:
                left = event.type == pygame.KEYDOWN
            elif event.key == pygame.K_d:
                right = event.type == pygame.KEYDOWN
        #if event.type == pygame.MOUSEMOTION:
        #    print(event)

    screen.fill(pygame.Color('black'))
    player_group.update(left, right, up, camera, ropes)

    for r in ropes:
        r.update()
    
    tiles_group.draw(screen)
    player_group.draw(screen)

    for r in ropes:
        r.draw()

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()