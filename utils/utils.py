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
