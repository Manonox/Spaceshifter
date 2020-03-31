import json
import pygame as pg

from utils.vector import vector as vec
from engine.entities import EntList, Player
from engine.vars import *
from copy import deepcopy
from copy import copy as shallowcopy
from os import path as pt


class MapLoader(object):

    def __init__(self, app):
        self.app = app
        self.filename = None
        self.json = None

    def load(self, mapname, addply=True):
        self.filename = mapname
        with open(pt.join("maps", mapname+".json"), "r") as f:
            self.json = json.load(f)

        if getattr(self.app, "player", None):
            self.app.entlist.delEnt(self.app.player.id)

        if addply:
            spawn = self.json["spawns"].get("default", None)
            if spawn is not None:
                self.app.player = Player()
                self.app.player.pos = (vec(self.json["rooms"][spawn["room"]]["pos"]) + vec(spawn["pos"])) * BLOCKSIZE
                self.app.entlist.insertEnt(self.app.player)
                self.app.camera.follow(self.app.player)


class Tilemap(object):

    def __init__(self, app):
        self.app = app
        self._data = {}
        self._dataRaw = {}

    def loadTiles(self):
        with open(pt.join("tileset", "data.json"), "r") as f:
            self._json = json.load(f)
        for k, v in self._json.items():
            add = {k: v}
            if v.get("multi",0)==1:
                add = {}
                for nk in ["-ul","-u","-ur", "-l","-c","-r", "-dl","-d","-dr"]:
                    newv = deepcopy(v)
                    newv["img"] = v["img"][0]+nk+v["img"][1]
                    add[k+nk] = newv
            for kk, vv in add.items():
                try:
                    image = pg.image.load(pt.join("tileset", vv["img"]))
                except:
                    print("Can't open '"+kk+"'!")
                else:
                    self._dataRaw[kk] = {
                        "type": vv["type"],
                        "nodraw": vv.get("nodraw",0),
                        "img": image
                    }
        self.rescale(self.app.camera.tilesize)

    def pushTiles(self):
        with open(pt.join("tileset", "data.json"), "w") as f:
            json.dump(self.getAll(), f)

    def rescale(self, tilesize=None):
        if tilesize is None: tilesize = self.app.camera.tilesize
        self._data = {k: {"type": v["type"], "nodraw": v.get("nodraw",0), "img": pg.transform.scale(v["img"], tilesize.vr)} for k, v in self._dataRaw.items()}

    def get(self, name, default=None, raw=False):
        return self.getAll(raw).get(name, default)

    def getAll(self, raw=False):
        return self._dataRaw if raw else self._data
