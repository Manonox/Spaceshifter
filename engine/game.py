import pygame as pg

from engine.entities import EntList, Player
from engine.map import MapLoader, Tilemap
from engine.render import Renderer, Camera
from engine.settings import SettingsManager
from engine.leveleditor import LevelEditor
from engine.keys import Inputs
from engine.ui import UI


class Game(object):

    def __init__(self, w=1280, h=720):

        pg.init()

        self.size = self.w, self.h = w, h
        self.surface = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        self.paused = True

        self.maploader = MapLoader(self)
        self.inputs = Inputs(self)

        self.settings = SettingsManager()
        self.leveleditor = LevelEditor(self)

        self.camera = Camera(self)

        self.tilemap = Tilemap()
        self.tilemap.loadTiles()

        self.entlist = EntList(self)

        self.renderer = Renderer(self)
        self.ui = UI(self)
        self.ui.open("main")

        self.updateReceivers = ["entlist", "leveleditor", "camera"]
        self.eventReceivers = ["entlist", "leveleditor", "ui"]
        self.drawReceivers = ["renderer", "entlist", "leveleditor","ui"]

    def start(self):
        self._running = True
        while(self._running):
            dt = self.clock.get_time()/1000
            for event in pg.event.get():
                self.on_event(event)
            self.on_update(dt)
            self.on_render()
            self.clock.tick(200)
        self.on_quit()

    def on_event(self, ev):
        results = [self.event(ev)] + [getattr(self, rc).event(ev) for rc in self.eventReceivers]

    def event(self, ev):
        if ev.type == pg.QUIT:
            self._running = False

    def on_update(self, dt):
        if self.paused:
            return
        results = [self.update(dt)] + [getattr(self, rc).update(dt) for rc in self.updateReceivers]

    def update(self, dt):
        pass

    def on_render(self):
        self.surface.fill((0, 0, 0))
        results = [getattr(self, rc).draw() for rc in self.drawReceivers]
        pg.display.update()

    def on_quit(self):
        pg.quit()
