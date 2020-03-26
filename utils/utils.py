from utils.vector import vector as vec
import math
def listget(l, i, n=None):
    try:
        return l[int(i)]
    except IndexError:
        return n


def pullValues(i, k, args, kwargs, n):
    if listget(args, i) is not None:
        return listget(args, i)
    else:
        return (kwargs.get(str(k), None) or n)

def lerp(x1, x2, a):
    return x1*(1-a) + x2*a

def approach(v1, v2, speed):
    if v1 == v2:
        return v2
    dir = 1 if v2>v1 else -1
    vn = v1+speed*dir
    if vn>v2 and v1<v2:
        return v2
    if vn<v2 and v1>v2:
        return v2
    return vn

def getTile(lst, x, y, w, h):
    if x<0 or y<0 or x>=w or y>=h or (x+y*w)>=len(lst):
        return None
    return lst[x+y*w]

def getTileN(x, y, w, h):
    if x<0 or y<0 or x>=w or y>=h or x+y*w>=w*h or x+y*w<0:
        return None
    return x+y*w

def getTileXY(i, w, h):
    if i<0 or i>=w*h:
        return None
    x = i%w
    y = math.floor(i/w)
    return [x, y]

def transformTiles(tiles, stPos, stSize, enPos, enSize):
    rtiles = [["" for x in range(enSize[0])] for y in range(enSize[1])]
    add = round(vec(stPos)-vec(enPos))
    for i, tile in enumerate(tiles):
        xy = (vec(getTileXY(i, stSize[0], stSize[1])) + add).vr
        if xy[0]<0 or xy[1]<0 or xy[0]>=enSize[0] or xy[1]>=enSize[1]:
            continue
        rtiles[xy[1]][xy[0]] = tile
    res = []
    for y in rtiles:
        res = res + y
    return res
