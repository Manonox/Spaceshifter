import pygame as pg

from utils.vector import vector as vec
from utils.aabb import AABB
from engine.vars import *

from utils.utils import lerp


class Renderer(object):

    def __init__(self, app):
        self.app = app
        self.grid = False
        self.renderedRooms = {}

    def renderRoom(self, name):
        camera = self.app.camera
        json = self.app.maploader.json
        if json is None:
            return
        rooms = json["rooms"]
        room = rooms[name]

        rw, rh = room["size"]

        surface = self.renderedRooms[name] = pg.Surface((vec(rw, rh)*camera.tilesize).vr, pg.SRCALPHA)

        tiles = room["tiles"]

        tilesize = camera.tilesize

        for x in range(rw):
            for y in range(rh):
                if x+y*rw < 0 or x+y*rw >= len(tiles):
                    continue
                tilename = tiles[x+y*rw]
                drawtile = self.app.tilemap.get(tilename, None)
                if drawtile is not None and (drawtile.get("nodraw",0)==0 or self.app.leveleditor.editing):
                    drawtile = drawtile["img"]
                    pos = (vec(x, y)) * tilesize
                    surface.blit(drawtile, pos.vr)

        return surface

    def renderRooms(self):
        json = self.app.maploader.json
        if json is None:
            return
        rooms = json["rooms"]
        for name, room in rooms.items():
            self.renderRoom(name)

    def draw(self):
        if self.app.ui.main:
            return
        surface = self.app.surface
        w, h = surface.get_size()
        json = self.app.maploader.json
        if json is None:
            return
        camera = self.app.camera

        tilesize = camera.tilesize

        self.app.debugger.start_stopwatch("Grid")

        if self.grid:
            alph = 30

            origin = round(camera.getPos(vec()))
            bs = BLOCKSIDE*camera.zoom

            div = origin % bs
            for ly in range(round(h/bs)+1):
                pg.draw.line(surface, (alph/1.2, alph/1.2, alph/1.2), (0, div.y+ly*bs), (w, div.y+ly*bs))
            for lx in range(round(w/bs)+1):
                pg.draw.line(surface, (alph/1.2, alph/1.2, alph/1.2), (div.x+lx*bs, 0), (div.x+lx*bs, h))

            if 0<=origin.y<=h:
                pg.draw.line(surface, (alph, 0, 0), (0, origin.y), (w, origin.y))
            if 0<=origin.x<=w:
                pg.draw.line(surface, (0, alph, 0), (origin.x, 0), (origin.x, h))

        self.app.debugger.stop_stopwatch("Grid")

        rooms = json["rooms"]
        for name, room in rooms.items():
            posraw = vec(room["pos"])
            if name == self.app.leveleditor.roomGrab and self.app.leveleditor.editing and self.app.leveleditor.roomGType == 0:
                posraw += round(self.app.leveleditor.roomMove/BLOCKSIDE)
            rpos = posraw*tilesize
            if camera.getAABB(AABB(posraw*BLOCKSIDE, posraw*BLOCKSIDE+vec(room["size"])*BLOCKSIDE)).intersect(AABB(vec(0,0), vec(w,h))):
                roomSurf = self.renderedRooms.get(name, None)
                if roomSurf is None:
                    roomSurf = self.renderRoom(name)
                surface.blit(roomSurf, (rpos-camera.corner).vr)

class Camera(object):

    def __init__(self, app):
        self.app = app
        self.pos = vec(0, 0)
        self.lastzoom = 0
        self.zoom = 1
        self.camFollow = None

    @property
    def tilesize(self):
        return BLOCKSIZE * self.zoom

    @property
    def corner(self):
        w, h = self.app.surface.get_size()
        return self.pos*self.zoom-vec(w, h)/2

    @property
    def aabb(self):
        w, h = self.app.surface.get_size()
        return AABB(self.getWorld(vec(0, 0)), self.getWorld(vec(w, h)))

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
        self.pos = flw.pos

    def stopFollow(self):
        self.camFollow = None

    def update(self, dt):
        if self.lastzoom!=self.zoom:
            self.lastzoom = self.zoom
            self.app.tilemap.rescale()
            self.app.renderer.renderRooms()
        if self.camFollow is not None:
            self.pos = lerp(self.pos, self.camFollow.pos, 1 - (0.01/1)**dt)
