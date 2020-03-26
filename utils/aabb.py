from utils.vector import vector as vec
import pygame as pg

class AABB(object):

    def __init__(self, min, max=None):
        if isinstance(min, AABB):
            self.min, self.max = min.min.copy(), min.max.copy()
        elif max is not None:
            self.min = min.copy()
            self.max = max.copy()
        else:
            raise NotImplementedError

    @property
    def rect(self):
        return pg.Rect((self.l, self.t), (self.w, self.h))

    def normalize(self):
        nmin = vec(min(self.min.x, self.max.x), min(self.min.y, self.max.y))
        self.max = vec(max(self.min.x, self.max.x), max(self.min.y, self.max.y))
        self.min = nmin

    def move(self, v):
        return AABB(self.min+v, self.max+v)

    def setL(self, v):
        mv = vec(v-self.l, 0)
        self = self.move(mv)
        return mv

    def setR(self, v):
        mv = vec(v-self.r, 0)
        self = self.move(mv)
        return mv

    def setT(self, v):
        mv = vec(0, v-self.t)
        self = self.move(mv)
        return mv

    def setB(self, v):
        mv = vec(0, v-self.b)
        self = self.move(mv)
        return mv

    l = property(lambda self: self.min.x, setL)
    r = property(lambda self: self.max.x, setR)
    t = property(lambda self: self.min.y, setT)
    b = property(lambda self: self.max.y, setB)

    def setW(self, w):
        self.max = self.max + vec(w-self.w, 0)

    def setH(self, h):
        self.max = self.max + vec(0, h-self.h)

    w = property(lambda self: (self.r-self.l), setW)
    h = property(lambda self: (self.b-self.t), setH)

    def intersect(self, other):
        return (abs(self.center.x - other.center.x) * 2 < (self.w + other.w)) and (abs(self.center.y - other.center.y) * 2 < (self.h + other.h))

    def inside(self, v):
        return ((self.l<=v.x<=self.r) and (self.t<=v.y<=self.b))

    @property
    def center(self):
        return (self.min + self.max)/2

    @property
    def size(self):
        return (self.max - self.min)

    def draw(self, camera, color):
        pg.draw.rect(camera.app.surface, color, camera.getAABB(self).rect)

    def __mul__(self, other):
        return AABB(self.min*other, self.max*other)

    def __repr__(self):
        return str(self.min) + " | " + str(self.max)

    def __str__(self):
        return str(self.min) + " | " + str(self.max)

    def copy(self):
        return AABB(self.min.copy(), self.max.copy())
