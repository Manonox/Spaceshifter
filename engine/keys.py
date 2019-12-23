import pygame as pg

class Inputs(object):

    def __init__(self, app):
        self.app = app

    def get(self):
        keys = pg.key.get_pressed()
        mouseb = pg.mouse.get_pressed()
        action = self.app.settings
        return action.getAll(keys, mouseb)
