from os import path as pt
import json
import pygame as pg
import math

from utils.vector import vector as vec


class Sprite(object):

    def __init__(self, app, name):
        self.name = name
        with open(pt.join("sprites", name, "data.json"), "r") as f:
            self.data = json.load(f)
        self.animation_names = self.data["animations"]
        self.animation_infos = {}
        self.animations = {}

        for k, v in self.animation_names.items():
            with open(pt.join("sprites", name, v, "anim.json"), "r") as f:
                self.animation_infos[k] = json.load(f)
                self.animations[k] = {"sequence": [], "speed": self.animation_infos[k]["speed"], "frameCount": len(self.animation_infos[k]["sequence"])}
                for i, image_name in enumerate(self.animation_infos[k]["sequence"]):
                    self.animations[k]["sequence"].append(pg.image.load(pt.join("sprites", name, v, image_name)))

        self.playing = ""
        self.flip = False
        self.frame = 0
        self.speed = 0
        self.frameCount = 0

        self.sizeMul = vec(1,1)

    def play(self, animation, frame=0, flip=None, restart=False):
        if self.animations.get(animation) is not None and (animation != self.playing or restart):
            if flip is not None:
                self.flip = flip
            self.playing = animation
            self.speed = self.animations[animation]["speed"]
            self.frame = frame
            self.frameCount = self.animations[animation]["frameCount"]

    def update(self, dt):
        self.frame = (self.frame + dt/self.speed) % self.frameCount
        self.sizeMul = self.sizeMul*0.94 + vec(1,1)*0.06

    @property
    def surface(self):
        if self.playing:
            image = self.animations[self.playing]["sequence"][math.floor(self.frame % self.frameCount)]
            if self.flip:
                image = pg.transform.flip(image, True, False)
            image = pg.transform.scale(image, (vec(image.get_size())*self.sizeMul).vr)
            return image
        else:
            return pg.Surface((0, 0))
