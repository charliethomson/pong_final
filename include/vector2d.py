
class VectorClassException(Exception):
    pass

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        
    def __repr__(self):
        return f"{self.x}, {self.y}"
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        x, y = (None, None)
        if isinstance(other, tuple):
            if len(other) != 2:
                raise VectorClassException()
            else:
                x, y = other

        if isinstance(other, int):
            x, y = other, other
        
        if isinstance(other, Vector2D):
            x, y = other.x, other.y

        if (x, y) == (None, None):
            raise TypeError("Can only multiply <Vector2D> by tuple (len 2), int, or Vector2D")

        return Vector2D(self.x * x, self.y * y)

    def __div__(self, other):
        x, y = (None, None)
        if isinstance(other, tuple):
            if len(other) != 2:
                raise VectorClassException()
            else:
                x, y = other

        if isinstance(other, int):
            x, y = other, other
        
        if isinstance(other, Vector2D):
            x, y = other.x, other.y

        if (x, y) == (None, None):
            raise TypeError("Can only divide <Vector2D> by tuple (len 2), int, or Vector2D")

        return Vector2D(self.x / x, self.y / y)
