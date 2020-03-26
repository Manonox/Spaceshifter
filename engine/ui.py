import pygame as pg
from engine.vars import *
from utils.utils import approach

class Button(object):

    def __init__(self, app, rect):
        self.app = app
        self.rect = rect
        if app:
            self.app.ui.new(self)
        self.held = 0
        self.func = None
        self.hover = 0
        self.font = pg.font.SysFont("Roboto", 14, False, True)
        self.bgcolor = (60, 60, 60)
        self.name = "Oof"
        self.name2 = None
        self.valfunc = None
        self.centered = True
        self.dropdown = False
        self.drawn = 0
        self.addw = 0

    def textSize(self, txt):
        surf = self.font.render(txt, False, (255, 255, 255))
        return surf.get_size()

    def event(self, ev):
        if ev.type == pg.MOUSEBUTTONDOWN:
            if (ev.button in [1,3]) and self.rect.collidepoint(ev.pos):
                self.held = ev.button

        if ev.type == pg.MOUSEBUTTONUP:
            if ev.button in [1,3]:
                if self.rect.collidepoint(ev.pos) and self.held:
                    if self.func:
                        self.func(self.name if self.dropdown else self.app)
                    self.app.leveleditor.buttonPress(self.name2 if self.name2 else self.name, self.held)
                    self.addw = 50
                self.held = 0

    def update(self, dt):
        pos = pg.mouse.get_pos()
        self.drawn = max(self.drawn - dt, 0)
        if self.rect.collidepoint(pos):
            self.addw = approach(self.addw, -10, dt*100)
            self.hover += dt
        else:
            self.addw = approach(self.addw, 0, dt*100)
            self.hover = 0

    def draw(self):
        surface = self.app.surface
        pg.draw.rect(surface, [max(x-10, x+self.addw) for x in self.bgcolor], self.rect)
        if isinstance(self.name, str):
            surf = self.font.render(self.name, True, (255, 255, 255))
        else:
            surf = self.name
        fs = surf.get_size()
        surface.blit(surf, self.rect.move(self.rect.width/2-fs[0]/2 if self.centered else 6, self.rect.height/2-fs[1]/2))
        if self.valfunc:
            r = self.valfunc(self.app)
            if r:
                surf = self.font.render("+", True, (255, 255, 255))
                fs = surf.get_size()
                surface.blit(surf, self.rect.move(self.rect.width-fs[0]/2-6, self.rect.height/2-fs[1]/2))
        self.drawn = 0.1


class UI(object):

    def __init__(self, app):
        self.app = app
        self.menus = {
            "main": [False, 4],
            "pause": [False, 4]
        }

        self.objects = []

        self.current = None
        self.selected = 0

    def __getattr__(self, name):
        return self.menus[name][0]

    def open(self, name):
        self.close()
        self.menus[name][0] = True
        self.current = name

    def close(self):
        self.selected = 0
        self.current = None
        self.menus = {n: [False, self.menus[n][1]] for n in self.menus.keys()}

    def event(self, ev):
        for obj in self.objects:
            obj.event(ev)

        action = self.app.settings
        if ev.type == pg.KEYDOWN:
            add = 0
            if ACT_UP in action.get(ev.key):
                add = -1
            if ACT_DOWN in action.get(ev.key):
                add = 1

            if self.current is not None:
                self.selected = (self.selected+add) % self.menus[self.current][1]

                if ACT_ACCEPT in action.get(ev.key):
                    self.button(self.current, self.selected)

    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)

    def new(self, obj):
        self.objects.append(obj)

    def button(self, name, i):
        if name == "main":
            if i == 0:
                self.close()
                self.app.maploader.load("test1")
                self.app.leveleditor.editing = False
                self.app.paused = False
                self.app.renderer.grid = False
            if i == 1:
                self.close()
                self.app.maploader.load("test1", False)
                self.app.leveleditor.editing = True
                self.app.paused = False
                self.app.renderer.grid = True
            if i == 3:
                pg.event.post(pg.event.Event(pg.QUIT))

    def draw(self):
        surface = self.app.surface
        w, h = surface.get_size()
        if self.main:
            font = pg.font.SysFont("Roboto", 30, False, True)
            wd = 0.7
            padTop = 0.1
            sh = 0.1
            step = 0.12
            for i, n in enumerate(["Play", "Map editor", "Settings", "Quit"]):
                pressed = i == self.selected
                rect = pg.Rect((1-wd)/2*w, (padTop+(step+sh)*i)*h, wd*w, sh*h)
                pg.draw.rect(surface, (70, 70, 70) if pressed else (100, 100, 100), rect)
                surf = font.render(n, True, (255, 255, 255))
                fs = surf.get_size()
                surface.blit(surf, rect.move(rect.width/2-fs[0]/2, rect.height/2-fs[1]/2))
