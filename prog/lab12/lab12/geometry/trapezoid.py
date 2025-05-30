class Trapezoid:
    def __init__(self, a, b, height):
        self.a = a
        self.b = b
        self.height = height

    def area(self):
        return ((self.a + self.b) / 2) * self.height

    def circumradius(self):
        # Простое приближение для радиуса описанной окружности
        return (self.a + self.b) / 2

    def inradius(self):
        return self.height / 2
