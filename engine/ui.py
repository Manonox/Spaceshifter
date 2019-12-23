import pygame as pg
from engine.vars import *


class UI(object):

    def __init__(self, app):
        self.app = app
        self.menus = {
            "main": [False, 4],
            "pause": [False, 4]
        }

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

    def button(self, name, i):
        if name == "main":
            if i == 0:
                self.close()
                self.app.maploader.load("test1")
                self.app.leveleditor.editing = False
                self.app.paused = False
            if i == 1:
                self.close()
                self.app.maploader.load("test1", False)
                self.app.leveleditor.editing = True
                self.app.paused = False
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
