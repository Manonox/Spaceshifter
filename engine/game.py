import pygame as pg

from engine.entities import EntList, Player
from engine.map import MapLoader, Tilemap
from engine.render import Renderer, Camera
from engine.settings import SettingsManager
from engine.leveleditor import LevelEditor
from engine.keys import Inputs
from engine.ui import UI
from engine.debug import Debugger
#from win32api import GetSystemMetrics


class Game(object):

    def __init__(self, w=1280, h=720, fullscreen=False):

        pg.init()

        self.size = self.w, self.h = w, h
        self.surface = pg.display.set_mode(
            ((1920, 1080) if fullscreen else self.size),
            pg.HWSURFACE | pg.DOUBLEBUF | (pg.FULLSCREEN if fullscreen else 0)
        )
        self.__fullscreen = fullscreen
        self.clock = pg.time.Clock()

        self.paused = True

        self.maploader = MapLoader(self)
        self.inputs = Inputs(self)

        self.settings = SettingsManager()

        self.camera = Camera(self)

        self.tilemap = Tilemap(self)
        self.tilemap.loadTiles()

        self.entlist = EntList(self)

        self.renderer = Renderer(self)
        self.ui = UI(self)

        self.leveleditor = LevelEditor(self)

        self.debugger = Debugger(self)

        self.ui.open("main")

        self.updateReceivers = ["entlist", "leveleditor", "camera", "ui", "debugger"]
        self.eventReceivers = ["entlist", "leveleditor", "ui", "debugger"]
        self.drawReceivers = ["entlist", "renderer", "leveleditor","ui", "debugger"]

    def start(self):
        self._running = True
        while(self._running):
            dt = self.clock.get_time()/1000
            dt = min(dt, 1/30)
            for event in pg.event.get():
                self.on_event(event)
            self.on_update(dt)
            self.on_render()
            self.clock.tick(200)
        self.on_quit()

    def on_event(self, ev):
        results = [self.event(ev)]
        for rc in self.eventReceivers:
            self.debugger.start_stopwatch(rc+" event")
            results.append(getattr(self, rc).event(ev))
            self.debugger.stop_stopwatch(rc+" event")

    def event(self, ev):
        if ev.type == pg.QUIT:
            self._running = False

        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_F11:
                self.fullscreen = not self.fullscreen

    def on_update(self, dt):
        self.debugger.dt = dt
        if self.paused:
            return
        results = [self.update(dt)]
        for rc in self.updateReceivers:
            self.debugger.start_stopwatch(rc+" update")
            results.append(getattr(self, rc).update(dt))
            self.debugger.stop_stopwatch(rc+" update")

    def update(self, dt):
        pass

    def on_render(self):
        self.surface.fill((100, 155, 255))
        results = []
        for rc in self.drawReceivers:
            self.debugger.start_stopwatch(rc+" draw")
            results.append(getattr(self, rc).draw())
            self.debugger.stop_stopwatch(rc+" draw")
        pg.display.update()

    def setFullscreen(self, state):
        if state:
            self.__fullscreen = True
            self.surface = pg.display.set_mode((GetSystemMetrics(0), GetSystemMetrics(1)), pg.HWSURFACE | pg.DOUBLEBUF | pg.FULLSCREEN)
        else:
            self.__fullscreen = False
            self.surface = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
    fullscreen = property(lambda self: self.__fullscreen, setFullscreen)

    def on_quit(self):
        pg.quit()
