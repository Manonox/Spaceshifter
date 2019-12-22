from utils.vector import vector as vec
import pygame as pg

class AABB(object):

    def __init__(self, min, max=None):
        if isinstance(min, AABB):
            self.min, self.max = min.min, min.max
        elif max is not None:
            self.min = min
            self.max = max
        else:
            raise NotImplementedError

    @property
    def rect(self):
        return pg.Rect((self.l, self.t), (self.w, self.h))

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
        self = AABB(self.min, self.max+vec(w-self.w, 0))

    def setH(self, h):
        self = AABB(self.min, self.max+vec(0, h-self.h))

    w = property(lambda self: (self.r-self.l), setW)
    h = property(lambda self: (self.b-self.t), setH)

    def intersect(self, other):
        return (abs(self.center.x - other.center.x) * 2 < (self.w + other.w)) and (abs(self.center.y - other.center.y) * 2 < (self.h + other.h))

    @property
    def center(self):
        return (self.min + self.max)/2

    @property
    def size(self):
        return (self.max - self.min)

    def draw(self, camera, color):
        pg.draw.rect(camera.app.surface, color, camera.getAABB(self).rect)
