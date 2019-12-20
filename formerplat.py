import math
import json
import pygame
from pygame.locals import *

import time

import os

from VCT2D.vector import Vector2d


level = "test1"


class Entity():
    def __init__(self, pos=Vector2d()):
        self._pos = pos
        self._dorm = False

    @property
    def pos(self):
        return self._pos

    @property
    def isdorm(self):
        return self._dorm

    @isdorm.setter
    def isdorm(self, dorm):
        self._dorm = dorm


class PhysEntity(Entity):
    def __init__(self, pos=Vector2d(), hull=Vector2d(), vel=Vector2d()):
        super().__init__(pos)
        self._vel = vel
        self._hull = hull

    @property
    def vel(self):
        return self._vel

    @property
    def hull(self):
        return self._hull

    def phystick(self, delta, entlist, level):
        pass


class Player(PhysEntity):
    def __init__(self, game, pos=Vector2d(320, 240)):
        super().__init__(pos, Vector2d(30, 30), Vector2d(0, 0))
        self._offset = self._hull*Vector2d(0.5, 1)

        self.onGround = False

        self.queuejump = 0
        self.jumped = 0
        self.canjump = 0

        self.noleft = 0
        self.noright = 0
        self.reducefriction = 0

        self.reducegrav = 0

        self.climbing = 0

        self.nojump = 0

        self.accelbonus = 0

        self.maxdashes = 1
        self.dashes = 0

        self.candash = 0

        self.nograv = 0

        self.lastTurn = 1

        self.indash = 0
        self.stopdash = 0
        self.reduceairfriction = 0

        self.canrestoredash = 0

        self.sprite = Sprite(game, "player", scale=(30, 30))
        self.sprite.play("idle")

    @property
    def rpos(self):
        return self._pos - self._offset

    @rpos.setter
    def rpos(self, other):
        self._pos = other + self._offset

    def phystick(self, delta, entlist, level, game):
        keys = pygame.key.get_pressed()

        grav = 1000
        if self.jumped >= game.curtime() + (0.1 if pygame.key.get_pressed()[K_SPACE] else 0) and not self.onGround:
            if pygame.key.get_pressed()[game.settings["JUMP"]] and self._vel.y < 0:
                grav = 500
            else:
                grav = 2800

        if keys[game.settings["DOWN"]] and self.reduceairfriction < game.curtime():
            grav *= 1.5

        grav *= 1.3

        vertspeedlimit = 700 if keys[game.settings["DOWN"]] else (400 if self.reducegrav < game.curtime() else 50)
        vertspeed = self._vel.y + grav * delta * (1 if self.nograv < game.curtime() else 0.01)
        if vertspeed > vertspeedlimit-10 and self.indash < game.curtime():
            a = 0.9
            vertspeed = (vertspeed*a + vertspeedlimit*(1-a))
        if self.climbing > game.curtime() and self.jumped < game.curtime() and not self.onGround:
            self._vel = Vector2d(self._vel.x, 140 if keys[game.settings["DOWN"]] else (-70 if keys[game.settings["UP"]] else 0))
        else:
            self._vel = Vector2d(self._vel.x, vertspeed)

        self.onGround = False

        stepcount = 4

        leftwall = False
        rightwall = False

        collided = False

        for i in range(stepcount):

            self._pos += self._vel * delta / stepcount

            checkhull = Vector2d(6, 6)
            roundpos = math.floor(self._pos/16-checkhull/2)
            for ty in range(checkhull.y):
                for tx in range(checkhull.x):

                    left = 1000
                    right = 1000
                    top = 1000
                    bottom = 1000
                    mrgn = 1
                    mrg = 1.2

                    rtx = tx + roundpos.x
                    rty = ty + roundpos.y
                    tilepos = Vector2d(rtx*16, rty*16)
                    tile = level.get_tile(Vector2d(rtx, rty))
                    if tile:
                        type = level.get_tile_info(tile)["type"]
                        if type == "solid":
                            left = self.rpos.x-(tilepos.x+16)
                            right = tilepos.x-(self.rpos.x+self.hull.x)+0.5
                            top = self.rpos.y-(tilepos.y+16)
                            bottom = tilepos.y-(self.rpos.y+self.hull.y)+0.5

                            if not leftwall:
                                leftwall = left < self.hull.x/2*0.2 and left > -self.hull.x / \
                                    2 and ((top < -mrgn and top > -self.hull.y/mrg) or (bottom < -mrgn and bottom > -self.hull.y/mrg))
                            if not rightwall:
                                rightwall = right < self.hull.x/2*0.2 and right > -self.hull.x / \
                                    2 and ((top < -mrgn and top > -self.hull.y/mrg) or (bottom < -mrgn and bottom > -self.hull.y/mrg))

                            arr = [[left, "l"], [right, "r"], [top, "t"], [bottom, "b"]]

                            collide = sorted(arr, reverse=True)[0]
                            clp = collide[0]
                            if clp < 0:
                                if collide[1] == "l" and ((top < -mrgn and top > -self.hull.y/mrg) or (bottom < -mrgn and bottom > -self.hull.y/mrg)):
                                    collided = True
                                    self.rpos += Vector2d(-clp*0.9+self._vel.x/stepcount*delta, 0)
                                    self._vel = Vector2d(0, self._vel.y)
                                if collide[1] == "r" and ((top < -mrgn and top > -self.hull.y/mrg) or (bottom < -mrgn and bottom > -self.hull.y/mrg)):
                                    collided = True
                                    self.rpos += Vector2d(clp*0.9-self._vel.x/stepcount*delta, 0)
                                    self._vel = Vector2d(0, self._vel.y)
                                if collide[1] == "t" and ((left < -mrgn and left > -self.hull.x/mrg) or (right < -mrgn and right > -self.hull.x/mrg)):
                                    collided = True
                                    self.rpos += Vector2d(0, -clp*0.9+self._vel.y/stepcount*delta)
                                    self._vel = Vector2d(self._vel.x, 0)
                                if collide[1] == "b" and ((left < -mrgn and left > -self.hull.x/mrg) or (right < -mrgn and right > -self.hull.x/mrg)):
                                    collided = True
                                    self.rpos += Vector2d(0, clp*0.9-self._vel.y/stepcount*delta)
                                    self._vel = Vector2d(self._vel.x, 0)
                                    self.onGround = True
                        elif type == "platform":
                            if self._vel.y >= -5:

                                left = self.rpos.x-(tilepos.x+16)
                                right = tilepos.x-(self.rpos.x+self.hull.x)+0.5
                                top = self.rpos.y-(tilepos.y+16)
                                bottom = tilepos.y-(self.rpos.y+self.hull.y)+0.5

                                arr = [[left, "l"], [right, "r"], [top, "t"], [bottom, "b"]]

                                collide = sorted(arr, reverse=True)[0]
                                clp = collide[0]
                                if clp < 0 and clp > -5:
                                    if collide[1] == "b" and ((left < -mrgn and left > -self.hull.x/mrg) or (right < -mrgn and right > -self.hull.x/mrg)):
                                        collided = True
                                        self.rpos += Vector2d(0, clp*0.9-self._vel.y/stepcount*delta)
                                        self._vel = Vector2d(self._vel.x, 0)
                                        self.onGround = True

        if self.onGround:
            self.canjump = game.curtime()+0.07
            if self.canrestoredash < game.curtime():
                self.dashes = self.maxdashes

        #  FRICTION
        if self.reduceairfriction < game.curtime() or self.onGround:
            stopspeed = 70
            if abs(self._vel.x) > stopspeed:
                self._vel = Vector2d(self._vel.x*(0.94+(0.03 if self.reducefriction > game.curtime() else 0)), self._vel.y)
            else:
                vl = self._vel.x
                self._vel = Vector2d(math.copysign(max(0, abs(vl)*(0.965+(0.01 if self.reducefriction > game.curtime() else 0)) -
                                                       4+(2.5 if self.reducefriction > game.curtime() else 0)), vl), self._vel.y)

        if self.stopdash > game.curtime() and self.indash < game.curtime():
            self._vel = self._vel*0.90

        jumppower = 450

        if self.queuejump >= game.curtime() and self.canjump > game.curtime() and self.nojump < game.curtime():
            if self.canrestoredash < game.curtime():
                self.dashes = self.maxdashes
            self.queuejump = 0
            self.canjump = 0
            self.jumped = game.curtime()+0.25
            self._vel = Vector2d(math.copysign(abs(self._vel.x)*1.25, self._vel.x), -jumppower)

        holdL = keys[game.settings["LEFT"]]
        holdR = keys[game.settings["RIGHT"]]

        if holdL and not holdR:
            self.lastTurn = -1
        if holdR and not holdL:
            self.lastTurn = 1

        if self.queuejump >= game.curtime() and self.jumped < game.curtime() and self.nojump < game.curtime():
            if keys[game.settings["CLIMB"]] and (leftwall or rightwall):
                self._vel = Vector2d(0, -jumppower*0.85)
                # self.noleft = game.curtime() + 0.05
                # self.noright = game.curtime() + 0.05
                self.jumped = game.curtime() + 0.05
                self.reducefriction = game.curtime() + 0.15
                self.nojump = game.curtime() + 0.15
            else:
                if leftwall:
                    self._vel = Vector2d(480, -jumppower)
                    self.noleft = game.curtime() + 0.4 - (0.18 if not holdL else 0)
                    self.noright = game.curtime() + 0.15 - (0.05 if holdR else 0)
                    self.reducefriction = game.curtime() + 0.1 - (0.09 if not holdL else 0)
                    self.jumped = game.curtime()+0.15
                if rightwall:
                    self._vel = Vector2d(-480, -jumppower)
                    self.noright = game.curtime() + 0.4 - (0.18 if not holdR else 0)
                    self.noleft = game.curtime() + 0.15 - (0.05 if holdL else 0)
                    self.reducefriction = game.curtime() + 0.1 - (0.09 if not holdR else 0)
                    self.jumped = game.curtime()+0.15
        else:
            if (leftwall and holdL) or (rightwall and holdR) and not keys[game.settings["CLIMB"]]:
                self.reducegrav = game.curtime() + 0.05
            if keys[game.settings["CLIMB"]] and (leftwall or rightwall) and self._vel.y > -5:
                self.climbing = game.curtime() + 0.05
                if leftwall:
                    self.noright = game.curtime()+0.05
                if rightwall:
                    self.noleft = game.curtime()+0.05


class Level():
    def __init__(self, levelname):
        self.drct = os.path.join("levels", levelname)

        with open(os.path.join(self.drct, "info.json"), "r") as read_file:
            self.info = json.load(read_file)

        with open(os.path.join(self.drct, "level.json"), "r") as read_file:
            self.level = json.load(read_file)

        self.size = self.w, self.h = self.level["size"]

        self.tiledata = self.level["map"]
        self.name = self.info.get("name", "No name")
        self.tileimg = self.info["tileset"]

    def __get_tile(self, n):
        if n < 0 or n >= len(self.tiledata):
            return None
        return self.tiledata[n]

    def get_tile(self, *args):
        if len(args) > 1:
            return self.__get_tile(args[0]+args[1]*self.w)
        else:
            if isinstance(args[0], Vector2d):
                return self.__get_tile(round(args[0].x+args[0].y*self.w))
            else:
                return self.__get_tile(args[0])

    def get_tile_info(self, tilestr):
        return self.tileimg.get(tilestr)


class Sprite():
    def __init__(self, game, entityName, scale=(16, 16)):
        self.ent_name = entityName
        print("Loading "+self.ent_name+".sprite ...")
        with open(os.path.join("entities", self.ent_name, "data.json"), "r") as read_file:
            self.data = json.load(read_file)
        self.animation_names = self.data["animations"]
        self.animation_infos = {}
        self.animations = {}

        for k, v in self.animation_names.items():
            with open(os.path.join("entities", self.ent_name, v, "anim.json"), "r") as read_file:
                self.animation_infos[k] = json.load(read_file)
                self.animations[k] = {"sequence": [], "speed": self.animation_infos[k]["speed"], "frameCount": len(self.animation_infos[k]["sequence"])}
                for i, image_name in enumerate(self.animation_infos[k]["sequence"]):
                    self.animations[k]["sequence"].append(pygame.transform.scale(
                        pygame.image.load(os.path.join("entities", self.ent_name, v, image_name)), scale))

        print("Done.")

        self.playing = ""
        self.frame = 0
        self.speed = 0
        self.frameCount = 0

        game.sprites[self.ent_name] = self

    def play(self, animation, frame=0):
        if self.animations.get(animation) is not None:
            self.playing = animation
            self.speed = self.animations[animation]["speed"]
            self.frame = frame
            self.frameCount = self.animations[animation]["frameCount"]

    def think(self, delta):
        self.frame = (self.frame + delta/self.speed) % self.frameCount

    @property
    def draw(self):
        if self.playing:
            return self.animations[self.playing]["sequence"][math.floor(self.frame % self.frameCount)]
        else:
            return pygame.Surface((0, 0))


class Game():
    def __init__(self, w=640, h=480):
        self.size = self.w, self.h = w, h
        self._running = True

    def on_init(self):
        pygame.init()
        self._surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._clock = pygame.time.Clock()
        self._running = True
        self._framerate = 0
        self.delta = 0
        self.tilemap = {}

        self.entlist = {}

        self.us = -1

        self.sprites = {}

        self.on_addplayer()

        self.on_loadlevel(level)

    def get_entity(self, id):
        return self.entlist.get(id, None)

    def get_emptyslot(self, plr=False):
        id = 1 if plr else 17
        while self.entlist.get(id) is not None:
            id += 1
        return id

    def get_players(self):
        plys = []
        for i in range(1, 17):
            ply = self.entlist.get(i)
            if ply:
                plys.append(ply)
        return plys

    def on_addplayer(self, control=True):
        empty = self.get_emptyslot(True)
        self.entlist[empty] = Player(self)
        if control:
            self.us = empty
        else:
            pass  # TODO: MP contols

    def on_updateTileImg(self):
        self.tilemap = {}
        for k, v in self.level.tileimg.items():
            self.tilemap[k] = v
            self.tilemap[k]["img"] = pygame.transform.scale(pygame.image.load(os.path.join(self.level.drct, "tileset", v["img"])), (16, 16))

    def on_loadlevel(self, levelname):
        self.level = Level(levelname)
        self.on_updateTileImg()
        self.entlist[0] = self.level
        # start = Vector2d(self.level.info["start"][0], self.level.info["start"][1])
        for ply in self.get_players():
            # ply._pos = start
            ply._pos = Vector2d(50, 300)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if self.us > 0:
                keys = pygame.key.get_pressed()
                me = self.entlist[self.us]
                if event.key == self.settings["JUMP"]:
                    me.queuejump = self.curtime()+0.05

                if event.key == self.settings["DASH"]:
                    if me.dashes > 0:
                        if me.candash < self.curtime() and keys[self.settings["DASH"]]:

                            dashlengthadd = -0.05

                            me.dashes -= 1
                            me.candash = self.curtime() + 0.25 + dashlengthadd
                            me.canrestoredash = self.curtime() + 0.15 + dashlengthadd

                            l, r, u, d = keys[self.settings["LEFT"]], keys[self.settings["RIGHT"]], keys[self.settings["UP"]], keys[self.settings["DOWN"]]
                            l, r, u, d = 1 if l else 0, 1 if r else 0, 1 if u else 0, 1 if d else 0
                            wantdir = Vector2d(r-l, d-u).normalized
                            if wantdir.len < 0.8:
                                wantdir = Vector2d(me.lastTurn, 0)
                            wantdir = wantdir * Vector2d(1, 0.95)
                            wantdir = wantdir.normalized
                            me.nograv = self.curtime() + 0.24 + dashlengthadd
                            me.reduceairfriction = self.curtime() + 0.18 + dashlengthadd
                            me.indash = self.curtime() + 0.15 + dashlengthadd
                            me.stopdash = self.curtime() + 0.18 + dashlengthadd
                            me.reducegrav = self.curtime() + 0.25 + dashlengthadd

                            if wantdir.x > 0.1:
                                me.noleft = self.curtime() + 0.25 + dashlengthadd
                                me.noright = self.curtime() + 0.25 + dashlengthadd
                            if wantdir.x < -0.1:
                                me.noright = self.curtime() + 0.25 + dashlengthadd
                                me.noleft = self.curtime() + 0.25 + dashlengthadd

                            me._vel = wantdir * 700

    def on_halt(self):
        pygame.quit()

    def on_sprite_think(self, delta):
        for k, v in self.sprites.items():
            v.think(delta)

    def on_loop(self):
        self._framerate = self._clock.get_fps()
        delta = self.delta

        self.on_sprite_think(delta)

        if self.us > 0:
            me = self.entlist[self.us]
            keys = pygame.key.get_pressed()
            if keys[self.settings["LEFT"]] or keys[self.settings["RIGHT"]]:
                speed = 2300 * delta
                addvel = (-1 if keys[self.settings["LEFT"]] and me.noleft < game.curtime() else 0) + \
                    (1 if keys[self.settings["RIGHT"]] and me.noright < game.curtime() else 0)
                me._vel = Vector2d(me._vel.x + addvel*speed, me._vel.y)

        for k, v in self.entlist.items():
            if isinstance(v, PhysEntity):
                v.phystick(delta, self.entlist, self.level, self)

    def on_render_level(self):
        w, h = self.level.w, self.level.h

        tiles = self.level.tiledata

        tilesize = Vector2d(16, 16)

        for x in range(w):
            for y in range(h):
                if x+y*w < 0 or x+y*w >= len(tiles):
                    continue
                tile = tiles[x+y*w]
                drawtile = self.tilemap.get(tile)
                if tile is not None and tile != "" and drawtile is not None:
                    pos = tilesize*Vector2d(x, y)
                    self._surf.blit(drawtile["img"], pos.tuple())

    def on_render_players(self):
        for ply in self.get_players():
            if ply.isdorm is False:
                # pygame.draw.rect(self._surf, (200, 100, 120), pygame.Rect(ply.rpos.tuple(), ply.hull.tuple()))
                self._surf.blit(ply.sprite.draw, (round(ply.rpos/2)*2).tuple())

    def on_render(self):
        self._surf.fill((30, 30, 30))

        self.on_render_level()

        self.on_render_players()

        pygame.display.update()

    def curtime(self):
        return time.time()-self._time_bias

    def on_loadsettings(self):
        self.settings = {

            "UP": K_w,
            "DOWN": K_s,
            "LEFT": K_a,
            "RIGHT": K_d,
            "JUMP": K_SPACE,
            "DASH": K_k,
            "CLIMB": K_l

        }

    def on_launch(self):

        self.on_loadsettings()

        self._time_bias = time.time()

        if self.on_init() is False:
            self._running = False

        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.delta = self._clock.get_time()/1000
            self.on_loop()
            self.on_render()
            self._clock.tick(144)
        self.on_halt()


if __name__ == "__main__":
    #я хуй кста
    game = Game()
    game.on_launch()
