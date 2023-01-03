import pygame
import os
import sys


pygame.init()

FPS = 60
GRAVITY = 0.35
JMP_POWER = 10
MOVE_SPEED = 7
size = WIDTH, HEIGHT = 500, 500
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

tile_width = tile_height = 50
screen = pygame.display.set_mode(size)


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


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
    filename = os.path.join(ROOT_PATH, 'data', filename)
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
    fullname = os.path.join(ROOT_PATH, 'data', name)
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

    return image


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y)
            """elif level[y][x] == "*":
                base_rope = Rope_Segment(Standart_Point(x*tile_width, y*tile_height, base=Tile('Wall', x, y)), 
                                        Standart_Point(x*tile_width, (y+1)*tile_height))"""
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    def apply(self, obj):
        obj.move(self.dx, self.dy)
    
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH / 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT / 2)

    def contact(self, player):
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        camera.apply(point)
        camera.apply(base_point)

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
        return v * (lenght / v.dist)

    @property
    def dist(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Standart_Point_Segment_of_Rope:
    def __init__(self, x, y, base=None):
        self.cords = Vector(x, y)
        self.base = base
        self.len = 50.0
        """if type(base) is Player:
            self.vx = base.vx
            self.vy = base.vy
        else:"""
        self.v = Vector(0, 0)

    def update(self):
        self.v += Vector(0, GRAVITY)
        #cords =  self.cords + self.v

        vec = self.cords.vector_to(self.start)
        tail = (vec.dist - self.len) / 10
        direction = self.cords.l_vector_to(self.start)
        dv = direction * tail
        
        self.v += dv
 
        self.cords += self.v
        self.v *= 0.99
    
    @property
    def start(self):
        return self.base.cords

    def move(self, dx, dy):
        self.cords += Vector(dx, dy)

    def draw(self):
        p1 = self.base.cords
        p2 = self.cords
        pygame.draw.line(screen, (255, 255, 255), (p1.x,p1.y), (p2.x,p2.y), 5)


class Rope_Segment:
    def __init__(self, *points):
        self.dist = 50
        for p in points:
            pass

    def update(self):
        pass

    def draw(self):
        pass


class Standart_Sprite(pygame.sprite.Sprite):
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Tile(Standart_Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        # return self


class Player(Standart_Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.x = pos_x
        self.y = pos_y
        self.vx = 0
        self.vy = 0
        self.on_ground = False

    def update(self, left, right, up):
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

        camera.contact(self)

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
        

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

level_map = load_level("lim.txt")

player, level_x, level_y = generate_level(level_map)
sizes = level_x + 1, level_y + 1

camera = Camera()

clock = pygame.time.Clock()

rope_start = 225, 295
base_point = Standart_Point_Segment_of_Rope(rope_start[0], rope_start[1])
point = Standart_Point_Segment_of_Rope(rope_start[0] + 30, rope_start[1] + 0, base=base_point)

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
    player_group.update(left, right, up)

    point.update()
    
    tiles_group.draw(screen)
    player_group.draw(screen)

    point.draw()

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()