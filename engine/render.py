import pygame as pg

from utils.vector import vector as vec
from utils.aabb import AABB
from engine.vars import *

from utils.utils import lerp


class Renderer(object):

    def __init__(self, app):
        self.app = app
        self.grid = True

    def draw(self):
        surface = self.app.surface
        w, h = surface.get_size()
        json = self.app.maploader.json
        if json is None:
            return
        camera = self.app.camera

        if self.grid:
            alph = 30

            origin = round(camera.getPos(vec()))
            bs = BLOCKSIDE*camera.zoom

            div = origin % bs
            for ly in range(round(h/bs)+1):
                pg.draw.rect(surface, (alph/2, alph/2, alph/2), pg.Rect((0, div.y+ly*bs), (w, 1)))
            for lx in range(round(w/bs)+1):
                pg.draw.rect(surface, (alph/2, alph/2, alph/2), pg.Rect((div.x+lx*bs, 0), (1, h)))

            if 0<=origin.y<=h:
                pg.draw.rect(surface, (alph, 0, 0), pg.Rect((0, origin.y), (w, 1)))
            if 0<=origin.x<=w:
                pg.draw.rect(surface, (0, alph, 0), pg.Rect((origin.x, 0), (1, h)))

        rooms = json["rooms"]
        for name, room in rooms.items():
            posraw = vec(room["pos"])
            if name == self.app.leveleditor.roomGrab:
                posraw += round(self.app.leveleditor.roomMove/BLOCKSIDE)
            rpos = posraw
            rw, rh = room["size"]

            tiles = room["tiles"]

            tilesize = camera.tilesize
            # tilesize = math.floor(tilesize)

            # OPTIMIZE: Stop rendering rooms outside of view

            for x in range(rw):
                for y in range(rh):
                    if x+y*rw < 0 or x+y*rw >= len(tiles):
                        continue
                    tilename = tiles[x+y*rw]
                    drawtile = self.app.tilemap.get(tilename, None)
                    if drawtile is not None:
                        drawtile = drawtile["img"]
                        # OPTIMIZE: move this *below* after camera = self.app.camera (using camera.zoom to rescale everything b4)
                        drawtile = pg.transform.scale(drawtile, tilesize.vr)
                        pos = (rpos+vec(x, y)) * tilesize - camera.corner
                        surface.blit(drawtile, pos.vr)


class Camera(object):

    def __init__(self, app):
        self.app = app
        self.pos = vec(16, 16)
        self.zoom = 1
        self.camFollow = None

    @property
    def tilesize(self):
        return BLOCKSIZE * self.zoom

    @property
    def corner(self):
        w, h = self.app.surface.get_size()
        return self.pos*self.zoom-vec(w, h)/2

    def getWorld(self, pos):
        w, h = self.app.surface.get_size()
        return (pos - vec(w, h)/2)/self.zoom + self.pos # (pos-self.pos)*self.zoom + vec(w, h)/2

    def getPos(self, pos):
        w, h = self.app.surface.get_size()
        return (pos-self.pos)*self.zoom + vec(w, h)/2

    def getAABB(self, aabb):
        return AABB(self.getPos(aabb.min), self.getPos(aabb.max))

    def follow(self, flw):
        self.camFollow = flw

    def stopFollow(self):
        self.camFollow = None

    def update(self, dt):
        if self.camFollow:
            self.pos = lerp(self.pos, self.camFollow.pos, 1 - (0.01/1)**dt)
