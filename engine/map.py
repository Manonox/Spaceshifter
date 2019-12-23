import json
import pygame as pg

from utils.vector import vector as vec
from engine.entities import EntList, Player
from engine.vars import *

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
            self.app.player = Player()
            spawn = self.json["spawns"]["default"]
            self.app.player.pos = (vec(self.json["rooms"][spawn["room"]]["pos"]) + vec(spawn["pos"])) * BLOCKSIZE
            self.app.entlist.insertEnt(self.app.player)
            self.app.camera.follow(self.app.player)


class Tilemap(object):

    def __init__(self):
        self._data = {}

    def loadTiles(self):
        with open(pt.join("tileset", "data.json"), "r") as f:
            self._json = json.load(f)
        for k, v in self._json.items():
            self._data[k] = {
                "type": v["type"],
                "img": pg.image.load(pt.join("tileset", v["img"]))
            }

    def get(self, name, default=None):
        return self._data.get(name, default)
