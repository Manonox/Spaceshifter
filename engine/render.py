import pygame as pg

from utils.vector import vector as vec
from utils.aabb import AABB
from engine.vars import *

from utils.utils import lerp


class Renderer(object):

    def __init__(self, app):
        self.app = app

    def draw(self):
        surface = self.app.surface
        w, h = surface.get_size()
        json = self.app.maploader.json
        if json is None:
            return
        camera = self.app.camera
        rooms = json["rooms"]
        for name, room in rooms.items():
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
                        pos = (vec(room["pos"])+vec(x, y)) * tilesize - camera.corner
                        surface.blit(drawtile, pos.vr)

class Camera(object):

    def __init__(self, app):
        self.app = app
        self.pos = vec(16, 16)
        self.zoom = 1

    @property
    def tilesize(self):
        return BLOCKSIZE * self.zoom

    @property
    def corner(self):
        w, h = self.app.surface.get_size()
        return self.pos*self.zoom-vec(w, h)/2

    def getPos(self, pos):
        w, h = self.app.surface.get_size()
        return (pos-self.pos)*self.zoom + vec(w, h)/2

    def getAABB(self, aabb):
        return AABB(self.getPos(aabb.min), self.getPos(aabb.max))

    def update(self, dt):
        ply = self.app.player
        self.pos = lerp(self.pos, ply.pos, 1 - (0.01/1)**dt)
