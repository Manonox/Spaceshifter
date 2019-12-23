import pygame as pg
import math

def roundedRect(surf, color, rect, width=0):
    pg.draw.rect(surf, color, rect, width)
    if width>1:
        width /= 2
        width = math.floor(width) - 1
        pg.draw.circle(surf, color, rect.topleft, width)
        pg.draw.circle(surf, color, rect.bottomleft, width)
        pg.draw.circle(surf, color, rect.topright, width)
        pg.draw.circle(surf, color, rect.bottomright, width)
