import math

def clamp(n, mi, ma):
    return max(min(n, ma), mi)

def easeOutCirc(n):
    n = clamp(n, 0, 1)
    n -= 1
    return math.sqrt(1 - (n * n))
