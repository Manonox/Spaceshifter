import json
import pygame as pg
from pygame.locals import *

from engine.vars import *

from os import path as pt


class InputWrapper(object):

    def __init__(self):
        self.data = {}

    def __getitem__(self, i):
        r = self.data.get(i, None)
        if r is None:
            r = False
        return r

    def __repr__(self):
        return str(self.data)

    def __str__(self):
        return str(self.data)


class SettingsManager(object):

    def __init__(self):
        with open(pt.join("data", "settings.json"), "r") as f:
            self.json = json.load(f)
        self.keys = {v: k for k, v in self.json["keys"].items()}

    def get(self, key):

        name = pg.key.name(key).lower()
        name = self.keys.get(name, name)

        if name == "return":
            return ACT_ACCEPT
        if name == "up":
            return ACT_UP
        if name == "left":
            return ACT_LEFT
        if name == "down":
            return ACT_DOWN
        if name == "right":
            return ACT_RIGHT

        if name == "jump":
            return ACT_JUMP
        if name == "accept":
            return ACT_ACCEPT

        return None

    def getAll(self, keys):
        r = InputWrapper()
        for key, state in enumerate(keys):
            act = self.get(key)
            if (act is not None) and state:
                r.data[act] = True
        return r
