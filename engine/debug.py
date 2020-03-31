import pygame as pg

class Debugger(object):
    def __init__(self, app):
        self.app = app
        self.on = False
        self.font = pg.font.SysFont("Roboto", 10, False, True)
        self.stopwatches = {}
        self.results = {}
        self.dt = 0

    def start_stopwatch(self, name):
        self.stopwatches[name] = pg.time.get_ticks()

    def stop_stopwatch(self, name, priority=0):
        self.results[name] = {"time": pg.time.get_ticks() - self.stopwatches[name], "priority": priority}

    def draw(self):
        if not self.on:
            return
        if self.dt>0:
            mul = min((1/self.dt)/144, 1)**0.1
            surf = self.font.render(str(round(1/self.dt*2)/2)+" FPS", True, (255,255*mul,255*mul))
            self.app.surface.blit(surf, (1, 100))
        i = 1
        for k, v in self.results.items():
            if (pg.time.get_ticks() - self.stopwatches[k])>1:
                mul = 1-min(max(v["time"]-7, 0)/20, 1)
                surf = self.font.render(k+": "+str(v["time"])+" ms", True, (255,255*mul,255*mul))
                self.app.surface.blit(surf, (1, 100+i*12))
                i += 1

    def update(self, dt):
        self.results = {k: v for k, v in sorted(self.results.items(), key = lambda t: t[1]["priority"], reverse = True)}

    def event(self, ev):
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_F1:
                self.on = not self.on
