from utils.vector import vector as vec
from engine.vars import *


def collision(type, surrounding, vel, aabb, tileaabb, dt):

    oaabb = aabb.move(-vel*dt)

    check = {
        "t": True,
        "b": True,
        "l": True,
        "r": True
    }

    for k, v in surrounding.items():
        if v is not None:
            check[k] = False

    response = {
        "top": False,
        "bottom": False,
        "left": False,
        "right": False,
        "collided": False,
        "move": vec(),
        "vel": vel
    }

    resolve = 0.05
    resolve2 = 0.5

    if not aabb.intersect(tileaabb):
        return response

    if type=="solid":
        if (aabb.b >= tileaabb.t and oaabb.b < tileaabb.t + resolve2/2) and check["t"]:
            response["move"] = aabb.setB(tileaabb.t - resolve)
            response["collided"] = True
            response["bottom"] = True
        elif (aabb.t <= tileaabb.b and oaabb.t > tileaabb.b - resolve2/2) and check["b"]:
            response["move"] = aabb.setT(tileaabb.b + resolve)
            response["collided"] = True
            response["top"] = True
        elif (aabb.r >= tileaabb.l and oaabb.r < tileaabb.l + resolve2/2) and check["l"]:
            response["move"] = aabb.setR(tileaabb.l - resolve)
            response["collided"] = True
            response["right"] = True
        elif (aabb.l <= tileaabb.r and oaabb.l > tileaabb.r - resolve2/2) and check["r"]:
            response["move"] = aabb.setL(tileaabb.r + resolve)
            response["collided"] = True
            response["left"] = True

    elif (type=="onlyT" or type=="platform"):
        if (aabb.t <= tileaabb.b and oaabb.t > tileaabb.b - resolve2/2) and check["b"]:
            response["move"] = aabb.setT(tileaabb.b + resolve)
            response["collided"] = True
            response["top"] = True
    elif (type=="onlyB"):
        if (aabb.b >= tileaabb.t and oaabb.b < tileaabb.t + resolve2/2) and check["t"]:
            response["move"] = aabb.setB(tileaabb.t - resolve)
            response["collided"] = True
            response["bottom"] = True
    elif (type=="onlyL"):
        if (aabb.l <= tileaabb.r and oaabb.l > tileaabb.r - resolve2/2) and check["r"]:
            response["move"] = aabb.setL(tileaabb.r + resolve)
            response["collided"] = True
            response["left"] = True
    elif (type=="onlyR"):
        if (aabb.r >= tileaabb.l and oaabb.r < tileaabb.l + resolve2/2) and check["l"]:
            response["move"] = aabb.setR(tileaabb.l - resolve)
            response["collided"] = True
            response["right"] = True

    return response


def velocityCollision(type, vel, r):
    if r["bottom"]:
        vel = vec(vel.x, min(vel.y, 0))
    if r["top"]:
        vel = vec(vel.x, max(vel.y, 0))
    if r["right"]:
        vel = vec(min(vel.x, 0), vel.y)
    if r["left"]:
        vel = vec(max(vel.x, 0), vel.y)
    return vel
