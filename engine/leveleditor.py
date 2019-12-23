import pygame as pg
from engine.vars import *
from utils.aabb import AABB
import math

class LevelEditor(object):

    def __init__(self, app):
        self.app = app
        self.editing = False
        self.movePos = None

        self.roomMove = vec()
        self.roomGrab = None
        self.inputs = self.app.inputs.get()

    def update(self, dt):
        if not self.editing:
            return
        self.inputs = inputs = self.app.inputs.get()
        speed = BLOCKSIDE*20
        mX = (1 if inputs[ACT_RIGHT] else 0) - (1 if inputs[ACT_LEFT] else 0)
        mY = (1 if inputs[ACT_DOWN] else 0) - (1 if inputs[ACT_UP] else 0)
        self.app.camera.pos += vec(mX, mY) * dt * speed

        if self.movePos is None:
            self.movePos = vec(pg.mouse.get_pos())

        mMove = (vec(pg.mouse.get_pos()) - self.movePos)

        if inputs[ACT_MOUSE3]:
            self.app.camera.pos -= mMove

        if inputs[ACT_MOUSE1]:
            if self.roomGrab:
                self.roomMove += mMove

        self.movePos = vec(pg.mouse.get_pos())

    def event(self, ev):
        json = self.app.maploader.json
        if ev.type == pg.MOUSEBUTTONDOWN:
            if self.inputs[ACT_EDITOR_GRAB] and (ev.button == 1):
                pos = vec(ev.pos)

                if json is None:
                    return
                camera = self.app.camera
                rooms = json["rooms"]
                for name, room in rooms.items():
                    rpos = vec(room["pos"])*BLOCKSIDE
                    rsize = vec(room["size"])*BLOCKSIDE
                    raabb = camera.getAABB(AABB(rpos, rpos+rsize))
                    if raabb.inside(pos):
                        self.roomGrab = name
                        self.roomMove = vec()
                        break
        if ev.type == pg.MOUSEBUTTONUP:
            if self.roomGrab:
                add = round(self.roomMove/BLOCKSIDE)
                json["rooms"][self.roomGrab]["pos"] = [json["rooms"][self.roomGrab]["pos"][0] + add[0], json["rooms"][self.roomGrab]["pos"][1] + add[1]]
                self.roomGrab = None
                self.roomMove = vec()

    def draw(self):
        if not self.editing:
            return
        surface = self.app.surface
        w, h = surface.get_size()
        json = self.app.maploader.json
        if json is None:
            return
        camera = self.app.camera
        rooms = json["rooms"]
        for name, room in rooms.items():
            posraw = vec(room["pos"])
            if name == self.roomGrab:
                posraw += round(self.roomMove/BLOCKSIDE)
            rpos = posraw*BLOCKSIDE
            rsize = vec(room["size"])*BLOCKSIDE
            raabb = camera.getAABB(AABB(rpos, rpos+rsize))
            pg.draw.rect(self.app.surface, (255, 100, 100), raabb.rect, 2)
            font = pg.font.SysFont("Roboto", 14, True, False)
            surf = font.render(name, True, (255, 100, 100))
            self.app.surface.blit(surf, (raabb.min+vec(2, 0)).vr)
