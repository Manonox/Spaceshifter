from os import path as pt
import json
import pygame as pg
import math


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
        self.frame = 0
        self.speed = 0
        self.frameCount = 0

    def play(self, animation, frame=0):
        if self.animations.get(animation) is not None:
            self.playing = animation
            self.speed = self.animations[animation]["speed"]
            self.frame = frame
            self.frameCount = self.animations[animation]["frameCount"]

    def update(self, dt):
        self.frame = (self.frame + dt/self.speed) % self.frameCount

    @property
    def surface(self):
        if self.playing:
            return self.animations[self.playing]["sequence"][math.floor(self.frame % self.frameCount)]
        else:
            return pg.Surface((0, 0))
