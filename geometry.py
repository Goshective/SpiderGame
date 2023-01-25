from constants import *


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    InsideTheRectangle = 1
    Entry = 2
    EntryExit = 3
    NoIntersection = 4


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

    def copy(self):
        return Vector(self.x, self.y)

    @property
    def dist(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


def get_side(circle, tile):
    """tl = Vector(circle.cords.x + ENEMY_RADIUS - pl, circle.cords.y).dist
    tr = Vector(circle.cords.x - ENEMY_RADIUS - pr, circle.cords.y).dist
    tt = Vector(circle.cords.x, circle.cords.y + ENEMY_RADIUS - pt).dist
    tb = Vector(circle.cords.x, circle.cords.y - ENEMY_RADIUS - pb).dist
    t_min = min(tl, tr, tt, tb)
    if t_min == tl:
        return "left"
    elif t_min == tr:
        return "right"
    elif t_min == tb:
        return "bottom"
    else:
        return "top" """
    r = tile.clip(circle)
    if r.height < r.width:
        if circle.x < tile.x:
            return "left"
        return "right"
    if circle.y < tile.y:
        return "top"
    return "bottom"



def get_intersection_point(p1, p2, rect):
    if is_contain(p1, rect) and is_contain(p2, rect):
        # Can't set null to Point that's why I am returning just empty object
        return (None, None, Line.InsideTheRectangle)  # None

    elif not is_contain(p1, rect) and not is_contain(p2, rect):
        if not line_intersects_rectangle(p1, p2, rect):
            return (None, None, Line.InsideTheRectangle)  # None

        entryPoint = None
        exitPoint = None

        entryPointFound = False

        # Top Line of Chart Area
        if line_intersects_line(p1, p2, Point(rect.x, rect.y), Point(rect.right, rect.y)):  # change all to rect.x, rect.right, y, bottom
            entryPoint = get_point_from_y_value(p1, p2, rect.y)
            entryPointFound = True
    
        # Right Line of Chart Area
        if line_intersects_line(p1, p2, Point(rect.right, rect.y), Point(rect.right, rect.bottom)):
            if entryPointFound:
                exitPoint = get_point_from_x_value(p1, p2, rect.right)
            else:
                entryPoint = get_point_from_x_value(p1, p2, rect.right)
                entryPointFound = True

        # Bottom Line of Chart
        if line_intersects_line(p1, p2, Point(rect.x, rect.bottom), Point(rect.right, rect.bottom)):
            if entryPointFound:
                exitPoint = get_point_from_y_value(p1, p2, rect.bottom)
            else:
                entryPoint = get_point_from_y_value(p1, p2, rect.bottom)

        # Left Line of Chart
        if line_intersects_line(p1, p2, Point(rect.x, rect.y), Point(rect.x, rect.bottom)):
            exitPoint = get_point_from_x_value(p1, p2, rect.x)

        return (entryPoint, exitPoint, Line.EntryExit)

    else:
        entryPoint = get_entry_intersection_point(rect, p1, p2)
        return (entryPoint, None, Line.Entry)


def get_entry_intersection_point(rect, p1, p2):
    if line_intersects_line(Point(rect.x, rect.y), Point(rect.right, rect.y), p1, p2):
        return get_point_from_y_value(p1, p2, rect.y)

    elif line_intersects_line(Point(rect.right, rect.y), Point(rect.right, rect.bottom), p1, p2):
        return get_point_from_x_value(p1, p2, rect.right)

    elif line_intersects_line(Point(rect.x, rect.bottom), Point(rect.right, rect.bottom), p1, p2):
        return get_point_from_y_value(p1, p2, rect.bottom)
    else:
        return get_point_from_x_value(p1, p2, rect.x)


def line_intersects_rectangle(p1, p2, r):
    return (line_intersects_line(p1, p2, Point(r.x, r.y), Point(r.x + r.width, r.y)) or
            line_intersects_line(p1, p2, Point(r.x + r.width, r.y), Point(r.x + r.width, r.y + r.height)) or
            line_intersects_line(p1, p2, Point(r.x + r.width, r.y + r.height), Point(r.x, r.y + r.height)) or
            line_intersects_line(p1, p2, Point(r.x, r.y + r.height), Point(r.x, r.y)) or
            (is_contain(p1, r) and is_contain(p2, r)))
            # code from here: https://stackoverflow.com/questions/5221725/get-intersection-point-of-rectangle-and-line

        
def line_intersects_line(l1p1, l1p2, l2p1, l2p2):
    q = (l1p1.y - l2p1.y) * (l2p2.x - l2p1.x) - (l1p1.x - l2p1.x) * (l2p2.y - l2p1.y)
    d = (l1p2.x - l1p1.x) * (l2p2.y - l2p1.y) - (l1p2.y - l1p1.y) * (l2p2.x - l2p1.x)

    if d == 0:
        return False
    r = q / d
    q = (l1p1.y - l2p1.y) * (l1p2.x - l1p1.x) - (l1p1.x - l2p1.x) * (l1p2.y - l1p1.y)
    s = q / d

    if (r < 0 or r > 1 or s < 0 or s > 1):
        return False
    return True


def is_contain(p, r):
    return r.top <= p.y <= r.bottom and r.left <= p.x <= r.right


def get_point_from_y_value(p1, p2, y):
    x1, x2 = p1.x, p2.x
    y1, y2 = p1.y, p2.y
    x = (((y - y1) * (x2 - x1)) / (y2 - y1)) + x1
    return Point(x, y)


def get_point_from_x_value(p1, p2, x):
    x1, x2 = p1.x, p2.x
    y1, y2 = p1.y, p2.y
    y = (((x - x1) * (y2 - y1)) / (x2 - x1)) + y1
    return Point(x, y)