import pygame
import sys
import time
import sqlite3

from constants import * # type: ignore
from groups import * # type: ignore
from camera import Camera

from loading_files import load_image
from geometry import Point, Line, Vector, get_intersection_point
import settings as game_settings
from map import generate_level

pygame.init()

screen = pygame.display.set_mode(size)

debugging_points = []

def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    game_settings.stage = 'menu'


def options_screen():
    game_settings.stage = 'options'


def end_screen(res, score):
    game_settings.stage = 'end_of_round'
    game_settings.best_scores = res
    game_settings.last_score = score


def key_pressing_change(key):
    if key == "backspace" and len(game_settings.player_name) > 0:
        game_settings.player_name = game_settings.player_name[:-1]
    elif key.isalnum() or key in ("-=,./;'"):
        game_settings.player_name = game_settings.player_name + key


def game_screen():
    global debugging_points
    game_settings.level = 0
    player_name = "goshective" # start_screen()
    ropes = [None, None]
    score = 0
    up, down, left, right = False, False, False, False
    game_end_murder = False
    for spr in all_sprites:
        spr.kill()

    while True:
        if len(all_sprites) == 0:
            player = generate_level(game_settings)
            start_cords = player.rect.x, player.rect.y
            for finish in finish_tiles:
                fin_cords = finish.rect.x, finish.rect.y
                dist_to = Vector(fin_cords[0] - start_cords[0], fin_cords[1] - start_cords[1]).dist
            time_start = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or game_end_murder:
                request = """INSERT INTO score  (login, score) VALUES (?, ?)"""
                request2 = """SELECT MAX(score), login FROM score GROUP BY login ORDER BY MAX(score) DESC LIMIT 3"""
                con = sqlite3.connect(DATA_BASE_PATH)
                con.cursor().execute(request, (player_name, score))
                con.commit()
                res = con.cursor().execute(request2).fetchall()
                print(res)
                end_screen(res, score)
                con.close()
                return game_end_murder
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
                if player.rope is not None:
                    ropes[0] = None
                    player.set_rope(None)
                else:
                    p = pygame.mouse.get_pos()
                    rope = Rope.create(p, player)
                    if rope is not None:
                        ropes[0] = rope
                        player.set_rope(rope)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if ropes[1] is None:
                    ropes[1] = Rope.create(pygame.mouse.get_pos(), player, ln=5)
                else:
                    ropes[1] = None

        screen.fill((192, 192, 255))
        player_group.update(left, right, up, down, camera, ropes)
        if player.check_exit():
            ropes = [None, None]
            remain_time = pygame.time.get_ticks() - time_start
            score += round(((dist_to * DIST_COEFF) ** 1.5) * (TIME_COEFF / remain_time) ** 0.5)
            print(score, "{:.3f}".format(dist_to), round(((dist_to * DIST_COEFF) ** 1.5) * (TIME_COEFF / remain_time) ** 0.5), "{:.3f}".format(TIME_COEFF / remain_time))

        for r in ropes:
            if r is not None:
                r.update()
            
        for enemy in enemies_group:
            enemy.update()
            if enemy.murder:
                game_end_murder = True

        tiles_group.draw(screen)
        player_group.draw(screen)
        for enemy in enemies_group:
            enemy.draw(screen)

        for r in ropes:
            if r is not None:
                r.draw()
            
        if len(debugging_points) > 0:
            for pt in debugging_points:
                pygame.draw.circle(screen, (255, 0, 0), pt, 2)
            pygame.draw.circle(screen, (255, 0, 255), debugging_points[-1], 3)

        if len(debugging_points) > 0:
            debugging_points = []
            time.sleep(100)

        font = pygame.font.Font(None, 40)
        text = font.render(f'Уровень {game_settings.level}', True, pygame.Color('white'))
        text_rect = text.get_rect(center=(WIDTH // 2, 25))
        screen.blit(text, text_rect)

        pygame.display.flip()

        clock.tick(FPS)


def level_width_change():
    game_settings.width = scroll_bars['level_width'].value


def level_height_change():
    game_settings.height = scroll_bars['level_height'].value


def check_line(point, player_cords):
    global debugging_points
    intersections = []
    for tile in col_tiles:
        entry, exit, t = get_intersection_point(Point(*player_cords), Point(*point), tile.rect)
        if t == Line.Entry or t == Line.EntryExit:
            intersections.append((tile, entry, exit))
    if len(intersections) == 0:
        return None
    min_dist = Vector(intersections[0][1].x - player_cords[0], intersections[0][1].y - player_cords[1]).dist
    min_point = intersections[0][1]
    for tile, p_en, p_ex in intersections:
        # if p_en is not None:
        #    debugging_points.append((int(p_en.x), int(p_en.y)))
        #    print("entry", p_en.x, p_en.y)
        # if p_ex is not None:
        #    debugging_points.append((int(p_ex.x), int(p_ex.y)))
        #    print("exit", p_ex.x,p_ex.y)
        dist = Vector(p_en.x - player_cords[0], p_en.y - player_cords[1]).dist
        if dist < min_dist:
            min_dist = dist
            min_point = p_en
        if p_ex is not None:
            dist = Vector(p_ex.x - player_cords[0], p_ex.y - player_cords[1]).dist
            if dist < min_dist:
                min_dist = dist
                min_point = p_ex
    # min_point.y -= 10
    # debugging_points.append((int(min_point.x), int(min_point.y)))
    return min_point 


class PinnedSegment:
    def __init__(self, x, y, player_width, src=None):
        self.cords = Vector(x, y)
        self.src = src
        self.player_width = player_width

    def changelen(self, dl):
        pass

    def link(self, prev, next):
        self.prev = prev
        self.next = next
        
    def update(self):
        if self.src is not None:
            self.cords = Vector(self.src.rect.left + self.player_width // 2, self.src.rect.top)
        
    def move(self, dx, dy):
        self.cords += Vector(dx, dy)

    def draw(self):
        p1 = self.prev.cords
        p2 = self.cords
        pygame.draw.line(screen, (255, 255, 255), (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 1)
        pygame.draw.circle(screen, (0, 255, 0), (int(p2.x), int(p2.y)), 2)


class Segment:
    class FakeRect: 
        def __init__(self, rect): self.rect = rect

    def __init__(self, x, y, l):
        self.cords = Vector(x, y)
        self.v = Vector(0, 0)
        self.len = l
        self.min_len = l / 5
        self.max_len = l * 10
        
    def changelen(self, dl):
        if self.len < self.min_len and dl < 0:
            return
        if self.len > self.max_len and dl > 0:
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
        r1 = pygame.Rect(int(self.cords.x), int(self.cords.y), 1, 1)
        r2 = pygame.Rect(int(next_pos.x), int(next_pos.y), 1, 1)
        r = r1.union(r2)
        lst = pygame.sprite.spritecollide(Segment.FakeRect(r), tiles_group, False)

        for tile in lst:
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
        pygame.draw.circle(screen, (128, 128, 128), (int(p2.x), int(p2.y)), 2)


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
    def create(p, player, ln=1):
        x, y = player.rect.left + player.rect.width // 2, player.rect.top
        r_point = check_line(p, (x, y))
        if r_point is None:
            return None
        pts = 10
        dx = (r_point.x - x) / pts
        dy = (r_point.y - y) / pts
        segments = []
        for i in range(pts):
            segments.append(Segment(x, y, ln))
            x += dx
            y += dy
        segments.append(PinnedSegment(r_point.x, r_point.y, player.rect.width))
        return Rope(*segments)


class Button:

    def __init__(self, text, pos_top, action, x=0, width=200, height=75):
        font = pygame.font.Font(None, 40)
        self.text = font.render(text, True, (0, 0, 0))
        self.button_rect = pygame.Rect(((WIDTH - width) // 2 + x, pos_top, width, height))
        self.text_rect = self.text.get_rect(center=self.button_rect.center)
        self.inactive_color = (255, 0, 0)
        self.active_color = (0, 255, 0)
        self.action = action
        self.hover = False

    def check(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.button_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover and self.action:
                self.action()

    def draw(self, screen):
        if self.hover:
            color = self.active_color
        else:
            color = self.inactive_color

        pygame.draw.rect(screen, color, self.button_rect)
        screen.blit(self.text, self.text_rect)


class ScrollBar:
    width = 600
    height = 50

    def __init__(self, text, min, max, value, pos_top, action):
        self.min = min
        self.max = max
        self.value = value
        self.scale = self.width / (max - min)
        pos_left = (WIDTH - self.width) // 2
        self.track_rect = pygame.Rect((pos_left, pos_top, self.width, self.height))
        self.thumb_rect = pygame.Rect((pos_left + (value - min) * self.scale, pos_top - 5, 30, self.height + 10))
        font = pygame.font.Font(None, 40)
        self.text = font.render(text, True, pygame.Color('black'))
        self.text_rect = self.text.get_rect(centery=self.thumb_rect.centery)
        self.text_rect.left = 50
        self.action = action
        self.hover = False
        self.scrolling = False
        self.offset = 0

    def check(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.track_rect.collidepoint(event.pos)
            if self.scrolling and pygame.mouse.get_pressed()[0]:
                if self.hover:
                    self.thumb_rect.left = event.pos[0] - self.offset
                    self.value = self.min + int((self.thumb_rect.centerx - self.track_rect.left) / self.scale)
                    if self.action:
                        self.action()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.scrolling = self.thumb_rect.collidepoint(event.pos)
            self.offset = event.pos[0] - self.thumb_rect.left
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scrolling = self.thumb_rect.collidepoint(event.pos)

    def draw(self, screen):
        pygame.draw.rect(screen, pygame.Color('blue'), self.track_rect)
        if self.hover:
            pygame.draw.rect(screen, pygame.Color('green'), self.thumb_rect)
        else:
            pygame.draw.rect(screen, pygame.Color('dark grey'), self.thumb_rect)

        text = pygame.font.Font(None, 40).render(str(self.value), True, pygame.Color('white'))
        screen.blit(text, text.get_rect(center=self.track_rect.center))
        screen.blit(self.text, self.text_rect)


camera = Camera()

clock = pygame.time.Clock()

fon = pygame.transform.scale(load_image('gradient.jpg'), (WIDTH, HEIGHT))

buttons = {
    'game': Button('НОВАЯ ИГРА', 300, game_screen),
    'options': Button('НАСТРОЙКИ', 400, options_screen),
    'exit': Button('ВЫХОД', 600, terminate),
    'return': Button('НАЗАД', 600, start_screen),
    'continue': Button('В ГЛАВНОЕ МЕНЮ', 400, start_screen, width=300)
}
scroll_bars = {
    'level_width': ScrollBar('Ширина уровня:', 20, 50, game_settings.width, 200, level_width_change),
    'level_height': ScrollBar('Высота уровня:', 50, 100, game_settings.height, 300, level_height_change)
}


running = True

while running:
    for event in pygame.event.get():
        key_pressed = None
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            key_pressed = pygame.key.name(event.key)

        if game_settings.stage == 'menu':
            if key_pressed is not None:
                key_pressing_change(key_pressed)
            buttons['game'].check(event)
            buttons['options'].check(event)
            buttons['exit'].check(event)

        elif game_settings.stage == 'game':
            pass

        elif game_settings.stage == 'options':
            scroll_bars['level_width'].check(event)
            scroll_bars['level_height'].check(event)
            buttons['return'].check(event)

        elif game_settings.stage == 'end_of_round':
            buttons['continue'].check(event)

    screen.blit(fon, (0, 0))

    if game_settings.stage == 'menu':
        fonts = [pygame.font.Font(None, 200), pygame.font.Font(None, 30), pygame.font.Font(None, 30)]
        colors = [pygame.Color('purple'), pygame.Color('white'), pygame.Color('white')]
        lines = ['Spider', 'Никнейм игрока:', game_settings.player_name]
        text_cords = [(WIDTH // 2, HEIGHT // 4), (85, HEIGHT // 2 - 20), (len(game_settings.player_name) * 6, HEIGHT // 2)]
        for i in range(len(lines)):
            text = fonts[i].render(lines[i], True, colors[i])
            text_rect = text.get_rect(center=text_cords[i])
            screen.blit(text, text_rect)
        buttons['game'].draw(screen)
        buttons['options'].draw(screen)
        buttons['exit'].draw(screen)
    
    elif game_settings.stage == 'game':
        pass
    
    elif game_settings.stage == 'options':
        scroll_bars['level_width'].draw(screen)
        scroll_bars['level_height'].draw(screen)
        buttons['return'].draw(screen)
    
    elif game_settings.stage == 'end_of_round':
        intro_text = [f'Ваш счёт: {game_settings.last_score} ' +
                     f'({game_settings.player_name if game_settings.player_name != "" else "Noname"})', 'Лучшие попытки:'] + \
                     [f'{name if name != "" else "Noname"} набрал счёт {sc}' for sc, name in game_settings.best_scores]
        fon = pygame.transform.scale(load_image('gradient.jpg'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        size = 60
        font = pygame.font.Font(None, size)
        text_coords_y = [50, 50, 110, 170, 230]
        text_coords_x = [-WIDTH + 100, 50, 50, 50, 50]
        for i in range(len(intro_text)):
            line = str(intro_text[i])
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord = text_coords_y[i]
            intro_rect.top = text_coord
            intro_rect.x = (WIDTH + text_coords_x[i]) // 2
            #text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        buttons['continue'].draw(screen)

    pygame.display.update()

pygame.quit()


"""CREATE TABLE score (
    id        INTEGER      PRIMARY KEY,
    login     VARCHAR (50) NOT NULL,
    timestamp DATETIME     NOT NULL
                           DEFAULT (datetime('now') ),
    score     INTEGER      NOT NULL
);"""