import math

class Triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def area(self):
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def circumradius(self):
        return (self.a * self.b * self.c) / (4 * self.area())

    def inradius(self):
        return self.area() / ((self.a + self.b + self.c) / 2)
