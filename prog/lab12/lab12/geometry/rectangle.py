class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def circumradius(self):
        return ((self.width**2 + self.height**2)**0.5) / 2

    def inradius(self):
        return min(self.width, self.height) / 2
