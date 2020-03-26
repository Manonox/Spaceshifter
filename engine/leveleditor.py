import pygame as pg
from engine.vars import *
from utils.aabb import AABB
from engine.ui import Button
from utils.utils import getTileN, transformTiles
import math
from copy import deepcopy
from copy import copy as shallowcopy
from os import path as pt
import json as jsontools

class LevelEditor(object):

    def __init__(self, app):
        self.app = app
        self.editing = False
        self.movePos = None

        self.roomMove = vec()
        self.roomGrab = None
        self.roomGType = 0

        self.newRoomStart = None

        self.history = []

        self.roomEditing = None
        self.roomNameEdit = None
        self.roomNameNew = ""

        self.textInput = 0
        self.textInputData = ""

        self.inputs = self.app.inputs.get()

        self.toolbar = {
            "type": "hlist",
            "children": {
                "File": {
                    "type": "dropdown",
                    "children": {
                        "New": {
                            "type": "button",
                        },
                        "Open": {
                            "type": "button",
                        },
                        "Save": {
                            "type": "button",
                        }
                    }
                },
                "Edit": {
                    "type": "dropdown",
                    "children": {
                        "Undo": {
                            "type": "button",
                        },
                        "Redo": {
                            "type": "button",
                        },
                        "Properties": {
                            "type": "button"
                        }
                    }
                },
                "View": {
                    "type": "dropdown",
                    "children": {
                        "Grid": {
                            "type": "switch",
                            "valfunc": (lambda app: app.renderer.grid)
                        }
                    }
                },
                "Blocks": {
                    "type": "gridlist",
                    "listfunc": (lambda app: app.tilemap.getAll())
                },
                "Entities": {
                    "type": "list",
                    "listfunc": None
                },
                "Help": {
                    "type": "dropdown",
                    "children": {
                        "Guide": {
                            "type": "button",
                        }
                    }
                }
            }
        }

        self.buttons = {}
        self.states = {}
        self.current = ""
        self.scrollBlocks = 0

        self.generateButtons(self.toolbar)

        self.currentBlock = None

        self.blockProperties = None

    def dropdownPress(self, name):
        if not self.states[name]:
            self.toolbarClose()
        self.states[name] = not self.states[name]

    def save(self):
        json = self.app.maploader.json
        fn = self.app.maploader.filename

        if json and fn != "":
            with open(pt.join("maps", fn+".json"), "w") as f:
                jsontools.dump(json, f)

    def addToHistory(self, action):
        self.history.append([deepcopy(self.app.maploader.json), action])

    def undo(self):
        if len(self.history)==0: return
        data = self.history.pop(-1)
        self.app.maploader.json = data[0]
        return data[1]

    def buttonPress(self, name, mbtn):
        isBlock = False
        if name[:2] == "__":
            name = name[2:]
            isBlock = True

        if self.buttons[name].drawn == 0:
            return

        if isBlock:
            if mbtn==1:
                self.currentBlock = name
            else:
                self.blockProperties = name
            return

        if name == "New":
            self.app.maploader.json = {
                "file": "",
                "name": "",
                "desc": "",
                "rooms": {},
                "spawns": {}
            }
            self.app.maploader.filename = ""

        if name == "Open":
            self.textInput = 2
            self.textInputData = ""

        if name == "Save":
            if self.app.maploader.filename == "":
                self.textInput = 1
            else:
                self.save()

        if name == "Undo":
            self.undo()

        if name == "Grid":
            self.app.renderer.grid = not self.app.renderer.grid

    def toolbarClose(self):
        self.states = {k: False for k, v in self.states.items()}

    @property
    def buttonHovered(self):
        for k, v in self.buttons.items():
            if v.hover > 0 and v.drawn > 0:
                return True
        return False

    def generateButtons(self, data, parent=None, offset=(0, 0)):
        type = data["type"]
        left = offset[0]
        top = offset[1]

        children = data.get("children", None)
        if children:
            for k, v in children.items():
                vtype = v["type"]
                if type == "hlist":
                    btn = Button(self.app, pg.Rect((left, top), (0, 20)))
                    btn.name = k
                    width = btn.textSize(k)[0] + 20
                    btn.rect.width = width
                    btn.func = self.dropdownPress
                    self.buttons[k] = btn
                    self.states[k] = False
                    btn.dropdown = True

                    self.generateButtons(v, parent, (left, top+20))
                    left += width

                if type == "dropdown":
                    btn = Button(self.app, pg.Rect((left, top), (100, 20)))
                    btn.name = k
                    btn.centered = False
                    if vtype == "dropdown":
                        btn.func = self.dropdownPress
                        btn.dropdown = True
                        self.states[k] = False
                    if vtype == "button" or vtype == "switch":
                        if vtype == "switch":
                            btn.valfunc = v["valfunc"]

                    self.buttons[k] = btn

                    self.generateButtons(v, parent, (left+100, top))
                    top += 20

        if type == "gridlist":
            width = 10
            numbr = 0
            bsize = BLOCKSIDE
            size = bsize+4
            fu = data.get("listfunc", None)
            if fu:
                for k, v in fu(self.app).items():
                    btn = Button(self.app, pg.Rect((left+numbr*size, top+size*(numbr//width)), (size, size)))
                    btn.name = pg.transform.scale(v["img"], (bsize, bsize))
                    btn.name2 = "__"+k
                    self.buttons[k] = btn
                    numbr += 1

    def update(self, dt):
        json = self.app.maploader.json
        camera = self.app.camera
        if not self.editing:
            return
        if self.roomNameEdit is not None:
            return
        if self.textInput!=0:
            return
        if self.blockProperties is not None:
            return

        self.inputs = inputs = self.app.inputs.get()
        speed = BLOCKSIDE*20
        mX = (1 if inputs[ACT_RIGHT] else 0) - (1 if inputs[ACT_LEFT] else 0)
        mY = (1 if inputs[ACT_DOWN] else 0) - (1 if inputs[ACT_UP] else 0)
        camera.pos += vec(mX, mY) * dt * speed / camera.zoom

        if self.movePos is None:
            self.movePos = vec(pg.mouse.get_pos())

        mMove = (vec(pg.mouse.get_pos()) - self.movePos)/camera.zoom

        if inputs[ACT_MOUSE3]:
            self.app.camera.pos -= mMove

        if inputs[ACT_MOUSE1] and not self.buttonHovered:
            if self.roomGrab:
                self.roomMove += (vec() if inputs[ACT_MOUSE3] else mMove) + vec(mX, mY) * dt * speed / camera.zoom
            elif self.currentBlock:
                rooms = json["rooms"]
                mpos = math.floor(camera.getWorld(vec(pg.mouse.get_pos()))/BLOCKSIDE)
                for name, room in rooms.items():
                    rpos = vec(room["pos"])
                    rtile = mpos-rpos
                    tile = getTileN(rtile.x, rtile.y, room["size"][0], room["size"][1])
                    if tile is not None:
                        room["tiles"][tile] = self.currentBlock

        if inputs[ACT_MOUSE2] and not self.buttonHovered and not inputs[ACT_MOUSE1]:
            rooms = json["rooms"]
            mpos = math.floor(camera.getWorld(vec(pg.mouse.get_pos()))/BLOCKSIDE)
            for name, room in rooms.items():
                rpos = vec(room["pos"])
                rtile = mpos-rpos
                tile = getTileN(rtile.x, rtile.y, room["size"][0], room["size"][1])
                if tile is not None:
                    room["tiles"][tile] = ""

        self.movePos = vec(pg.mouse.get_pos())

    def zoom(self, d):
        camera = self.app.camera
        if d == 1:
            pre = camera.getWorld(vec(pg.mouse.get_pos()))
            camera.zoom = min(camera.zoom*2, 4)
            post = camera.getWorld(vec(pg.mouse.get_pos()))
            camera.pos += (pre-post)
        else:
            pre = camera.getWorld(vec(pg.mouse.get_pos()))
            camera.zoom = max(camera.zoom/2, 0.25)
            post = camera.getWorld(vec(pg.mouse.get_pos()))
            camera.pos += (pre-post)

    def event(self, ev):
        if not self.editing:
            return
        json = self.app.maploader.json
        camera = self.app.camera

        if ev.type == pg.KEYDOWN:
            if ev.key in [pg.K_PLUS, pg.K_KP_PLUS, pg.K_EQUALS]:
                self.zoom(1)
                return
            elif ev.key in [pg.K_MINUS, pg.K_KP_MINUS]:
                self.zoom(-1)
                return

            kn = (pg.key.name(ev.key)).lower()
            mapping = {
                "space": "_"
            }
            kn = mapping.get(kn, kn)

            if (self.textInput!=0):
                if kn == "backspace" and len(self.textInputData)>0:
                    self.textInputData = self.textInputData[:-1]
                    return
                if kn == "return":
                    if self.textInput == 1:
                        self.app.maploader.filename = self.textInputData
                    if self.textInput == 2:
                        self.app.maploader.load(self.textInputData)

                    self.textInput = 0
                    self.textInputData = ""
                    return
                if len(kn)!=1: return
                self.textInputData = self.textInputData + kn

            if (self.roomNameEdit is not None):

                if kn == "backspace" and len(self.roomNameNew)>0:
                    self.roomNameNew = self.roomNameNew[:-1]
                    return
                if kn == "return":
                    self.addToHistory("Room renamed")
                    room = deepcopy(json["rooms"][self.roomNameEdit])
                    del(json["rooms"][self.roomNameEdit])
                    json["rooms"][self.roomNameNew] = room
                    self.roomNameEdit = None
                    self.roomNameNew = ""
                    return
                if len(kn)!=1: return
                self.roomNameNew = self.roomNameNew + kn

        if ev.type == pg.MOUSEBUTTONDOWN:

            if ev.button == 4:
                self.zoom(1)
                return
            if ev.button == 5:
                self.zoom(-1)
                return

            if json is None:
                return

            if self.blockProperties is not None:

                return

            if self.roomNameEdit is not None:
                self.addToHistory("Room renamed")
                room = deepcopy(json["rooms"][self.roomNameEdit])
                del(json["rooms"][self.roomNameEdit])
                json["rooms"][self.roomNameNew] = room
                self.roomNameEdit = None
                self.roomNameNew = ""
                return

            if self.textInput!=0:
                return

            if self.roomEditing is not None:
                if (ev.button == 1):
                    room = json["rooms"][self.roomEditing]
                    rpos = vec(room["pos"])*BLOCKSIDE
                    rsize = vec(room["size"])*BLOCKSIDE
                    raabb = camera.getAABB(AABB(rpos, rpos+rsize))
                    raabbRename = raabb.copy()
                    raabbDelete = raabb.copy()
                    raabbRename.max.y = raabb.center.y
                    raabbDelete.min.y = raabb.center.y
                    if raabbRename.inside(vec(ev.pos)):
                        self.roomNameEdit = self.roomEditing
                        self.roomNameNew = ""
                    if raabbDelete.inside(vec(ev.pos)):
                        self.addToHistory("Room deleted")
                        del(json["rooms"][self.roomEditing])

                self.roomEditing = None
                return

            if self.inputs[ACT_EDITOR_GRAB] and (ev.button == 1):
                pos = vec(ev.pos)

                rooms = json["rooms"]
                self.roomGrab = None
                for name, room in rooms.items():
                    rpos = vec(room["pos"])*BLOCKSIDE
                    rsize = vec(room["size"])*BLOCKSIDE
                    raabb = camera.getAABB(AABB(rpos, rpos+rsize))
                    if raabb.inside(pos):
                        self.roomGrab = name
                        self.roomMove = vec()
                        self.roomGType = 0
                        marg = 7
                        if pos.x < raabb.min.x+marg:
                            self.roomGType = self.roomGType | 1
                        if pos.x > raabb.max.x-marg:
                            self.roomGType = self.roomGType | 2
                        if pos.y < raabb.min.y+marg:
                            self.roomGType = self.roomGType | 4
                        if pos.y > raabb.max.y-marg:
                            self.roomGType = self.roomGType | 8
                        break

                if self.roomGrab is None:
                    self.newRoomStart = math.floor(camera.getWorld(vec(pg.mouse.get_pos()))/BLOCKSIDE)

                return

            inputs = self.app.inputs.get()
            if ev.button == 1 and not self.buttonHovered:
                self.addToHistory("Tile draw")
            if ev.button == 3 and not self.buttonHovered and not inputs[ACT_MOUSE1]:
                self.addToHistory("Tile erase")

        if ev.type == pg.MOUSEBUTTONUP:
            if ev.button == 1:
                if self.roomGrab:
                    room = json["rooms"][self.roomGrab]
                    val = round(self.roomMove/BLOCKSIDE)
                    if val[0]==0 and val[1]==0:
                        return
                    self.addToHistory("Room resized")
                    if self.roomGType == 0:
                        room["pos"] = [round(room["pos"][0] + val[0]), round(room["pos"][1] + val[1])]
                    else:
                        rpos = vec(room["pos"])
                        oldpos = vec(room["pos"])
                        rsize = vec(room["size"])
                        if self.roomGType & 1:
                            rsize += vec(-val.x, 0)
                            rpos += vec(val.x, 0)
                        if self.roomGType & 2:
                            rsize += vec(val.x, 0)
                        if self.roomGType & 4:
                            rsize += vec(0, -val.y)
                            rpos += vec(0, val.y)
                        if self.roomGType & 8:
                            rsize += vec(0, val.y)

                        room["tiles"] = transformTiles(room["tiles"], room["pos"], room["size"], rpos.vr, rsize.vr)
                        room["pos"] = rpos.vr
                        room["size"] = rsize.vr


                    self.roomGrab = None
                    self.roomMove = vec()

                if self.newRoomStart is not None:
                    self.addToHistory("Room created")
                    newRoomEnd = math.floor(camera.getWorld(vec(pg.mouse.get_pos()))/BLOCKSIDE)
                    newRoom = AABB(self.newRoomStart, newRoomEnd)
                    newRoom.normalize()
                    smth = newRoomEnd - self.newRoomStart

                    if smth.x != 0:
                        newRoom.w = newRoom.w+1
                    if smth.y != 0:
                        newRoom.h = newRoom.h+1

                    if newRoom.w > 1 and newRoom.h > 1:
                        newName = 0
                        while json["rooms"].get(str(newName), None) is not None:
                            newName += 1
                        json["rooms"][str(newName)] = {
                            "pos": newRoom.min.vr,
                            "size": newRoom.size.vr,
                            "tiles": ["" for i in range(newRoom.size.x*newRoom.size.y)],
                            "ents": []
                        }
                    self.newRoomStart = None

            if ev.button == 3:
                self.roomEditing = None and self.roomGrab is None
                if self.inputs[ACT_EDITOR_GRAB]:

                    propertiesRoom = None

                    pos = vec(ev.pos)

                    if json is None:
                        return
                    rooms = json["rooms"]
                    self.roomGrab = None
                    for name, room in rooms.items():
                        if propertiesRoom is None:
                            rpos = vec(room["pos"])*BLOCKSIDE
                            rsize = vec(room["size"])*BLOCKSIDE
                            raabb = camera.getAABB(AABB(rpos, rpos+rsize))
                            if raabb.inside(pos):
                                propertiesRoom = name

                    if propertiesRoom is not None:
                        self.roomEditing = propertiesRoom

    def drawUI(self, data, name=None):
        surface = self.app.surface
        w, h = surface.get_size()
        if name:
            btn = self.buttons.get(name, None)
            if btn:
                btn.draw()
            open = self.states.get(name, False)
        else:
            pg.draw.rect(surface, (60, 60, 60), pg.Rect((0, 0), (w, 20)))
            open = True

        if open:
            children = data.get("children", {})
            for k, v in children.items():
                self.drawUI(v, k)

            fu = data.get("listfunc", None)
            if fu:
                for k, v in fu(self.app).items():
                    self.drawUI(v, k)

    def draw(self):
        if not self.editing:
            return
        surface = self.app.surface
        w, h = surface.get_size()
        json = self.app.maploader.json
        if json is None:
            return
        camera = self.app.camera
        font = pg.font.SysFont("Roboto", 14, True, False)

        rooms = json["rooms"]
        for name, room in rooms.items():
            rpos = vec(room["pos"])
            rsize = vec(room["size"])
            if name == self.roomGrab:
                val = round(self.roomMove/BLOCKSIDE)
                if self.roomGType == 0:
                    rpos += val
                else:
                    if self.roomGType & 1:
                        rsize += vec(-val.x, 0)
                        rpos += vec(val.x, 0)
                    if self.roomGType & 2:
                        rsize += vec(val.x, 0)
                    if self.roomGType & 4:
                        rsize += vec(0, -val.y)
                        rpos += vec(0, val.y)
                    if self.roomGType & 8:
                        rsize += vec(0, val.y)

            rpos *= BLOCKSIDE
            rsize *= BLOCKSIDE
            raabb = camera.getAABB(AABB(rpos, rpos+rsize))

            if name != self.roomEditing:
                clr = (255, 100, 100)
                if self.roomNameEdit == name:
                    clr = (205, 150, 60)
                    name = self.roomNameNew
                pg.draw.rect(surface, (255,100,100), raabb.rect, 2)
                surf = font.render(name, True, clr)
                surface.blit(surf, (raabb.min+vec(2, 0)).vr)

            raabbRename = raabb.copy()
            raabbDelete = raabb.copy()
            raabbRename.max.y = raabb.center.y
            raabbDelete.min.y = raabb.center.y

            if name == self.roomEditing:
                pg.draw.rect(surface, (100,100,100), raabbRename.rect)
                surf = font.render("Rename", True, (255, 255, 255))
                surface.blit(surf, (raabbRename.center-vec(surf.get_size())/2).vr)

                pg.draw.rect(surface, (150,50,50), raabbDelete.rect)
                surf = font.render("Delete", True, (255, 255, 255))
                surface.blit(surf, (raabbDelete.center-vec(surf.get_size())/2).vr)

        if self.newRoomStart is not None:
            newRoomEnd = math.floor(camera.getWorld(vec(pg.mouse.get_pos()))/BLOCKSIDE)
            newRoom = AABB(self.newRoomStart, newRoomEnd)
            newRoom.normalize()
            smth = newRoomEnd - self.newRoomStart

            if smth.x != 0:
                newRoom.w = newRoom.w+1
            if smth.y != 0:
                newRoom.h = newRoom.h+1

            if newRoom.size.x > 1 and newRoom.size.y > 1:
                newRoom = camera.getAABB(newRoom*BLOCKSIDE)
                pg.draw.rect(surface, (200, 70, 70), newRoom.rect, 2)

        if camera.zoom != 1:
            font = pg.font.SysFont("Roboto", 22, True, False)
            zoomNum = str(round(camera.zoom, 2))
            if not "." in zoomNum:
                zoomNum += ".0"
            surf = font.render("x"+zoomNum, True, (100, 100, 100))
            surf2 = pg.Surface(surf.get_size())
            surf2.blit(surf, (0, 0), special_flags=0)
            surf2 = surf2.convert_alpha()
            surface.blit(surf2, (5, h-surf.get_size()[1]), special_flags=pg.BLEND_RGBA_ADD)

        block = self.app.tilemap.get(self.currentBlock)
        if block:
            surface.blit(pg.transform.scale(block["img"], (BLOCKSIDE, BLOCKSIDE)), (vec(pg.mouse.get_pos())+vec(15, 15)).vr)

        if self.textInput!=0:
            surfsize = surface.get_size()
            pg.draw.rect(surface, (150,150,150), pg.Rect(0,surfsize[1]*0.45,surfsize[0],surfsize[1]*0.1))
            surf = font.render(self.textInputData, True, (255, 255, 255))
            surface.blit(surf, (vec(surfsize)/2-vec(surf.get_size())/2).vr)

        self.drawUI(self.toolbar)
