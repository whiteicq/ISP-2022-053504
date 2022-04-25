import math

d = 5


def _t(arg):
    c = 2

    def _f(arg):
        a = 123
        return math.sin(arg * a * c * d)

    return _f(arg)
