from constants import *
from geometry import *
from groups import *
import pygame

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

    def draw(self, screen):
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

    def draw(self, screen):
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

    def draw(self, screen):
        for s in self.segments:
            s.draw(screen)
 
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