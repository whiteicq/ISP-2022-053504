class Test1:
    def __init__(self, a):
        self.a = a

    def print_hello(self):
        return "Hello"


class Test(Test1):
    def __init__(self, a, b):
        super().__init__(a)
        self.b = b


def fact(n):
    if n == 1:
        return 1
    return n * fact(n - 1)
