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

    def getraw(self, key):
        name = key
        if isinstance(key, int):
            name = pg.key.name(key).lower()
        name = self.keys.get(name, name)
        if name[0]=="_":
            name = name[1:]
        if name[:5]=="left ":
            name = name[0] + name[5:]
        if name[:6]=="right ":
            name = name[0] + name[6:]

        result = []

        if name == "return":
            result.append(ACT_ACCEPT)
        if name == "up":
            result.append(ACT_UP)
        if name == "left":
            result.append(ACT_LEFT)
        if name == "down":
            result.append(ACT_DOWN)
        if name == "right":
            result.append(ACT_RIGHT)

        if name == "jump":
            result.append(ACT_JUMP)
        if name == "accept":
            result.append(ACT_ACCEPT)

        if name == "lshift":
            result = result + [ACT_LSHIFT, ACT_SHIFT]
        if name == "rshift":
            result = result + [ACT_RSHIFT, ACT_SHIFT]
        if name == "lctrl":
            result = result + [ACT_LCTRL, ACT_CTRL]
        if name == "rctrl":
            result = result + [ACT_RCTRL, ACT_CTRL]
        if name == "lalt":
            result = result + [ACT_LALT, ACT_ALT]
        if name == "ralt":
            result = result + [ACT_RALT, ACT_ALT]

        if name == "shift":
            result.append(ACT_SHIFT)
        if name == "ctrl":
            result.append(ACT_CTRL)
        if name == "alt":
            result.append(ACT_ALT)

        if name == "caps":
            result.append(ACT_CAPSLOCK)

        if name == "escape":
            result.append(ACT_PAUSE)

        if name == "editor_grab":
            result.append(ACT_EDITOR_GRAB)

        return result

    def get(self, key):
        ret = self.getraw(key)
        if isinstance(ret, int):
            ret = [ret]
        return ret

    def getMods(self):
        ret = []
        mods = pg.key.get_mods()
        if mods & KMOD_LSHIFT:
            ret.append("lshift")
        if mods & KMOD_RSHIFT:
            ret.append("rshift")
        if mods & KMOD_LCTRL:
            ret.append("lctrl")
        if mods & KMOD_RCTRL:
            ret.append("rctrl")
        if mods & KMOD_LALT:
            ret.append("lalt")
        if mods & KMOD_RALT:
            ret.append("ralt")

        if mods & KMOD_SHIFT:
            ret.append("shift")
        if mods & KMOD_CTRL:
            ret.append("ctrl")
        if mods & KMOD_ALT:
            ret.append("alt")

        if mods & KMOD_CAPS:
            ret.append("caps")

        return ret

    def getAll(self, keys, mouseb=(False, False, False)):
        r = InputWrapper()
        for key, state in enumerate(keys):
            acts = self.get(key)
            for act in acts:
                if state:
                    r.data[act] = True
        for ac in self.getMods():
            for acc in self.get(ac):
                r.data[acc] = True

        if mouseb[0]:
            r.data[ACT_MOUSE1] = True
        if mouseb[1]:
            r.data[ACT_MOUSE3] = True
        if mouseb[2]:
            r.data[ACT_MOUSE2] = True

        return r
