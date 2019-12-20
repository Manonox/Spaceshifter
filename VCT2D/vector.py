from math import *
from types import *

class Vector2d():

    def __init__(self, x=0, y=0, wtf=0):
        if (isinstance(x, int) or isinstance(x, float)) and (isinstance(y, int) or isinstance(y, float)):
            self._x = x
            self._y = y
        else:
            raise NotImplementedError

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def length(self):
        return sqrt(self._x**2+self._y**2)

    @property
    def len(self):
        return sqrt(self._x**2+self._y**2)

    @property
    def normalized(self):
        len = sqrt(self._x**2+self._y**2)
        if len == 0:
            return Vector2d(0, 0)
        return Vector2d(self._x/len, self._y/len)

    def __neg__(self):
        return Vector2d(-self._x, -self._y)

    def __add__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2d(self._x+other, self._y+other)
        elif isinstance(other, Vector2d):
            return Vector2d(self._x+other.x, self._y+other.y)

    def __sub__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2d(self._x-other, self._y-other)
        elif isinstance(other, Vector2d):
            return Vector2d(self._x-other.x, self._y-other.y)

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2d(self._x*other, self._y*other)
        elif isinstance(other, Vector2d):
            return Vector2d(self._x*other.x, self._y*other.y)

    def __div__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2d(self._x/other, self._y/other)
        elif isinstance(other, Vector2d):
            return Vector2d(self._x/other.x, self._y/other.y)

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2d(self._x/other, self._y/other)
        elif isinstance(other, Vector2d):
            return Vector2d(self._x/other.x, self._y/other.y)

    def __round__(self):
        return Vector2d(round(self._x), round(self._y))

    def __floor__(self):
        return Vector2d(floor(self._x), floor(self._y))

    def dot(self, other):
        return self._x*other.x+self._y*other.y

    def tuple(self):
        return (self._x, self._y)
