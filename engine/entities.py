from utils.utils import pullValues
from utils.vector import vector as vec
from utils.aabb import AABB
from engine.sprites import Sprite
import pygame as pg
from engine.vars import *
import math
from engine.collisions import collision, velocityCollision
from utils.utils import approach, getTile


class EntList(object):

    def __init__(self, app):
        self.app = app
        self.__dict = {}

    def getEmptyId(self):
        i = 1
        while self.__dict.get(str(i), None) is not None:
            i += 1
        return i

    @property
    def all(self):
        return self.__dict.values()

    def getById(self, id=0):
        return self.__dict.get(str(id), None)

    @property
    def world(self):
        return self.getById()

    def insertEnt(self, ent, id=None):
        if id is None:
            id = self.getEmptyId()
        if self.getById(id) is None:
            self.__dict[str(id)] = ent
            ent.register(self, id)
            return id

    def delEnt(self, id):
        if self.getById(id) is not None:
            del self.__dict[str(id)]

    def delAll(self):
        self.__dict.clear()

    def update(self, dt):
        for ent in self.all:
            ent.update(dt)

    def event(self, ev):
        for ent in self.all:
            ent.event(ev)

    def draw(self):
        for ent in self.all:
            ent.draw()


class BaseEntity(object):

    def __init__(self, *args, **kwargs):
        self.id = None
        self.entlist = None
        entlist = kwargs.get('entlist', None)
        if entlist is not None:
            self.register(entlist, entlist.insertEnt(self))

    @property
    def app(self):
        return self.entlist.app

    @property
    def world(self):
        return self.entlist.world

    def register(self, entlist, id):
        self.entlist = entlist
        self.id = id

    def update(self, dt):
        pass

    def event(self, ev):
        pass

    def draw(self):
        pass


class Entity(BaseEntity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pos = pullValues(0, 'pos', args, kwargs, vec(0, 0))
        self.__aabb = pullValues(1, 'aabb', args, kwargs, AABB(vec(0, 0), vec(0, 0)))
        self.__sprite = None
        self.drawShift = vec(0,0)

    def setPos(self, pos):
        self.__pos = vec(pos)
    pos = property(lambda self: vec(self.__pos), setPos)

    def setAABB(self, aabb):
        self.__aabb = AABB(aabb)
    aabb = property(lambda self: AABB(self.__aabb), setAABB)

    @property
    def w_aabb(self):
        return AABB(self.aabb.min+self.pos, self.aabb.max+self.pos)

    def setSprite(self, s):
        self.__sprite = s
    sprite = property(lambda self: self.__sprite, setSprite)

    def update(self, dt):
        super().update(dt)
        self.__sprite.update(dt)

    def draw(self):
        if self.__sprite:
            drawaabb = self.app.camera.getAABB(self.w_aabb)
            zoom = self.app.camera.zoom
            sprsize = vec(self.__sprite.surface.get_size())*zoom*2
            self.app.surface.blit(pg.transform.scale(self.__sprite.surface, sprsize.vr), (drawaabb.center - sprsize + self.drawShift*zoom).vr)


class PhysEntity(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__vel = vec(0, 0)

    def setVel(self, vel):
        self.__vel = vec(vel)
    vel = property(lambda self: vec(self.__vel), setVel)

    def update(self, dt):
        super().update(dt)


class Player(PhysEntity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drawShift = vec(15,15)
        self.aabb = AABB(vec(-15, -30), vec(15, 0))

        self.isControlled = kwargs.get("control", True)

        self.status = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False,
            "collided": False,
            "onGround": False
        }

        self.timers = {}
        self.varJumpSpeed = 0
        self.lastVel = self.vel
        self.lastOnGround = False

        self.inputs = None

    def __getattr__(self, name):
        return self.timers.get(name, 0)>0

    def setTimer(self, name, t):
        self.timers[name] = t

    def getTimer(self, name):
        return self.timers[name]

    def register(self, entlist, id):
        self.sprite = Sprite(entlist.app, "player")
        self.sprite.play("idle")
        super().register(entlist, id)

    def p_updatePos(self, dt):
        self.pos += self.vel*dt

    def p_update(self, dt):
        self.inputs = self.app.inputs.get()

        n = 2
        dt = dt/n

        self.app.debugger.start_stopwatch("Entity physics")

        for i in range(n):

            self.p_gravity2(dt)

            self.p_collisions(dt)

            self.p_accelerate(dt)
            self.p_updatePos(dt)

            self.p_gravity2(dt)

        self.app.debugger.stop_stopwatch("Entity physics")

    @property
    def moveX(self):
        left = self.inputs[ACT_LEFT]
        right = self.inputs[ACT_RIGHT]
        return (1 if right else 0) - (1 if left else 0)

    @property
    def moveY(self):
        up = self.inputs[ACT_UP]
        down = self.inputs[ACT_DOWN]
        return (1 if down else 0) - (1 if up else 0)

    def p_jump(self):
        self.vel = vec(self.vel.x+BLOCKSIDE*0.15*self.moveX, -BLOCKSIDE*40) # 40 , -105
        self.varJumpSpeed = self.vel.y

        self.sprite.sizeMul = vec(0.8,1)

        self.setTimer("jump", 0)
        self.setTimer("jumpGrace", 0)
        self.setTimer("onGround", 0)
        self.setTimer("varJump", 0.25)

    def p_accelerate(self, dt):
        left = self.inputs[ACT_LEFT]
        right = self.inputs[ACT_RIGHT]

        max = BLOCKSIDE*25 # 90
        mult = 1 if self.onGround else 0.65
        runAccel = max*8 # 1000
        runReduce = max*4.5 # 400

        sign = 1 if self.vel.x>0 else -1
        if self.vel.x==0:
            sign = 0

        moveX = self.moveX

        if abs(self.vel.x) > max and sign == moveX:
            self.vel = vec(approach(self.vel.x, max*moveX, runReduce*dt*mult), self.vel.y)
        else:
            self.vel = vec(approach(self.vel.x, max*moveX, runAccel*dt*mult), self.vel.y)
        if self.jump and self.jumpGrace:
            self.p_jump()

    def event(self, ev):
        if ev.type == pg.KEYDOWN:
            k = self.app.settings.get(ev.key)
            if ACT_JUMP in k:
                self.setTimer("jump", 0.1)

    def p_gravity2(self, dt):
        mf = BLOCKSIDE*30
        if self.onGround:
            self.vel = vec(self.vel.x, -0.05)
        else:
            max = mf
            halfGrav = BLOCKSIDE*4.5
            mult = 0.5 if (abs(self.vel.y) < halfGrav and self.inputs[ACT_JUMP]) else 1
            self.vel = vec(self.vel.x, approach(self.vel.y, max, BLOCKSIDE*64 * mult * dt))
            self.p_variableJumping(dt)

    def p_variableJumping(self, dt):
        if self.status["top"]:
            self.setTimer("varJump", 0)
        if self.varJump:
            if not self.inputs[ACT_JUMP]:
                self.vel = vec(self.vel.x, self.vel.y * 0.6)
                self.setTimer("varJump", 0)

    def p_collisions(self, dt):
        json = self.app.maploader.json
        if json is None:
            return

        tilemap = self.app.tilemap

        checkhull = vec(4, 4)

        self.status = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False,
            "collided": False,
        }

        trueVel = self.vel.copy()

        self.vel = vec(0, self.vel.y)

        rooms = json["rooms"]
        for tries in range(2):
            for name, room in rooms.items():
                rw, rh = room["size"]
                margin = vec(1,1)
                if not self.w_aabb.intersect(AABB((vec(room["pos"])-margin)*BLOCKSIDE, (vec(room["pos"])+vec(room["size"])+margin)*BLOCKSIDE)):
                    continue
                tiles = room["tiles"]
                roundedPos = math.floor((self.pos/BLOCKSIDE-vec(room["pos"]))-checkhull/2)
                for ty in range(roundedPos.y, roundedPos.y + checkhull.y):
                    for tx in range(roundedPos.x, roundedPos.x + checkhull.x):
                        tilepos = vec(tx, ty) * BLOCKSIDE
                        tile = getTile(tiles, tx, ty, rw, rh)
                        if tile:
                            type = tilemap.get(tile)
                            if type:
                                type = type["type"]
                                if type and type!="None":

                                    surrounding = {
                                        "l": getTile(tiles, tx-1, ty, rw, rh),
                                        "r": getTile(tiles, tx+1, ty, rw, rh),
                                        "t": getTile(tiles, tx, ty-1, rw, rh),
                                        "b": getTile(tiles, tx, ty+1, rw, rh)
                                    }
                                    for k, v in surrounding.items():
                                        if v is not None:
                                            v = tilemap.get(v)
                                            if v is not None:
                                                surrounding[k] = v["type"]
                                    aabb = self.w_aabb.move(-vec(room["pos"])*BLOCKSIZE)
                                    tileaabb = AABB(tilepos, tilepos+BLOCKSIZE)
                                    r = collision(self.app, type, surrounding, self.vel, aabb, tileaabb, dt)
                                    self.pos += r["move"]
                                    velPrev = self.vel
                                    self.vel = velocityCollision(type, self.vel, r)
                                    for k, v in self.status.items():
                                        if r[k]:
                                            self.status[k] = True
            if tries==0:
                trueVel = vec(trueVel.x, self.vel.y)
                self.vel = vec(trueVel.x, 0)
            else:
                self.vel = vec(self.vel.x, trueVel.y)
        if self.status["bottom"]:
            self.setTimer("onGround", 0.05)
        if self.onGround:
            self.setTimer("jumpGrace", 0.1)
            self.vel = vec(self.vel.x, -1)

    def t_update(self, dt):
        for k, v in self.timers.items():
            self.timers[k] = v - dt

    def a_update(self, dt):
        grnd = self.jumpGrace
        if grnd:
            if abs(self.vel.x)<10:
                self.sprite.play("idle")
            if abs(self.vel.x)>=10:
                self.sprite.play("run")
        else:
            self.sprite.play("air")

        if self.inputs[ACT_LEFT] and not self.inputs[ACT_RIGHT]:
            self.sprite.flip = True
        if self.inputs[ACT_RIGHT] and not self.inputs[ACT_LEFT]:
            self.sprite.flip = False

        if not self.lastOnGround and grnd:
            self.sprite.sizeMul = vec(1.1, 0.9)

        self.lastVel = self.vel
        self.lastOnGround = grnd

    def update(self, dt):
        self.t_update(dt)
        self.p_update(dt)
        super().update(dt)
        self.a_update(dt)

    def draw(self):
        super().draw()
