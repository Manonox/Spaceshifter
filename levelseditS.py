import json
import os
import pygame
from pygame.locals import *
import math

from VCT2D.vector import Vector2d

info = {}
level = {"map": [], "size": [40, 30], "ents": []}
for y in range(level["size"][1]):
    for x in range(level["size"][0]):
        level["map"].append("")

opj = os.path.join

while True:
    lname = input("Level name: ")

    folder = opj("levels", lname)

    try:
        with open(opj(folder, "info.json"), "r") as read_file:
            info = json.load(read_file)
    except:
        print("info.json is missing...")
    else:
        break


try:
    with open(opj(folder, "level.json"), "r") as read_file:
        level = json.load(read_file)
except:
    print("Creating new level.json...")
else:
    print("Loaded!")

pygame.init()
size = w, h = 640, 480
surface = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)
running = True

tileset = info["tileset"]

tiles = []
# tiles = [{"name": "", "data": {"type": "", "img": ""}}]

for k, v in tileset.items():
    tileset[k]["img"] = pygame.image.load(opj(folder, "tileset", tileset[k]["img"]))
    tiles.append({"name": k, "data": tileset[k]})

listpos = 0


camerapos = Vector2d(0, 0)

def predraw():
    pygame.draw.rect(surface, (0, 0, 0), ((0, 0), size))

def postdraw():
    pass

def drawworld():
    cubesize = 16
    for y in range(30):
        ry = y - camerapos.tuple()[1]
        for x in range(40):
            rx = x - camerapos.tuple()[0]

            if rx < 0 or rx >= level["size"][0] or ry < 0 or ry >= level["size"][1]:
                pygame.draw.rect(surface, (60, 50, 50), ((x * cubesize, y * cubesize), (cubesize, cubesize)))
                continue

            tilename = level["map"][rx+ry*level["size"][0]]

            if tilename != "":
                surface.blit(pygame.transform.scale(tileset[tilename]["img"], (cubesize, cubesize)), (x * cubesize, y * cubesize))


def drawents():
    pass

def drawtiles():
    cubesize = 32
    center = Vector2d(w*0.5, h-cubesize*2)
    cm = center - Vector2d(cubesize*0.5, cubesize*0.5)
    border = 4

    dw = 0.7
    pygame.draw.rect(surface, (155, 155, 155), ((0, h-cubesize*2-cubesize*(1-dw)), (w, cubesize*dw-2)))
    pygame.draw.rect(surface, (155, 155, 155), ((cm - Vector2d(border, border)).tuple(), (cubesize+border*2, cubesize+border*2)))
    pygame.draw.rect(surface, (50, 50, 50), ((cm - Vector2d(border-1, border-1)).tuple(), (cubesize+border*2-2, cubesize+border*2-2)))

    for i in range(len(tiles)):
        tile = tiles[i]
        img = tile["data"]["img"]
        xi = i - listpos

        drawpos = round(center - Vector2d(cubesize*0.25, cubesize*0.25) + Vector2d(math.copysign(abs(xi)**1.2, xi) * cubesize*1.2, 0)).tuple()
        if i == listpos:
            drawpos = round(cm).tuple()

        if img != "":
            if i == listpos:
                surface.blit(pygame.transform.scale(img, (cubesize, cubesize)), drawpos)
            else:
                surface.blit(pygame.transform.scale(img, (round(cubesize*0.5), round(cubesize*0.5))), drawpos)
        else:
            if i == listpos:
                pygame.draw.rect(surface, (50, 50, 50), (drawpos, (cubesize, cubesize)))
            else:
                pygame.draw.rect(surface, (50, 50, 50), (drawpos, (round(cubesize*0.5), round(cubesize*0.5))))


def setTile(tpos, tname):
    if tpos[0] < 0 or tpos[0] >= level["size"][0]:
        return
    if tpos[1] < 0 or tpos[1] >= level["size"][1]:
        return

    level["map"][tpos[0]+tpos[1]*level["size"][0]] = tname


def insertTile(mpos, pressed):
    tilepos = math.floor(Vector2d(mpos[0], mpos[1]) / 16)
    if pressed[0]:
        setTile((tilepos - camerapos).tuple(), tiles[listpos]["name"])
    if pressed[2]:
        setTile((tilepos - camerapos).tuple(), "")
    return pressed[0] or pressed[2]


def save():
    print("Saving...")
    with open(opj(folder, "level.json"), "w") as write_file:
        json.dump(level, write_file)


startupdate = True
while running:
    update = startupdate
    startupdate = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_COMMA:
                listpos = (listpos - 1) % len(tiles)
            if event.key == K_PERIOD:
                listpos = (listpos + 1) % len(tiles)

            if event.key == K_UP:
                camerapos -= Vector2d(0, -1)
            if event.key == K_DOWN:
                camerapos -= Vector2d(0, 1)
            if event.key == K_LEFT:
                camerapos -= Vector2d(-1, 0)
            if event.key == K_RIGHT:
                camerapos -= Vector2d(1, 0)

            if event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
                save()

            update = True

    if insertTile(pygame.mouse.get_pos(), pygame.mouse.get_pressed()):
        update = True

    if update:
        predraw()
        drawworld()
        drawents()
        drawtiles()
        postdraw()
        pygame.display.update()

save()
